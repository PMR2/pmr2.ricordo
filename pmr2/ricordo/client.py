import requests
import json


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
        return self.get(query=query, endpoint='terms')


class RdfStoreClient(RicordoClient):
    """
    RICORDO RDF Store client.
    """

    def __init__(self,
            root_endpoint='http://localhost:8080/ricordo-rdfstore-ws/service',
            *a, **kw):
        super(RdfStoreClient, self).__init__(root_endpoint, *a, **kw)

    def search(self, target, data):
        return self.post(endpoint='search/' + target, data=data)

    def getResourceForAnnotation(self, query):
        return self.search(target='getResourceForAnnotation', data={
            'query': query,
        })

    def getAnnotationOfResource(self, query):
        return self.search(target='getAnnotationOfResource', data={
            'query': query,
        })


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


class OwlSparqlClient(SparqlClient):

    _sparql_query = """
        select ?s ?o
        %(from_graph_statement)s
        where {
            ?s <http://www.w3.org/2000/01/rdf-schema#label> ?o
            filter regex(?o, "%%(keyword)s", "i") .
        }
    """

    def __init__(self, graph_urls=(), *a, **kw):
        self.graph_urls = graph_urls
        self.default_sparql_query = self.make_query(graph_urls)
        super(OwlSparqlClient, self).__init__(*a, **kw)

    def make_query(self, graph_urls):
        stmt = '\n'.join(['from <%s>' % g for g in graph_urls])
        return self._sparql_query % {'from_graph_statement': stmt}

    def get_owl_terms(self, keyword):
        """
        Method to provide the labels and the associated identifier for
        the terms within the selected ontologies users will be searching
        their data against.
        """

        results = self.query(self.default_sparql_query % {'keyword': keyword})
        return sorted([(i['o']['value'], i['s']['value'])
            for i in results['results']['bindings']])
