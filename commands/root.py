import click

from .cloud import cloud
from .consolidate_and_vacuum import consolidate, vacuum
from .convert_from import convert_from
from .dump import dump


@click.group()
def root():
    pass


root.add_command(cloud)
root.add_command(convert_from)
root.add_command(dump)
root.add_command(consolidate)
root.add_command(vacuum)
