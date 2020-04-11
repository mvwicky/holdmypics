import json
import subprocess
from pathlib import Path
from subprocess import DEVNULL

import click
import semver
import tomlkit as toml
from flask import Flask
from funcy import merge
from loguru import logger
from semver import VersionInfo

from . import __version__
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

        poetry = proj_data["tool"]["poetry"]
        version = semver.parse_version_info(poetry["version"])
        if bump:
            f = SEMVER_BUMPS[level]
            logger.info(f"Bumping {level}.")
            version = str(f(version))
            proj_data["tool"]["poetry"]["version"] = version
            proj.write_text(toml.dumps(proj_data))
            logger.success(f"New version: {version}")
        else:
            version = str(version)
            logger.info(f"Current version: {version}")

        if __version__.__version__ != version:
            logger.info(f"{__version__.__name__} out of date.")
            ver_file = Path(__version__.__file__)
            ver_file.write_text(f'__version__ = "{version}"\n')
        else:
            logger.info(f"{__version__.__name__} up to date.")

        if pkg.is_file():
            pkg_data = json.loads(pkg.read_text())
            if pkg_data["version"] != version:
                logger.info("package.json out of date.")
                pkg.write_text(json.dumps(merge(pkg_data, {"version": version})))
                args = ["yarn", "prettier", "--write", str(pkg)]
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
