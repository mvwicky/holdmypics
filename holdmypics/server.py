import os
import subprocess
import time
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Dict, Sequence

import attr
from flask import Blueprint, Flask
from loguru import logger

WAIT = 30


@attr.s(slots=True, auto_attribs=True)
class Server(object):
    app: Flask
    start_run: bool = True
    start_yarn: bool = True

    procs: Dict[str, subprocess.Popen] = attr.ib(init=False, factory=dict)

    def start(self):
        if self.start_yarn:
            self._start_yarn()
        if self.start_run:
            args = [
                "gunicorn",
                "wsgi:application",
                "--config",
                "python:gunicorn_config",
            ]
            self._start_proc("dev_server", args)
        n = len(self.procs)
        ts = "" if n == 1 else "es"
        logger.info("Started {0} process{1}", n, ts)

    def _start_proc(self, name: str, args: Sequence[str], **kwargs):
        logger.info("Starting process `{0}`", " ".join(args))
        self.procs[name] = subprocess.Popen(args, **kwargs)

    def _start_yarn(self):
        bp: Blueprint = self.app.blueprints.get("core")
        template_folder = Path(bp.root_path) / bp.template_folder
        base_out = template_folder / "base-out.html"
        start_mtime = 0
        if base_out.is_file():
            start_mtime = os.path.getmtime(base_out)
            logger.debug("Waiting for changes (mtime={0}).", start_mtime)
        self._start_proc("yarn", ["yarn", "watch"])
        self._wait_for_yarn(base_out, start_mtime)

    def _wait_for_yarn(self, base_tpl: Path, start_mtime: float):
        start = time.perf_counter()
        while True:
            if base_tpl.is_file():
                if os.path.getmtime(base_tpl) != start_mtime:
                    logger.debug("File changed.")
                    break
                time.sleep(0.1)
            if time.perf_counter() - start > WAIT:
                logger.warning("Waited too long.")
                break
        logger.info("Done waiting for yarn.")

    def loop(self):
        while True:
            try:
                should_shutdown = self._inner_loop()
                if should_shutdown:
                    break
                time.sleep(0.1)
            except (KeyboardInterrupt, Exception):
                break
        self.shutdown()

    def _inner_loop(self):
        for name, proc in self.procs.items():
            if proc.poll() is not None:
                logger.warning("Subprocess {0} died", name)
                return True
        return False

    def shutdown(self):
        logger.info("Shutting down.")
        for name, proc in self.procs.items():
            logger.info("Terminating {0}", name)
            proc.terminate()
            try:
                proc.wait(WAIT)
            except TimeoutExpired:
                logger.warning("Killing {0}", name)
                proc.kill()
                try:
                    proc.wait(WAIT)
                except TimeoutExpired:
                    logger.error("Unable to kill {0}", name)
