from __future__ import annotations

import os
import re
import time
from collections.abc import Sequence
from pathlib import Path
from subprocess import Popen, TimeoutExpired
from typing import Any

import attr
from flask import Flask
from loguru import logger

from .utils import config_value

WEB_PROC_RE = re.compile(r"^web: (?P<cmd>.+)$")


@attr.s(slots=True, auto_attribs=True)
class Server(object):
    app: Flask
    wait: float
    start_server: bool = True
    start_yarn: bool = True

    procs: dict[str, Popen] = attr.ib(init=False, factory=dict)

    def start(self) -> None:
        if self.start_yarn:
            self._start_yarn()
        if self.start_server:
            self._start_server()
        n = len(self.procs)
        logger.info("Started {0} process{1}", n, "" if n == 1 else "es")

    def _start_proc(self, name: str, args: Sequence[str], **kwargs: Any) -> Popen:
        logger.info("Running `{0}`", " ".join(args))
        return self.procs.setdefault(name, Popen(args, **kwargs))

    def _start_server(self) -> None:
        procfile = config_value("BASE_PATH", app=self.app, cast_as=Path) / "Procfile"
        if not procfile.is_file():
            raise RuntimeError("Unable to find Procfile")
        lines = procfile.read_text().splitlines()
        cmd = None
        for line in lines:
            match = WEB_PROC_RE.match(line.strip())
            if match:
                cmd = match.group("cmd").split(" ")
        if cmd is None:
            raise RuntimeError("Unable to parse command from Procfile")
        self._start_proc("dev_server", cmd)

    def _start_yarn(self) -> None:
        bp = self.app.blueprints.get("web")
        assert bp is not None
        assert bp.template_folder is not None
        out = Path(bp.root_path) / bp.template_folder / "base-out.html"
        start_mtime = 0
        if out.is_file():
            out.unlink()
        env = {**os.environ, "NODE_ENV": "development", "TAILWIND_MODE": "build"}
        proc = self._start_proc("yarn", ["yarn", "watch"], env=env)
        self._wait_for_yarn(out, start_mtime, proc)

    def _wait_for_yarn(self, base_tpl: Path, start_mtime: float, proc: Popen) -> None:
        start = time.perf_counter()
        while True:
            if base_tpl.is_file():
                if os.path.getmtime(base_tpl) != start_mtime:
                    logger.debug("File changed.")
                    break
                time.sleep(0.1)
            if time.perf_counter() - start > self.wait:
                logger.warning("Waited too long.")
                break
        logger.info("Done waiting for yarn.")

    def loop(self) -> None:
        while True:
            try:
                should_shutdown = self._check_procs()
                if should_shutdown:
                    break
                time.sleep(0.1)
            except (KeyboardInterrupt, Exception):
                break
        self.shutdown()

    def _check_procs(self) -> bool:
        for name, proc in self.procs.items():
            if proc.poll() is not None:
                logger.warning("Subprocess {0} died", name)
                return True
        return False

    def shutdown(self) -> None:
        logger.info("Shutting down.")
        for name, proc in self.procs.items():
            logger.info("Terminating {0}", name)
            proc.terminate()
            try:
                proc.wait(self.wait)
            except TimeoutExpired:
                logger.warning("Killing {0}", name)
                proc.kill()
                try:
                    proc.wait(self.wait)
                except TimeoutExpired:
                    logger.error("Unable to kill {0}", name)
