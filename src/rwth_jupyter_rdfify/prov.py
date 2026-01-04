import rdflib
from prov.model import ProvDocument
from prov.dot import prov_to_dot
from IPython.display import Image
try:
    import prov.serializers.rdf
except ImportError:
    pass


def draw_provgraph(g, logger, shorten_uris=True, rename_blank_nodes=True):
    turtle_data = g.serialize(format='turtle')
    if isinstance(turtle_data, bytes):
        turtle_data = turtle_data.decode("utf-8")
    prov_doc = ProvDocument.deserialize(content=turtle_data, format='rdf', rdf_format='turtle')
    dot = prov_to_dot(prov_doc)
    image_data = dot.create(format='png')
    logger.out(Image(image_data))