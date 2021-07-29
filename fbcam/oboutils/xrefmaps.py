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
from pronto import Ontology

from fbcam.oboutils import __version__

prog_name = "obo-xrefmaps"
prog_notice = f"""\
Copyright © 2021 Damien Goutte-Gattat

This program is released under the GNU General Public License.
See the COPYING file or <http://www.gnu.org/licenses/gpl.html>.
"""


def die(msg):
    print(f"{prog_name}: {msg}", file=sys.stderr)
    sys.exit(1)


def _has_xref_in_set(term, ids):
    xrefs = [x.id for x in term.xrefs]
    for xref in xrefs:
        if xref in ids:
            return xref
    return False


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version=__version__, message=prog_notice)
@click.argument('source')
@click.argument('foreign')
def xrefmaps(source, foreign):
    """Find xref mappings between two ontologies."""

    try:
        src = Ontology(source)
        frn = Ontology(foreign)
    except Exception as e:
        die(f"Cannot load ontology: {e}")

    # IDs from the source ontology
    src_ids = [t.id for t in src.terms()]

    # IDs from the foreign ontology
    frn_ids = [t.id for t in frn.terms()]

    # Loop over the source ontology
    for term in src.terms():
        frn_ref = _has_xref_in_set(term, frn_ids)
        if frn_ref:
            frn_term = frn.get(frn_ref)
            frn_name = frn_term.name

            src_ref = _has_xref_in_set(frn_term, src_ids)
            if src_ref:
                src_term = src.get(src_ref)
                src_name = src_term.name
                src_id = src_term.id
            else:
                src_name = ''
                src_id = ''
            print(f"{term.id},{term.name},{frn_ref},{frn_name},{src_id},{src_name}")


if __name__ == '__main__':
    xrefmaps()
