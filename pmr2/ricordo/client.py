from os.path import basename, dirname, join
from glob import glob

import requests
import json

from pmr2.virtuoso.sparql import quote_iri


def load_queries(target_dir):
    result = {}
    for fn in glob(join(target_dir, '*.txt')):
        with open(fn) as fd:
            result[basename(fn)[:-4]] = fd.read()
    return result

_base_queries = {}
def _load():
    global _base_queries
    _base_queries = load_queries(join(dirname(__file__),
        'resources', 'rdfstore_query'))

_load()
del _load


class SparqlClient(object):
    """
    A client for accessing the Virtuoso Sparql webservice endpoint.
    """

    def __init__(self, endpoint='http://localhost:8890/sparql',
            requests_session=None):

        if requests_session is None:
            requests_session = requests.Session()

        self.endpoint = endpoint
        self.requests_session = requests_session

    def query(self, sparql_query):
        r = self.requests_session.get(self.endpoint, params={
            'query': sparql_query,
            'format': 'application/json',
        })
        return r.json()


class RicordoClient(object):

    def __init__(self, root_endpoint, requests_session=None):
        self.root_endpoint = root_endpoint

        if requests_session is None:
            requests_session = requests.Session()
            requests_session.headers.update({
                'Accept': 'application/json',
                'Content-type': 'application/json',
            })
        self.requests_session = requests_session

    def get(self, endpoint, query):
        target = '%s/%s/%s' % (self.root_endpoint, endpoint, query)
        return self.requests_session.get(target).json()

    def post(self, endpoint, data):
        target = '%s/%s' % (self.root_endpoint, endpoint)
        return self.requests_session.post(target, data=json.dumps(data)).json()


class OwlkbClient(RicordoClient):
    """
    Owl knowledgebase client.
    """

    def __init__(self,
            root_endpoint='http://localhost:8080/ricordo-owlkb-ws/service',
            *a, **kw):
        super(OwlkbClient, self).__init__(root_endpoint, *a, **kw)

    def query_terms(self, query):
        return [i['id'] for i in self.get(query=query, endpoint='terms').get(
            'terms', {}).get('terms', [])]


class RdfStoreClient(SparqlClient):
    """
    RICORDO RDF Store client.
    """

    def search(self, target, data):
        t = _base_queries[target] % {'iri': '<%s>' % quote_iri(data)}
        return self.query(t).get('results', {}).get('bindings')

    def getResourceForAnnotation(self, query):
        return self.search('getResourceForAnnotation', query)

    def getAnnotationOfResource(self, query):
        return self.search('getAnnotationOfResource', query)


class OwlSparqlClient(SparqlClient):

    _sparql_query = {
        'term_lookup': """
            select ?s ?o
            %(from_graph_statement)s
            where {
                ?s <http://www.w3.org/2000/01/rdf-schema#label> ?o
                filter regex(?o, "%(keyword)s", "i") .
            }
        """,
    }

    def __init__(self, graph_urls=(), *a, **kw):
        self.graph_urls = graph_urls
        super(OwlSparqlClient, self).__init__(*a, **kw)

    def make_query(self, query_id, graph_urls=None, **kw):
        if graph_urls is None:
            graph_urls = self.graph_urls

        graph_stmt = '\n'.join(['from <%s>' % g for g in graph_urls])
        kw['from_graph_statement'] = graph_stmt
        return self._sparql_query[query_id] % kw

    def get_owl_terms(self, keyword, graph_urls=None):
        """
        Method to provide the labels and the associated identifier for
        the terms within the selected ontologies users will be searching
        their data against.
        """

        results = self.query(self.make_query('term_lookup', graph_urls,
            keyword=keyword.replace('"', '\\"')))
        return sorted([(i['o']['value'], i['s']['value'])
            for i in results['results']['bindings']])
