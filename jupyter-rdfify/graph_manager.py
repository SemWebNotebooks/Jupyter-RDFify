
from owlrl import DeductiveClosure, RDFS_Semantics, OWLRL_Semantics
from .graph import draw_graph
from .rdf_module import RDFModule


class GraphManagerModule(RDFModule):

    def __init__(self, name, parser, logger, description, displayname):
        super().__init__(name, parser, logger, description, displayname)
        self.parser.add_argument(
            "action", choices=["list", "remove", "draw", "entail-rdfs", "entail-owl", "entail-rdfs+owl"], help="Action to perform")
        self.parser.add_argument(
            "--label", "-l", help="Reference a local graph by label")

    def check_label(self, label, store):
        if label is not None:
            if label in store["rdfgraphs"]:
                return True
            else:
                self.log(f"Graph labelled '{label}' not found.")
        else:
            self.log(
                "Please specify the label of a graph with parameter --label or -l.")

    def handle(self, params, store):
        if params.action is not None:
            if params.action == "list":
                labels = "The following labelled graphs are present:<br><ul>"
                for label in store["rdfgraphs"].keys():
                    labels += f"<li>{label}</li>"
                self.logger.display_html(labels + "</ul>")
            elif params.action == "draw":
                if self.check_label(params.label, store):
                    draw_graph(store["rdfgraphs"]
                               [params.label], self.logger)
            elif params.action == "remove":
                if self.check_label(params.label, store):
                    del store["rdfgraphs"][params.label]
                    self.log(
                        f"Graph labelled '{params.label}' has been removed.")
            elif params.action == "entail-rdfs":
                if self.check_label(params.label, store):
                    DeductiveClosure(RDFS_Semantics).expand(
                        store["rdfgraphs"][params.label])
                    self.log(
                        f"Graph labelled '{params.label}' has been entailed using the RDFS regime.")
            elif params.action == "entail-owl":
                if self.check_label(params.label, store):
                    DeductiveClosure(OWLRL_Semantics).expand(
                        store["rdfgraphs"][params.label])
                    self.log(
                        f"Graph labelled '{params.label}' has been entailed using the OWL-RL regime.")
            elif params.action == "entail-rdfs+owl":
                if self.check_label(params.label, store):
                    DeductiveClosure(OWLRL_Semantics, rdfs_closure=True).expand(
                        store["rdfgraphs"][params.label])
                    self.log(
                        f"Graph labelled '{params.label}' has been entailed using the RDFS regime and then the OWL-RL regime.")
