from __future__ import annotations

import json
import shlex
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import click
import semver
from flask import Flask
from loguru import logger
from semver import VersionInfo

SEMVER_LEVELS = ("major", "minor", "patch", "prerelease", "build")
SEMVER_BUMPS: dict[str, Callable[[VersionInfo], Any]] = {
    level: getattr(VersionInfo, f"bump_{level}") for level in SEMVER_LEVELS
}


def run(*args: str, **kwargs: Any) -> subprocess.CompletedProcess:
    if not kwargs.pop("no_echo", False):
        click.echo(shlex.join(args))
    kwargs.setdefault("check", True)
    return subprocess.run(args, **kwargs)


def register(app: Flask):  # noqa: C901
    base_path = app.config.get("BASE_PATH")
    cfg_path = base_path / "config"
    dev_dir = str(cfg_path / "dev")
    prod_dir = str(cfg_path / "prod")
    default_template = str(cfg_path / "Dockerfile.template")

    @app.cli.command()
    @click.option(
        "--both/--not-both",
        "-b/ ",
        default=True,
        help="Freeze main and dev requirements.",
        show_default=True,
    )
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
    def freeze(both: bool, dev: bool, hashes: bool):
        """Create a requirements.txt file."""
        from .package import Package

        package: Package = Package.find_root()
        if both:
            logger.info("Freezing both requirement types.")
            package.freeze(False, not hashes)
            package.freeze(True, not hashes)
        else:
            package.freeze(dev, not hashes)

    @app.cli.command()
    @click.option(
        "--bump/--no-bump",
        "-b/ ",
        default=False,
        help="Increment the version before syncing.",
    )
    @click.option(
        "--level",
        "-l",
        type=click.Choice(SEMVER_LEVELS),
        default="patch",
        help="The part of the version to bump.",
    )
    def sync_versions(bump: bool, level: str):
        """Make sure that versions are synced between various files.

        The pyproject.toml version is treated as canonical.
        """
        from . import __version__
        from .package import Package

        package: Package = Package.find_root()
        version_cmd = run(
            "poetry", "version", "--short", text=True, capture_output=True
        )
        version = semver.parse_version_info(version_cmd.stdout.strip())
        if bump:
            logger.info("Bumping {0}.", level)
            version = str(SEMVER_BUMPS[level](version))
            run("poetry", "version", version)
            logger.success("New version: {0}", version)
        else:
            version = str(version)
            logger.info("Current version: {0}", version)

        if __version__.__version__ != version:
            logger.info("{0} out of date.", __version__.__name__)
            ver_file = Path(__version__.__file__)
            ver_file.write_text('__version__ = "{0}"\n'.format(version))
        else:
            logger.info("{0} up to date.", __version__.__name__)

        pkg = package.root_dir / "package.json"
        if pkg.is_file():
            pkg_data = json.loads(pkg.read_text())
            if pkg_data["version"] != version:
                logger.info("package.json out of date.")
                run(
                    "yarn",
                    "version",
                    "--no-git-tag-version",
                    "--no-commit-hooks",
                    "--new-version",
                    version,
                    check=True,
                )
            else:
                logger.info("package.json up to date.")
            assert json.loads(pkg.read_text())["version"] == version
        else:
            logger.warning("No package.json found.")

    @app.cli.command()
    @click.option("--serve/--no-serve", default=True, help="Don't start the server.")
    @click.option("--yarn/--no-yarn", default=True, help="Don't start yarn")
    def serve(serve: bool, yarn: bool):
        """Run dev server and build client bundles."""
        from .server import Server

        server = Server(app, start_server=serve, start_yarn=yarn)
        server.start()
        server.loop()

    @app.cli.command()
    @click.argument(
        "template",
        type=click.Path(exists=True, dir_okay=False),
        default=default_template,
    )
    @click.option(
        "--dev-output",
        "-d",
        type=click.Path(),
        default=dev_dir,
        help="The location of the development Dockerfile",
    )
    @click.option(
        "--prod-output",
        "-p",
        type=click.Path(),
        default=prod_dir,
        help="The location of the production Dockerfile",
    )
    @click.option(
        "--dry-run/--for-real",
        "-n/ ",
        default=False,
        help="Don't actually write new files to disk.",
    )
    @click.option("--verbose", "-v", count=True, help="Controls how much to log.")
    @click.option(
        "--yes",
        "-y",
        is_flag=True,
        default=False,
        help="Don't prompt to confirm when files are overwritten.",
    )
    @click.option(
        "--port",
        "-e",
        type=int,
        default=None,
        help="The exposed port in the resulting container.",
    )
    def dockerfiles(
        template: str,
        dev_output: str,
        prod_output: str,
        dry_run: bool,
        verbose: int,
        yes: bool,
        port: int,
    ):
        """Generate development and production Dockerfiles.

        Dockerfiles will be based on a given [TEMPLATE]
        """
        from .generate import Generator

        gen = Generator(template, dev_output, prod_output)
        gen.generate(dry_run, verbose, yes, port)
