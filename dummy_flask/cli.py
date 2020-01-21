import json
import subprocess
from pathlib import Path

import click
import toml
from flask import Flask

from . import __version__
from .package import Package, find_path_named


def register(app: Flask):
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

        click.secho(f"Current version: ", fg="green", nl=False)
        click.secho(f"{version}", bold=True)
        if __version__.__version__ != version:
            click.echo("Version module out of date.")
            ver_file = Path(__version__.__file__)
            ver_file.write_text(f'__version__ = "{version}"\n')

        if pkg.is_file():
            pkg_data = json.loads(pkg.read_text())
            if pkg_data["version"] != version:
                click.echo("package.json out of date.")
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
            click.echo("No package.json found.")

    @app.cli.command()
    def icons():
        from bs4 import BeautifulSoup

        node_modules = find_path_named("node_modules")
        icons_dir = node_modules / "feather-icons" / "dist" / "icons"
        svgs = icons_dir.glob("*svg")
        an_icon = next(svgs)
        print(an_icon.name)
        soup = BeautifulSoup(an_icon.read_text(), "xml")
        p = soup.find("path")
        print(p.attrs["d"])
