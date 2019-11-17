import multiprocessing as mp
import os
import signal
import sys
import time

import click
from environs import Env

env = Env()
env.read_env()

MAX_WAIT = 15.0


def _run(application, host, port):
    import bjoern

    bjoern.run(application, host, port)


def wait(proc):
    if proc.exitcode is not None:
        return True
    start = time.perf_counter()
    while True:
        elapsed = time.perf_counter() - start
        if not proc.is_alive():
            return True
        if elapsed > MAX_WAIT:
            return not proc.is_alive()


def kill_proc(proc):
    if proc.exitcode is not None:
        return
    proc.terminate()
    done = wait(proc)
    if done:
        return
    proc.kill()
    wait(proc)


def run(application):
    port = env.int("PORT", default=80)
    host = env("HOST", default="0.0.0.0")

    click.secho(f"Running on ", fg="green", nl=False)
    click.secho(f"{host}:{port}", bold=True, fg="white")
    click.secho(f"PID: ", nl=False)
    click.secho(str(os.getpid()), bold=True)

    proc = mp.Process(target=_run, args=(application, host, port))
    proc.start()

    def kill(*args, **kwargs):
        click.secho("Closing", fg="red", bold=True)
        kill_proc(proc)
        sys.exit(0)

    signal.signal(signal.SIGTERM, kill)
    signal.signal(signal.SIGHUP, kill)

    click.echo("Subprocess PID: ", nl=False)
    click.secho(str(proc.pid), bold=True)

    while True:
        try:
            if not proc.is_alive():
                break
        except (Exception, KeyboardInterrupt):
            break
    kill()
