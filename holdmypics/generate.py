import operator as op
import string
from difflib import SequenceMatcher
from functools import partial
from pathlib import Path
from typing import Optional

import attr
import click
from cytoolz import merge
from jinja2 import Environment, FileSystemLoader, Template

junk = partial(op.contains, string.whitespace)

split = partial(str.splitlines, keepends=True)


def diff_contents(a: str, b: str) -> SequenceMatcher:
    a_lines, b_lines = map(split, [a, b])
    matcher = SequenceMatcher(junk, a_lines, b_lines)
    return matcher


@attr.s(slots=True, auto_attribs=True)
class Generator(object):
    template_file: Path = attr.ib(converter=Path)
    dev_dir: Path = attr.ib(converter=Path)
    prod_dir: Path = attr.ib(converter=Path)

    _env: Optional[Environment] = attr.ib(default=None, init=False, repr=False)
    _template: Optional[Template] = attr.ib(default=None, init=False, repr=False)

    def confirm(self, file: Path, yes: bool):
        if yes or not file.is_file():
            return True
        return click.confirm("Overwrite {0}?".format(file), default=True)

    def generate(self, dry_run: bool, verbosity: int, yes: bool, port: Optional[int]):
        contexts = [
            (True, {"yarn_build": "build:dev", "requirements": "requirements-dev.txt"}),
            (False, {"yarn_build": "build", "requirements": "requirements.txt"}),
        ]
        for dev, context in contexts:
            mode = "dev" if dev else "prod"
            click.secho("Rendering {0} template.".format(mode), fg="green", bold=True)
            folder = self.dev_dir if dev else self.prod_dir
            if not folder.is_dir():
                folder.mkdir()
            file: Path = folder / "Dockerfile"
            ctx = merge(context, {"dev": dev})
            if port is not None:
                ctx.update({"port": port})
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
            click.secho("Wrote {0}".format(file), fg="blue")

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
