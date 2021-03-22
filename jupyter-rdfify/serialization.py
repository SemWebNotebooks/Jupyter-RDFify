import rdflib
from IPython.display import display_pretty
from owlrl import DeductiveClosure, RDFS_Semantics, OWLRL_Semantics
from .rdf_module import RDFModule
from .graph import parse_graph, draw_graph
from .table import graph_spo_iterator, html_table
from .util import strip_comments

displays = ["graph", "table", "raw", "none"]
formats = ["turtle", "json-ld", "xml"]


class SerializationModule(RDFModule):
    def __init__(self, name, parser, logger, description, displayname):
        super().__init__(name, parser, logger, description, displayname)
        self.parser.add_argument(
            "--serialize", "-s", choices=formats, default="turtle", help="Format for serializing when display is set to raw.")
        self.parser.add_argument(
            "--display", "-d", choices=displays, default="graph", help="How output is displayed")
        self.parser.add_argument(
            "--label", "-l", help="Store graph locally with this label")
        self.parser.add_argument(
            "--prefix", "-p", help="Define a prefix which gets prepend to every query. Useful for PREFIX declarations", action="store_true")
        self.parser.add_argument(
            "--entail", "-e", choices=["rdfs", "owl", "rdfs+owl"], help="Uses a brute force implementation of the finite version of RDFS semantics or OWL 2 RL. Uses owlrl python package.")
        self.prefix = ""

    def handle(self, params, store):
        if params.cell is not None:
            if params.prefix:
                self.prefix = params.cell + "\n"
                self.log("Stored prefix.")
            else:
                try:
                    code = strip_comments(params.cell)
                    g = parse_graph(self.prefix + code,
                                    self.logger, self.name)
                except Exception as e:
                    self.log(f"Parse failed:\n{str(e)}")
                    store["rdfgraphs"]["last"] = None
                    store["rdfsources"]["last"] = self.prefix + params.cell
                    return
                g.source = lambda: self.name
                if params.label is not None:
                    store["rdfgraphs"][params.label] = g
                    store["rdfsources"][params.label] = self.prefix + params.cell
                store["rdfgraphs"]["last"] = g
                store["rdfsources"]["last"] = self.prefix + params.cell
                if params.entail is not None:
                    if params.entail == "rdfs":
                        DeductiveClosure(RDFS_Semantics).expand(g)
                    elif params.entail == "owl":
                        DeductiveClosure(OWLRL_Semantics).expand(g)
                    elif params.entail == "rdfs+owl":
                        DeductiveClosure(
                            OWLRL_Semantics, rdfs_closure=True).expand(g)
                if params.display == "none":
                    return
                elif params.display == "graph":
                    draw_graph(g, self.logger)
                elif params.display == "table":
                    self.logger.display_html(html_table(graph_spo_iterator(g)))
                else:
                    display_pretty(g.serialize(format=params.serialize,
                                               encoding="utf-8",).decode("utf-8"), raw=True)
