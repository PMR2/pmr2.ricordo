import re


class Converter(object):

    def __init__(self, rules):
        self.compiled_rules = [(re.compile(k), v) for k, v in rules]

    def __call__(self, identifier):
        return [rule.sub(replacement, identifier) for rule, replacement in
            self.compiled_rules if rule.search(identifier)]

purlobo_to_identifiers = Converter((
    ('^http://purl.org/obo/owlapi/gene_ontology#GO_([0-9]{7})$',
        'http://identifiers.org/obo.go/GO:\\1'),
    ('^http://purl.org/obo/owlapi/gene_ontology#GO_([0-9]{7})$',
        'http://identifiers.org/go/GO:\\1'),
    ('^http://purl.org/obo/owlapi/fma#FMA_([0-9]*)$',
        'http://identifiers.org/obo.fma/FMA:\\1'),
    ('^http://purl.org/obo/owlapi/fma#FMA_([0-9]*)$',
        'http://identifiers.org/fma/FMA:\\1'),
))

purlobo_to_owlkb = Converter((
    ('http://purl.org/obo/owlapi/gene_ontology#GO_([0-9]{7})', 'GO_\\1'),
    ('http://purl.org/obo/owlapi/fma#FMA_([0-9]*)', 'FMA_\\1'),
))
