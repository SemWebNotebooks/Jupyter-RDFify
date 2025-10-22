__version__ = '1.0.2'

from IPython.display import display_javascript
from .jupyter_rdf import JupyterRDF
from .serialization import SerializationModule
from .sparql import SPARQLModule
from .graph_manager import GraphManagerModule
from .persistence import PersistenceModule


def load_ipython_extension(ipython):
    """Executed when loading the extension. Registers all default modules and the %rdf magic."""
    # Activates syntax highlighting for sparql, turtle and json-ld in jupyter notebook.
    # This does not work on JupyterLab because the global IPython object is not defined there.
    js_highlight = """
    if (typeof IPython !== "undefined") {
        IPython.CodeCell.options_default.highlight_modes['application/sparql-query'] = {'reg':[/^%%rdf sparql/]};
        IPython.CodeCell.options_default.highlight_modes['text/turtle'] = {'reg':[/^%%rdf turtle/]};
        IPython.CodeCell.options_default.highlight_modes['application/ld+json'] = {'reg':[/^%%rdf json-ld/]};
        IPython.notebook.get_cells().map(function(cell){ if (cell.cell_type == 'code'){ cell.auto_highlight(); } });
    }
    """
    display_javascript(js_highlight, raw=True)

    ipython.push({
        "rdfgraphs": dict(),
        "rdfsources": dict(),
        "rdfresults": dict(),
        "rdfshapes": dict()
    }, True)
    jupyter_rdf = JupyterRDF(ipython)
    jupyter_rdf.register_module(
        SerializationModule, "turtle", "Turtle module", "Turtle")
    jupyter_rdf.register_module(
        SerializationModule, "n3", "Notation 3 module", "N3")
    jupyter_rdf.register_module(
        SerializationModule, "json-ld", "JSON-LD module", "JSON-LD")
    jupyter_rdf.register_module(
        SerializationModule, "xml", "XML+RDF module", "XML+RDF")
    jupyter_rdf.register_module(
        SPARQLModule, "sparql", "SPARQL module", "SPARQL")
    jupyter_rdf.register_module(
        GraphManagerModule, "graph", "Graph management module", "Graphman")
    jupyter_rdf.register_module(
        PersistenceModule, "persistence", "Persistence module", "Persistence")
    ipython.register_magics(jupyter_rdf)
