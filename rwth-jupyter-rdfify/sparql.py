from IPython.display import display, display_pretty
from SPARQLWrapper import SPARQLWrapper

from .rdf_module import RDFModule
from .graph import parse_graph, draw_graph
from .table import display_table, html_table

def parse_header(line):
    """Replacement for cgi.parse_header"""
    parts = line.split(';')
    main_type = parts[0].strip()
    pdict = {}
    for p in parts[1:]:
        if '=' in p:
            name, value = p.split('=', 1)
            name = name.strip().lower()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            pdict[name] = value
    return main_type, pdict


formats = ["xml", "json"]
displays = ["graph", "table", "raw", "none"]
mime_types = {
    "application/sparql-results+xml": ["table"],
    "application/rdf+xml": ["graph", "table"],
    "application/xml": [],
    "application/sparql-results+json": ["table"],
}


class SPARQLModule(RDFModule):
    def __init__(self, name, parser, logger, description, displayname):
        super().__init__(name, parser, logger, description, displayname)
        self.parser.add_argument("--endpoint", "-e", help="SPARQL endpoint")
        self.parser.add_argument(
            "--format", "-f", choices=formats, help="Requested format for query result", default="xml")
        self.parser.add_argument(
            "--display", "-d", choices=displays, help="How output is displayed. Does not work for local queries.", default="table")
        grp = self.parser.add_mutually_exclusive_group()
        grp.add_argument(
            "--prefix", "-p", help="Define a prefix which gets prepend to every query. Useful for PREFIX declarations", action="store_true")
        grp.add_argument(
            "--local", "-l", help="Give a label of a local graph. This cell will then ignore the endpoint and query the graph instead")
        self.parser.add_argument(
            "--store", "-s", help="Store result of the query with this label")
        self.prefix = ""
        self.wrapper = None

    def query(self, query, params):
        self.log(params)
        if params.endpoint is not None:
            self.wrapper = SPARQLWrapper(params.endpoint)
        if self.wrapper is not None:
            self.wrapper.setQuery(self.prefix + query)
            self.wrapper.setReturnFormat(params.format)
            try:
                result = self.wrapper.query()
                if result._get_responseFormat() != params.format:
                    self.log(
                        f"""
The server responded with a format different from the requested format.\n
Either the server does not support the requested format or the query resulted in an incompatible type.\n
Requested: '{params.format}', Response: '{result._get_responseFormat()}'
                        """)
                content_type = parse_header(result.info()["content-type"])
                body = result.response.read()
                self.display_response(body, content_type[0], params.display)
                return result
            except Exception as e:
                self.log(f"Error during query:\n{str(e)}")
        else:
            self.log("Endpoint not set. Use --endpoint parameter.")

    def queryLocal(self, query, graph):
        try:
            res = graph.query(query)
            if res.type == "SELECT":
                self.logger.display_html(
                    html_table(select_result_row_iter(res)))
            elif res.type == "ASK":
                self.logger.print(res.askAnswer)
            elif res.type == "CONSTRUCT":
                draw_graph(res.graph, self.logger)
            elif res.type == "DESCRIBE":
                draw_graph(res.graph, self.logger)
            return res
        except Exception as e:
            self.log(f"Error during local query:\n{str(e)}")

    def display_response(self, body, mime, method):
        if method == "none":
            return
        if not mime in mime_types:
            self.log(
                f"Mime type '{mime}' not supported. Defaulting to raw display.")
            method = "raw"
        elif method in mime_types[mime]:
            if method == "graph":
                g = parse_graph(body, self.logger)
                draw_graph(g, self.logger)
            elif method == "table":
                display_table(body, mime, self.logger)
        else:
            if method != "raw":
                self.log(
                    f"Incompatible display option '{method}' for mime type '{mime}'. Defaulting to raw display.")
            self.logger.print(body.decode("utf-8"))

    def handle(self, params, store):
        if params.cell is not None:
            if params.prefix:
                self.prefix = params.cell + "\n"
                self.log("Stored prefix.")
            elif params.local is not None:
                if params.local in store["rdfgraphs"]:
                    res = self.queryLocal(
                        self.prefix + params.cell, store["rdfgraphs"][params.local])
                    if params.store is not None:
                        store["rdfresults"][params.store] = res
                        store["rdfsources"][params.store] = params.cell
                    store["rdfresults"]["last"] = res
                    store["rdfsources"]["last"] = params.cell
                else:
                    self.log(f"Graph labelled '{params.local}' not found.")
            else:
                res = self.query(self.prefix + params.cell, params)
                if params.store is not None:
                    store["rdfresults"][params.store] = res
                    store["rdfsources"][params.store] = params.cell
                store["rdfresults"]["last"] = res
                store["rdfsources"]["last"] = params.cell


def select_result_row_iter(result):
    header = []
    for var in result.vars:
        header.append(var.n3())
    yield header
    for row in result:
        yield row
