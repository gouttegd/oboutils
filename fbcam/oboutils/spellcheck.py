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

from fbcam.oboutils import __version__

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


class OntoChecker(object):
    
    def __init__(self):
        self._checker = SpellChecker()
        self._post_filters = []
        self._pre_filters = []
        
    def add_custom_dictionary(self, dictfile):
        self._checker.word_frequency.load_text_file(dictfile)
        
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
            results['synonym'] = words
                
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
            if f.exclude(word):
                return True
        return False
        
        
class ExcludeWordsWithNumberFilter(object):
    
    def exclude(self, word):
        return not word.isalpha()
    
    
class ExcludeAllUppercaseWordsFilter(object):
    
    def exclude(self, word):
        return word.isupper()
    
class ExcludeShortWordsFilter(object):
    
    def __init__(self, threshold):
        self._threshold = threshold
        
    def exclude(self, word):
        return len(word) < self._threshold


@click.command()
@click.option('--exclude', multiple=True)
@click.argument('obofile')
@click.argument('log')
def run(exclude, obofile, log):
    onto = pronto.Ontology(obofile)
    
    checker = OntoChecker()
    for excl in exclude:
        checker.add_custom_dictionary(excl)
        
    checker.add_filter(ExcludeWordsWithNumberFilter())
    checker.add_filter(ExcludeShortWordsFilter(4))
    checker.add_filter(ExcludeAllUppercaseWordsFilter(), pre=True)
    
    out = open(log, 'w')
    
    for term in onto.terms():
        r = checker.check_term(term)
        if not r:
            continue
        
        out.write(f"Term: {term.name} ({term.id})\n")
        for k, v in r.items():
            out.write(f"In {k}: ")
            out.write(" ".join(v))
            out.write("\n")
        out.write("\n")
                
    out.close()
    

if __name__ == '__main__':
    run()
