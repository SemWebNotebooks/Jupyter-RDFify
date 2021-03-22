from pyshex.utils.schema_loader import SchemaLoader
from pyshex import ShExEvaluator
from .rdf_module import RDFModule


class ShexModule(RDFModule):
    def __init__(self, name, parser, logger, description, displayname):
        super().__init__(name, parser, logger, description, displayname)
        self.parser.add_argument(
            "action", choices=["parse", "validate", "prefix"], help="Action to perform")
        self.parser.add_argument(
            "--label", "-l", help="Shape label for referencing")
        self.parser.add_argument(
            "--graph", "-g", help="Graph label for validation")
        self.parser.add_argument(
            "--focus", "-f", help="URI of node to focus on"
        )
        self.parser.add_argument(
            "--start", "-s", help="Starting shape"
        )
        self.loader = SchemaLoader()
        self.evaluator = ShExEvaluator()
        self.prefix = ""

    def print_result(self, result):
        self.log(f"Evaluating shape '{result.start}' on node '{result.focus}'")
        if result.result:
            self.logger.print("PASSED!")
        else:
            self.logger.print(f"FAILED! Reason:\n{result.reason}\n")

    def handle(self, params, store):
        if params.action == "prefix":
            self.prefix = params.cell + "\n"
            self.log("Stored Prefix.")
        elif params.action == "parse":
            if params.cell is not None:
                try:
                    schema = self.loader.loads(self.prefix + params.cell)
                    if params.label is not None and schema is not None:
                        store["rdfshapes"][params.label] = schema
                    self.log("Shape successfully parsed.")
                except Exception as e:
                    self.log(f"Error during shape parse:\n{str(e)}")
            else:
                self.log("No cell content to parse.")
        elif params.action == "validate":
            if params.label is not None and params.graph is not None:
                if params.label in store["rdfshapes"]:
                    if params.graph in store["rdfgraphs"]:
                        result = self.evaluator.evaluate(
                            store["rdfgraphs"][params.graph],
                            store["rdfshapes"][params.label],
                            start=params.start,
                            focus=params.focus
                        )
                        for r in result:
                            self.print_result(r)
                    else:
                        self.log(
                            f"Found no graph with label '{params.graph}'.")
                else:
                    self.log(f"Found no shape with label '{params.label}'.")
            else:
                self.log("A shape and a graph label are required for validation.")
