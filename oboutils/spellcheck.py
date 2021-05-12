import pronto
from spellchecker import SpellChecker
import click


@click.command()
@click.argument('input')
@click.argument('log')
@click.pass_context
def run(ctx, input, log):
    onto = pronto.Ontology(input)
    spell = SpellChecker()
    
    out = open('output', 'w')
    
    for term in onto.terms():
        miss_name = spell.unknown(spell.split_words(term.name))
        if len(miss_name) > 0:
            out.write(f"Term {term.id} has a potentially misspelled word in its name.\n")
            out.write(f"Name: {term.name}\n")
            for miss in miss_name:
                out.write(f"    {miss}\n")
            out.write("\n")
            
        if term.definition is not None:
            miss_def = spell.unknown(spell.split_words(term.definition.strip()))
            if len(miss_def) > 0:
                out.write(f"Term {term.id} has a potentially misspelled word in its definition.\n")
                out.write(f"Definition: {term.definition.strip()}\n")
                for miss in miss_def:
                    out.write(f"    {miss}\n")
                out.write("\n")
                
    out.close()
    

if __name__ == '__main__':
    run()
