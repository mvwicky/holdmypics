import hashlib
import itertools as it
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import attr
import click
import psutil as ps

CWD = Path.cwd()
DIST = CWD / "dist"
SRC = CWD / "src"


def hash_file(file: Path) -> str:
    return hashlib.md5(file.read_bytes()).hexdigest()


def start_proc(args: Sequence[str], delay: float = 0, **kwargs):
    kwargs.update({"cwd": str(CWD)})
    proc = ps.Popen(args, **kwargs)
    time.sleep(delay)
    return proc


@attr.s(slots=True, auto_attribs=True)
class Manager(object):
    procs: Dict[str, ps.Popen] = attr.ib(factory=dict)
    built_files: List[Path] = attr.ib(factory=list)
    src_files: Dict[Path, str] = attr.ib(factory=dict)
    should_end: bool = False

    def kill_all(self, proc_dict: Optional[Dict[str, ps.Popen]] = None):
        if proc_dict is None:
            proc_dict = self.procs
        names = tuple(proc_dict)
        click.echo(f"Killing processes: {names}")
        procs: List[ps.Popen] = list(proc_dict.values())
        for p in procs:
            if p.is_running():
                p.terminate()
        _, alive = ps.wait_procs(procs, timeout=10)
        if alive:
            click.echo("At least one process didn't terminate.")
        for p in alive:
            p.kill()

    def kill_others(self, key: str):
        tokill = {k: p for k, p in self.procs.items() if k != key}
        self.kill_all(tokill)

    def start_procs(self):
        self.procs.update({"flask": start_proc(["flask", "run"])})

    def check_src(self) -> bool:
        globs = ["*.html", "*.ts", "*.scss"]
        files = it.chain.from_iterable([SRC.glob(g) for g in globs])
        changed: List[Path] = []
        for file in filter(Path.is_file, files):
            file_hash = hash_file(file)
            current = self.src_files.get(file)
            if current != file_hash:
                changed.append(file)
                self.src_files[file] = file_hash

        n_changed = len(changed)
        if n_changed == 1:
            click.echo("1 file changed")
        elif n_changed > 1:
            click.echo(f"{n_changed} files changed")
        return n_changed != 0

    def on_src_change(self):

        proc = start_proc(["make", "dev"], stdout=subprocess.DEVNULL)
        create_time = proc.create_time()
        self.procs["src_change"] = proc
        proc.wait()
        elapsed = time.time() - create_time
        click.echo(f"Done rebuilding after {elapsed:.2f}s.")
        self.procs.pop("src_change", None)

    def start(self):
        self.start_procs()
        try:
            self.main_loop()
        finally:
            self.kill_all()

    def main_loop(self):
        while not self.should_end:
            self.should_end = False
            for name, proc in self.procs.items():
                if not proc.is_running():
                    self.kill_others(name)
                    self.should_end = True
                    break
            time.sleep(1)
            if self.check_src():
                self.on_src_change()


@click.command()
def main():
    Manager().start()
    # manager.start()
