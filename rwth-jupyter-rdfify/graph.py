from graphviz import Digraph
import rdflib
from .util import literal_to_string, StopCellExecution


def draw_graph(g, logger, shorten_uris=True, rename_blank_nodes=True):
    ns = g.namespace_manager
    dot = Digraph()
    nodes = dict()
    bnodes = 0
    for i, node in enumerate(g.all_nodes()):
        if isinstance(node, rdflib.term.URIRef):
            if shorten_uris:
                l = node.n3(ns)
            else:
                l = node.n3()
            dot.node(str(i), label=l)
        elif isinstance(node, rdflib.term.BNode):
            if rename_blank_nodes:
                l = f"_:bn{bnodes}"
                bnodes += 1
            else:
                l = node.n3()
            dot.node(str(i), label=l)
        elif isinstance(node, rdflib.term.Literal):
            if shorten_uris:
                l = node.n3(ns)
            else:
                l = node.n3()
            dot.node(str(i), label=l, shape="box")
        else:
            continue
        nodes[node.n3()] = str(i)
    for s, p, o in g:
        if shorten_uris:
            l = p.n3(ns)
        else:
            l = p.n3()
        dot.edge(nodes[s.n3()], nodes[o.n3()], label=l)
    logger.out(dot)


def parse_graph(string, logger, fmt="xml"):
    try:
        return rdflib.Graph().parse(data=string, format=fmt)
    except Exception as err:
        logger.print(f"Could not parse {fmt} graph:<br>{str(err)}")
        raise StopCellExecution
