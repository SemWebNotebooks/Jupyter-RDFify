from IPython.display import HTML
import xml.etree.ElementTree as ET
from .graph import parse_graph
import json


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
        row = []
        for binding in result.findall("sparql:binding", ns):
            n = binding[0]
            if n.tag == "{http://www.w3.org/2005/sparql-results#}literal":
                lang = n.get("{http://www.w3.org/XML/1998/namespace}lang")
                datatype = n.get(
                    "datatype")
                literal = n.text
                if lang is not None:
                    literal += "@{}".format(lang)
                if datatype is not None:
                    literal += "^^{}".format(datatype)
                row.append(literal)
            elif n.tag == "{http://www.w3.org/2005/sparql-results#}uri":
                row.append("&lt;{}&gt;".format(n.text))
            elif n.tag == "{http://www.w3.org/2005/sparql-results#}bnode":
                row.append("&lt;_:{}&gt;".format(n.text))
            else:
                row.append("Unknown node: {}".format(ET.tostring(n)))
        yield row


def json_row_iterator(obj):
    headers = obj["head"]["vars"]
    yield headers
    for binding in obj["results"]["bindings"]:
        row = []
        for header in headers:
            if header in binding:
                val = binding[header]
                if val["type"] == "uri":
                    row.append(f'&lt;{val["value"]}&gt;')
                elif val["type"] == "literal":
                    suff = ""
                    if "xml:lang" in val:
                        suff += f'@{val["xml:lang"]}'
                    if "datatype" in val:
                        suff += f'^^{val["datatype"]}'
                    row.append(val["value"] + suff)
                elif val["type"] == "bnode":
                    row.append(f'&lt;_:{val["value"]}&gt;')
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
    if header:
        return "<th>{}</th>".format(cell)
    return "<td>{}</td>".format(cell)
