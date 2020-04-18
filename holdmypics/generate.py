import operator as op
import string
from difflib import SequenceMatcher
from functools import partial
from pathlib import Path

import attr
import click
from funcy import merge
from jinja2 import Environment, FileSystemLoader, Template

junk = partial(op.contains, string.whitespace)


def diff_contents(a: str, b: str) -> SequenceMatcher:
    a_lines, b_lines = a.splitlines(), b.splitlines()
    matcher = SequenceMatcher(junk, a_lines, b_lines)
    return matcher


@attr.s(slots=True, auto_attribs=True)
class Generator(object):
    template_file: Path = attr.ib(converter=Path)
    dev_dir: Path = attr.ib(converter=Path)
    prod_dir: Path = attr.ib(converter=Path)

    _env: Environment = attr.ib(default=None, init=False, repr=False)
    _template: Template = attr.ib(default=None, init=False, repr=False)

    def confirm(self, file: Path, yes: bool):
        if yes or not file.is_file():
            return True
        return click.confirm(f"Overwrite {file}?", default=True)

    def generate(self, dry_run: bool, verbosity: int, yes: bool):
        contexts = [
            (True, {"yarn_build": "build:dev", "requirements": "requirements-dev.txt"}),
            (False, {"yarn_build": "build", "requirements": "requirements.txt"}),
        ]
        for dev, context in contexts:
            mode = "dev" if dev else "prod"
            click.secho(f"Rendering {mode} template.", fg="green", bold=True)
            folder = self.dev_dir if dev else self.prod_dir
            if not folder.is_dir():
                folder.mkdir()
            file: Path = folder / "Dockerfile"
            ctx = merge(context, {"dev": dev})
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
                click.secho(f"New file differs by {1.0 - ratio:.2%}", fg="yellow")
        if verbosity >= 1 or dry_run:
            print(cts)
            print("")
        if not self.confirm(file, yes or dry_run):
            raise click.ClickException("Breaking")

        if not dry_run:
            file.write_text(cts)
            click.secho(f"Wrote {file}", fg="blue")

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
            loader=loader, autoescape=False, lstrip_blocks=True, trim_blocks=True
        )
