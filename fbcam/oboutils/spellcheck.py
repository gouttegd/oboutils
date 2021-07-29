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
from subprocess import run

from pronto import Ontology
from spellchecker import SpellChecker
import click

prog_name = "obo-spellcheck"


def die(msg):
    print(f"{prog_name}: {msg}", file=sys.stderr)
    sys.exit(1)


class OntoChecker(object):

    def __init__(self):
        self._checker = SpellChecker()
        self._post_filters = []
        self._pre_filters = []

    def add_custom_dictionary(self, dictionary):
        self._checker.word_frequency.load_text(dictionary)

    def add_filter(self, filter_, pre=False):
        if pre:
            self._pre_filters.append(filter_)
        else:
            self._post_filters.append(filter_)

    def check_term(self, term):
        n = 0
        results = {}

        for field in ['name', 'definition', 'comment']:
            words = self._check_term_field(term, field)
            if words is not None:
                n += 1
                results[field] = words

        words = self._check_term_synonyms(term)
        if words is not None:
            n += 1
            results['synonyms'] = words

        if n > 0:
            return results
        else:
            return None

    def _check_term_field(self, term, field):
        value = getattr(term, field)
        if value is None:
            return None

        words = self._check_value(value)
        if len(words):
            return words
        else:
            return None

    def _check_term_synonyms(self, term):
        words = []
        for synonym in term.synonyms:
            words.extend(self._check_value(synonym.description))

        if len(words):
            return words
        else:
            return None

    def _check_value(self, value):
        input_words = self._checker.split_words(value)
        input_words = [w for w in input_words if not self._apply_filters(w, self._pre_filters)]

        words = self._checker.unknown(input_words)
        words = [w for w in words if not self._apply_filters(w, self._post_filters)]

        return words

    def _apply_filters(self, word, filters):
        for f in filters:
            if f(word):
                return True
        return False


def exclude_words_with_number(word):
    return not word.isalpha()


def exclude_all_uppercase_words(word):
    return word.isupper()


def exclude_camelcase_words(word):
    return word[0].islower() and not word[1:].islower()


def make_exclude_short_word_filter(threshold):

    def exclude_short_word_filter(word):
        return len(word) < threshold

    return exclude_short_word_filter


def _load_dictionary(location):
    if location[0] == '|':
        r = run(location[1:], shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Command failed ({r.returncode})")
        return r.stdout
    else:
        with open(location, 'r') as f:
            return f.read()


@click.command('spellcheck')
@click.argument('obofile')
@click.option('--output', '-o', type=click.File('w'), default=sys.stdout,
              help="""Write the report to the specified FILE instead
                      of standard output.""")
@click.option('--dictionary', '-d', multiple=True, metavar='DICT',
              help="""Use the specified additional dictionary.
                      This option may be used multiple times to use
                      as many additional dictionaries as needed.
                      If DICT starts with a pipe character ('|'),
                      it is interpreted as a command that is expected
                      to write the dictionary to its standard output. """)
@click.option('--obsolete/--no-obsolete', default=False,
              help="""Check terms marked as obsolete.""")
def check_ontology(obofile, output, dictionary, obsolete):
    """Spell-check the specified OBOFILE.
    
    This command performs a spell-check on the ontology in the
    provided OBO file. For every term defined in the ontology,
    it looks for misspelled words in the label, the definition,
    and any comment and synonym.
    
    It produces a report listing the misspelled words for each
    term.
    """

    try:
        onto = Ontology(obofile)
    except Exception as e:
        die(f"Cannot load ontology: {e}")

    checker = OntoChecker()
    for dictfile in dictionary:
        try:
            dictdata = _load_dictionary(dictfile)
        except Exception as e:
            die(f"Cannot load dictionary: {e}")
        checker.add_custom_dictionary(dictdata)

    checker.add_filter(exclude_words_with_number)
    checker.add_filter(make_exclude_short_word_filter(4))
    checker.add_filter(exclude_all_uppercase_words, pre=True)
    checker.add_filter(exclude_camelcase_words, pre=True)

    for term in sorted(onto.terms()):
        if term.obsolete and not obsolete:
            continue
        r = checker.check_term(term)
        if not r:
            continue

        output.write(f"Term: {term.name} ({term.id})\n")
        for k, v in r.items():
            output.write(f"In {k}: ")
            output.write(" ".join(sorted(v)))
            output.write("\n")
        output.write("\n")


if __name__ == '__main__':
    check_ontology()
