import subprocess
import time
from subprocess import TimeoutExpired
from typing import Dict

import attr
from loguru import logger

WAIT = 5


@attr.s(slots=True, auto_attribs=True)
class Server(object):
    start_run: bool = True
    start_yarn: bool = True

    procs: Dict[str, subprocess.Popen] = attr.ib(init=False, factory=dict)

    def start(self):
        if self.start_yarn:
            self.procs["yarn"] = subprocess.Popen(["yarn", "watch"])
            time.sleep(5)
        if self.start_run:
            self.procs["run"] = subprocess.Popen(["flask", "run"])

    def loop(self):
        while True:
            should_shutdown = False
            for name, proc in self.procs.items():
                if proc.poll() is not None:
                    logger.warning(f"Subprocess {name} died")
                    should_shutdown = True
                    break
            if should_shutdown:
                break
            try:
                time.sleep(0.1)
            except (KeyboardInterrupt, Exception):
                break
        self.shutdown()

    def shutdown(self):
        logger.info("Shutting down.")
        for name, proc in self.procs.items():
            logger.info(f"Terminating {name}")
            proc.terminate()
            try:
                proc.wait(WAIT)
            except TimeoutExpired:
                logger.warning(f"Killing {name}")
                proc.kill()
                try:
                    proc.wait(WAIT)
                except TimeoutExpired:
                    logger.error(f"Unable to kill {name}")
