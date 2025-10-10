from IPython.core.magic import (
    Magics, magics_class, line_cell_magic, needs_local_scope)
from shlex import split

from .rdf_module import RDFModule
from .log import RDFLogger
from .util import MagicParser


@magics_class
class JupyterRDF(Magics):

    def __init__(self, shell):
        super(JupyterRDF, self).__init__(shell)
        self.parser = MagicParser("%rdf")
        self.parser.set_defaults(func=lambda _: (
            self.logger.out("Usage: %rdf --help")))
        self.parser.add_argument(
            "--verbose", "-v", help="Enable verbose output", action="store_true")
        self.parser.add_argument(
            "--return-store", "-r", help="Returns a copy of all present elements (graphs, schemas, etc.)", action="store_true")
        self.subparsers = self.parser.add_subparsers(help="RDF modules")
        self.submodules = list()
        self.logger = RDFLogger()

        self.store = {
            "rdfgraphs": dict(),
            "rdfsources": dict(),
            "rdfresults": dict(),
            "rdfshapes": dict()
        }

    def register_module(self, module_class, name, description="", displayname=None):
        assert issubclass(module_class, RDFModule)
        self.submodules.append(module_class(
            name, self.subparsers, self.logger, description, displayname))

    @line_cell_magic
    def rdf(self, line, cell=None):
        try:
            args = self.parser.parse_args(split(line))
            self.logger.set_verbose(args.verbose)
            if args.return_store:
                return self.store
            args.cell = cell
            return args.func(args, self.store)
        except Exception as e:
            self.logger.print(str(e))
