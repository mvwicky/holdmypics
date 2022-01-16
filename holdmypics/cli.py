from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import click
import semver
from flask import Flask
from loguru import logger
from semver import VersionInfo

from .cli_utils import CTX_SETTINGS, run

SEMVER_LEVELS = ("major", "minor", "patch", "prerelease", "build")
SEMVER_BUMPS: dict[str, Callable[[VersionInfo], Any]] = {
    level: getattr(VersionInfo, f"bump_{level}") for level in SEMVER_LEVELS
}


def register(app: Flask):
    cfg_path = cast(Path, app.config.get("BASE_PATH")) / "config"

    @app.cli.command(context_settings=CTX_SETTINGS)
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
        show_default=True,
    )
    def freeze(both: bool, dev: bool, hashes: bool):
        """Create a requirements.txt file."""
        from .package import Package

        package: Package = Package.find_root()
        if both:
            logger.info("Freezing both requirement types.")
            package.freeze(False, hashes)
            package.freeze(True, hashes)
        else:
            package.freeze(dev, hashes)

    @app.cli.command(context_settings=CTX_SETTINGS)
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
                )
            else:
                logger.info("package.json up to date.")
            assert json.loads(pkg.read_text())["version"] == version
        else:
            logger.warning("No package.json found.")

    @app.cli.command(context_settings=CTX_SETTINGS)
    @click.option("--serve/--no-serve", default=True, help="Start the server.")
    @click.option("--yarn/--no-yarn", default=True, help="Start yarn")
    @click.option("--wait-time", "wait", default=30, type=click.FLOAT, hidden=True)
    def serve(serve: bool, yarn: bool, wait: float):
        """Run dev server and build client bundles."""
        from .server import Server

        server = Server(app, wait, start_server=serve, start_yarn=yarn)
        server.start()
        server.loop()

    @app.cli.command(context_settings=CTX_SETTINGS)
    @click.argument(
        "template",
        type=click.Path(exists=True, dir_okay=False, path_type=Path),
        default=cfg_path / "Dockerfile.template",
    )
    @click.option(
        "--dev-output",
        "-d",
        type=click.Path(path_type=Path, file_okay=False),
        default=cfg_path / "dev",
        help="The location of the development Dockerfile",
    )
    @click.option(
        "--prod-output",
        "-p",
        type=click.Path(path_type=Path, file_okay=False),
        default=cfg_path / "prod",
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
        template: Path,
        dev_output: Path,
        prod_output: Path,
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
