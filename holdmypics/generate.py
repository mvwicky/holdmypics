from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from difflib import SequenceMatcher
from functools import partial
from pathlib import Path
from typing import Any, ClassVar

import click
from attrs import define, field
from jinja2 import Environment, FileSystemLoader, Template

import config
from .cli_utils import run

split = partial(str.splitlines, keepends=True)


def diff_contents(a: str, b: str) -> SequenceMatcher:
    matcher = SequenceMatcher(None, *map(split, (a, b)), autojunk=True)
    return matcher


@define()
class Generator:
    common_context: ClassVar[dict[str, Any]] = {"python_version": sys.version_info[:3]}

    template_file: Path = field(converter=Path)
    dev_dir: Path = field(converter=Path)
    prod_dir: Path = field(converter=Path)

    _env: Environment | None = field(default=None, init=False, repr=False)
    _template: Template | None = field(default=None, init=False, repr=False)
    _node_version: str | None = field(default=None, init=False, repr=False)

    def confirm(self, file: Path, yes: bool) -> bool:
        if yes or not file.is_file():
            return True
        return click.confirm(f"Overwrite {config.rel_to_root(file)}?", default=True)

    def get_context(self, dev: bool, port: int | None) -> dict[str, str | bool | int]:
        extra = {
            "yarn_build": f"build{':dev' if dev else ''}",
            "requirements": f"requirements{'-dev' if dev else ''}.txt",
            "node_version": self.get_node_version(),
            "dev": dev,
        }
        if port is not None:
            extra["port"] = port
        ctx = self.common_context.copy()
        ctx.update(extra)
        return ctx

    def generate(self, dry_run: bool, verbosity: int, yes: bool, port: int | None):
        for dev in (True, False):
            mode = "dev" if dev else "prod"
            click.secho(f"Rendering {mode} template.", fg="green", bold=True)
            folder = self.dev_dir if dev else self.prod_dir
            if not folder.is_dir():
                folder.mkdir()
            ctx = self.get_context(dev, port)
            self.render(folder / "Dockerfile", ctx, dry_run, verbosity, yes)

    def render(
        self,
        file: Path,
        context: Mapping[str, Any],
        dry_run: bool,
        verbosity: int,
        yes: bool,
    ):
        cts = self.template.render(context)
        if file.is_file():
            matcher = diff_contents(file.read_text(), cts)
            ratio = matcher.ratio()
            if ratio == 1.0:
                click.secho("Nothing to do, output is the same.", fg="blue")
                if not dry_run:
                    os.utime(file)
                return
            else:
                click.secho(f"New file differs by {1.0 - ratio:.2%}", fg="yellow")
        if verbosity >= 1 or dry_run:
            click.echo(cts)
            click.echo("")
        if not self.confirm(file, yes or dry_run):
            raise click.ClickException("Breaking")
        if not dry_run:
            file.write_text(cts)
            click.secho(f"Wrote {config.rel_to_root(file)}", fg="blue")

    @property
    def template(self) -> Template:
        if self._template is None:
            self._template = self.env.get_template(self.template_file.name)
        return self._template

    @property
    def env(self) -> Environment:
        if self._env is None:
            self._env = self._make_env()
        return self._env

    def _make_env(self) -> Environment:
        searchpath = str(self.template_file.parent)
        loader = FileSystemLoader(searchpath)
        return Environment(
            loader=loader,
            autoescape=False,
            lstrip_blocks=True,
            trim_blocks=True,
            block_start_string="#{%",
            block_end_string="%}",
        )

    def get_node_version(self) -> str:
        if self._node_version is None:
            cmd = run("node", "--version", capture_output=True, text=True, no_log=True)
            version = cmd.stdout.strip().rsplit(".", 1)[0].lstrip("v")
            parts = version.split(".")
            assert len(parts) == 2
            assert all(p.isnumeric() for p in parts)
            self._node_version = version
        return self._node_version
