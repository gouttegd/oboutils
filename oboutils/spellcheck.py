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

import pronto
from spellchecker import SpellChecker
import click

from oboutils import __version__

prog_name = "obo-spellcheck"
prog_notice = f"""\
{prog_name} {__version__}
Copyright © 2021 Damien Goutte-Gattat

This program is released under the GNU General Public License.
See the COPYING file or <http://www.gnu.org/licenses/gpl.html>.
"""


def die(msg):
    print(f"{prog_name}: {msg}", file=sys.stderr)
    sys.exit(1)

spell = SpellChecker()


def check_term_field(term, field, out):
    field_value = getattr(term, field)
    if field_value is None:
        return
    
    words = spell.unknown(spell.split_words(field_value))
    words = [w for w in words if not exclude_word(w)]
    if len(words):
        out.write(f"term: {term.id} ({term.name})\n")
        out.write(f"{field}: {field_value}\n")
        out.write("words: ")
        out.write(" ".join(words))
        out.write("\n\n")
        
        
def check_term_synonyms(term, out):
    for synonym in term.synonyms:
        words = spell.unknown(spell.split_words(synonym.description))
        words = [w for w in words if not exclude_word(w)]
        if len(words):
            out.write(f"term: {term.id} ({term.name})\n")
            out.write(f"synonym: {synonym.description}\n")
            out.write("words: ")
            out.write(" ".join(words))
            out.write("\n\n")
            
            
def exclude_word(word):
    if not word.isalpha():
        return True
    if len(word) < 3:
        return True
    return False


@click.command()
@click.option('--exclude', default=None)
@click.argument('obofile')
@click.argument('log')
def run(exclude, obofile, log):
    onto = pronto.Ontology(obofile)
    
    if exclude is not None:
        spell.word_frequency.load_text_file(exclude)
    
    out = open(log, 'w')
    
    for term in onto.terms():
        check_term_field(term, 'name', out)
        check_term_field(term, 'definition', out)
        check_term_field(term, 'comment', out)
        check_term_synonyms(term, out)
                
    out.close()
    

if __name__ == '__main__':
    run()
