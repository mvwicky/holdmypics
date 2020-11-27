import json
import subprocess
from pathlib import Path
from subprocess import DEVNULL
from typing import Any, Callable

import click
import semver
import tomlkit as toml
from cytoolz import get_in, merge
from flask import Flask
from loguru import logger
from semver import VersionInfo

from . import __version__
from .generate import Generator
from .package import Package
from .server import Server

SEMVER_BUMPS = {
    "major": VersionInfo.bump_major,
    "minor": VersionInfo.bump_minor,
    "patch": VersionInfo.bump_patch,
    "prerelease": VersionInfo.bump_prerelease,
    "build": VersionInfo.bump_build,
}
SEMVER_LEVELS = list(SEMVER_BUMPS)


def get_bump_fn(level: str) -> Callable[[VersionInfo], Any]:
    fn_name = "bump_{0}".format(level)
    return getattr(VersionInfo, fn_name)


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
        package: Package = Package.find_root()
        proj = package.root_dir / "pyproject.toml"
        pkg = package.root_dir / "package.json"

        proj_data = toml.parse(proj.read_text())

        poetry = get_in(["tool", "poetry"], proj_data)
        version = semver.parse_version_info(poetry["version"])
        if bump:
            f = SEMVER_BUMPS[level]
            logger.info("Bumping {0}.", level)
            version = str(f(version))
            proj_data["tool"]["poetry"]["version"] = version
            proj.write_text(toml.dumps(proj_data))
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

        if pkg.is_file():
            pkg_data = json.loads(pkg.read_text())
            if pkg_data["version"] != version:
                logger.info("package.json out of date.")
                pkg.write_text(json.dumps(merge(pkg_data, {"version": version})))
                args = ["yarn", "run", "prettier", "--write", str(pkg)]
                subprocess.run(args, stdout=DEVNULL, stderr=DEVNULL, check=True)
            else:
                logger.info("package.json up to date.")
        else:
            logger.warning("No package.json found.")

    @app.cli.command()
    @click.option("--run/--no-run", default=True)
    @click.option("--yarn/--no-yarn", default=True)
    def serve(run: bool, yarn: bool):
        """Run dev server and build client bundles."""
        server = Server(app, start_run=run, start_yarn=yarn)
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
    def generate_dockerfiles(
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
        gen = Generator(template, dev_output, prod_output)
        gen.generate(dry_run, verbose, yes, port)
