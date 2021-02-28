import sys
from difflib import SequenceMatcher
from functools import partial
from pathlib import Path
from typing import ClassVar, Optional, Union

import attr
import click
from jinja2 import Environment, FileSystemLoader, Template

import config

PY_VERSION = ".".join(map(str, sys.version_info[0:3]))

split = partial(str.splitlines, keepends=True)


def diff_contents(a: str, b: str) -> SequenceMatcher:
    a_lines, b_lines = map(split, [a, b])
    matcher = SequenceMatcher(None, a_lines, b_lines, autojunk=True)
    return matcher


@attr.s(slots=True, auto_attribs=True)
class Generator(object):
    common_context: ClassVar[dict[str, str]] = {
        "python_version": PY_VERSION,
        "gunicorn_config": "config/gunicorn_config",
    }

    template_file: Path = attr.ib(converter=Path)
    dev_dir: Path = attr.ib(converter=Path)
    prod_dir: Path = attr.ib(converter=Path)

    _env: Optional[Environment] = attr.ib(default=None, init=False, repr=False)
    _template: Optional[Template] = attr.ib(default=None, init=False, repr=False)

    def confirm(self, file: Path, yes: bool) -> bool:
        if yes or not file.is_file():
            return True
        rel = config.rel_to_root(file)
        return click.confirm("Overwrite {0}?".format(rel), default=True)

    def get_context(
        self, dev: bool, port: Optional[int]
    ) -> dict[str, Union[str, bool, int]]:
        build_suffix = ":dev" if dev else ""
        req_suffix = "-dev" if dev else ""
        ctx = {
            **self.common_context,
            "yarn_build": f"build{build_suffix}",
            "requirements": f"requirements{req_suffix}.txt",
            "dev": dev,
        }
        if port is not None:
            ctx["port"] = port
        return ctx

    def generate(self, dry_run: bool, verbosity: int, yes: bool, port: Optional[int]):
        for dev in (True, False):
            mode = "dev" if dev else "prod"
            click.secho(f"Rendering {mode} template.", fg="green", bold=True)
            folder = self.dev_dir if dev else self.prod_dir
            if not folder.is_dir():
                folder.mkdir()
            file: Path = folder / "Dockerfile"
            ctx = self.get_context(dev, port)
            self.render(file, ctx, dry_run, verbosity, yes)

    def render(
        self, file: Path, context: dict, dry_run: bool, verbosity: int, yes: bool
    ):
        cts = self.template.render(context)
        if file.is_file():
            matcher = diff_contents(file.read_text(), cts)
            ratio = matcher.ratio()
            if ratio == 1.0:
                click.secho("Nothing to do, output is the same.", fg="blue")
                return
            else:
                click.secho(
                    "New file differs by {0:.2%}".format(1.0 - ratio), fg="yellow"
                )
        if verbosity >= 1 or dry_run:
            print(cts)
            print("")
        if not self.confirm(file, yes or dry_run):
            raise click.ClickException("Breaking")

        if not dry_run:
            file.write_text(cts)
            click.secho("Wrote {0}".format(config.rel_to_root(file)), fg="blue")

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
