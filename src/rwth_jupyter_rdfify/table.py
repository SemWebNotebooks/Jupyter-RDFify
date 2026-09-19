from IPython.display import HTML
import html
import xml.etree.ElementTree as ET
from rdflib.term import Node
from .graph import parse_graph
import json


def literal_text(value, lang=None, datatype=None):
    """A literal for a result table: its value, then @lang or ^^datatype. A language-tagged literal
    has no datatype of its own (rdf:langString), so only the tag is shown. HTML-escaped."""
    text = html.escape(value or "")
    if lang:
        return f"{text}@{html.escape(lang)}"
    if datatype:
        return f"{text}^^{html.escape(datatype)}"
    return text


def display_table(body, mime, logger):
    if mime == "application/sparql-results+xml":
        root = ET.fromstring(body)
        logger.display_html(html_table(xml_row_iterator(root)))
    elif mime == "application/sparql-results+json":
        result = json.loads(body)
        logger.display_html(html_table(json_row_iterator(result)))
    elif mime == "application/rdf+xml":
        g = parse_graph(body, logger)
        logger.display_html(html_table(graph_spo_iterator(g)))
    else:
        logger.print("Could not display table")


#

def xml_row_iterator(elem):
    """Iterates a Sparql xml result (http://www.w3.org/2005/sparql-results#) by rows. First result are the column headers."""
    ns = {"sparql": "http://www.w3.org/2005/sparql-results#"}
    headers = []
    for head in elem.findall("sparql:head/sparql:variable", ns):
        headers.append(head.attrib["name"])
    yield headers
    for result in elem.findall("sparql:results/sparql:result", ns):
        # a result lists only its bound variables: place each value under its own column
        values = {}
        for binding in result.findall("sparql:binding", ns):
            n = binding[0]
            if n.tag == "{http://www.w3.org/2005/sparql-results#}literal":
                value = literal_text(n.text, n.get("{http://www.w3.org/XML/1998/namespace}lang"),
                                     n.get("datatype"))
            elif n.tag == "{http://www.w3.org/2005/sparql-results#}uri":
                value = "&lt;{}&gt;".format(html.escape(n.text or ""))
            elif n.tag == "{http://www.w3.org/2005/sparql-results#}bnode":
                value = "&lt;_:{}&gt;".format(html.escape(n.text or ""))
            else:
                value = "Unknown node: {}".format(html.escape(ET.tostring(n, encoding="unicode")))
            values[binding.get("name")] = value
        yield [values.get(header, "") for header in headers]


def json_row_iterator(obj):
    headers = obj["head"]["vars"]
    yield headers
    for binding in obj["results"]["bindings"]:
        row = []
        for header in headers:
            if header in binding:
                val = binding[header]
                if val["type"] == "uri":
                    row.append(f'&lt;{html.escape(val["value"])}&gt;')
                elif val["type"] in ("literal", "typed-literal"):
                    row.append(literal_text(val["value"], val.get("xml:lang"), val.get("datatype")))
                elif val["type"] == "bnode":
                    row.append(f'&lt;_:{html.escape(val["value"])}&gt;')
            else:
                row.append("")
        yield row


def graph_spo_iterator(graph):
    yield ["subject", "predicate", "object"]
    for s, p, o in graph:
        yield [s, p, o]


def html_table(row_iter):
    res = "<table>"
    res += html_table_row(next(row_iter), True)
    for row in row_iter:
        res += html_table_row(row)
    return res + "</table>"


def html_table_row(row, header=False):
    res = "<tr>"
    for cell in row:
        res += html_table_cell(cell, header)
    return res + "</tr>"


def html_table_cell(cell, header=False):
    # rows of local results hold rdflib terms (which subclass str), and None for an unbound
    # variable; the iterators over remote results deliver strings that are already escaped
    if cell is None:
        cell = ""
    elif isinstance(cell, Node) or not isinstance(cell, str):
        cell = html.escape(str(cell))
    if header:
        return "<th>{}</th>".format(cell)
    return "<td>{}</td>".format(cell)
