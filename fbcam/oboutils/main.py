# -*- coding: utf-8 -*-
# oboutils - OBO utilities
# Copyright (C) 2021 Damien Goutte-Gattat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys

import click

from fbcam.oboutils import __version__
from fbcam.oboutils.spellcheck import check_ontology
from fbcam.oboutils.xrefmaps import xrefmaps

prog_name = "oboutils"
prog_notice = f"""\
{prog_name} {__version__}
Copyright © 2021 Damien Goutte-Gattat

This program is released under the GNU General Public License.
See the COPYING file or <http://www.gnu.org/licenses/gpl.html>.
"""


def die(msg):
    print(f"{prog_name}: {msg}", file=sys.stderr)
    sys.exit(1)


@click.group(commands=[check_ontology, xrefmaps],
             context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version=__version__, message=prog_notice)
def oboutil():
    """OBO Utilities."""

    pass


if __name__ == '__main__':
    try:
        oboutil()
    except Exception as e:
        die(e)
