import json
import subprocess
from pathlib import Path

import click
import toml
from flask import Flask
from loguru import logger

from . import __version__
from .package import Package
from .server import Server


def register(app: Flask):  # noqa: C901
    @app.cli.command("freeze")
    @click.option(
        "--dev/--not-dev",
        "-d/ ",
        default=False,
        help="Freeze development requirements.",
    )
    @click.option(
        "--hashes/--no-hashes",
        default=True,
        help="Create lock file without file hashes.",
    )
    def freeze_reqs(dev: bool, hashes: bool):
        """Create a requirements.txt file."""
        package: Package = Package.find_root()
        package.freeze(dev, not hashes)

    @app.cli.command()
    def sync_versions():
        """Make sure that versions are synced between various files.

        The pyproject.toml version is treated as canonical.
        """
        package: Package = Package.find_root()
        proj = package.root_dir / "pyproject.toml"
        pkg = package.root_dir / "package.json"

        proj_data = toml.loads(proj.read_text())

        poetry = proj_data["tool"]["poetry"]
        version = poetry["version"]

        logger.info(f"Current version: {version}")
        version_mod = __version__.__name__
        if __version__.__version__ != version:
            logger.info(f"{version_mod} out of date.")
            ver_file = Path(__version__.__file__)
            ver_file.write_text(f'__version__ = "{version}"\n')
        else:
            logger.info(f"{version_mod} up to date.")

        if pkg.is_file():
            pkg_data = json.loads(pkg.read_text())
            if pkg_data["version"] != version:
                logger.info("package.json out of date.")
                pkg_data["version"] = version
                pkg.write_text(json.dumps(pkg_data))
                args = [
                    "yarn",
                    "--silent",
                    "run",
                    "prettier",
                    "--loglevel",
                    "error",
                    "--write",
                    str(pkg),
                ]
                subprocess.run(args)
            else:
                logger.info("package.json up to date.")
        else:
            logger.warning("No package.json found.")

    @app.cli.command()
    @click.option("--run/--no-run", default=True)
    @click.option("--yarn/--no-yarn", default=True)
    def serve(run: bool, yarn: bool):
        """Run dev server and build client bundles."""
        server = Server(start_run=run, start_yarn=yarn)
        server.start()
        server.loop()
