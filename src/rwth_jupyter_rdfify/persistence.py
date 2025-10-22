import os
import rdflib
import requests
from pathlib import Path
from .rdf_module import RDFModule
from .util import StopCellExecution


class PersistenceModule(RDFModule):
    def __init__(self, name, parser, logger, description, displayname):
        super().__init__(name, parser, logger, description, displayname)
        self.parser.add_argument(
            "--load", "-l", help="Load an RDF graph from a local file path")
        self.parser.add_argument(
            "--download", "-d", help="Download an RDF graph from a remote URL")
        self.parser.add_argument(
            "--save", "-s", help="Save a graph to disk. Requires --label to specify which graph to save")
        self.parser.add_argument(
            "--label", help="Label to identify the graph (used for loading with --label or saving with --save)")
        self.parser.add_argument(
            "--format", "-f", choices=["turtle", "json-ld", "xml", "n3", "nt", "trig"],
            default="turtle", help="RDF format for the file")
        self.parser.add_argument(
            "--output", "-o", help="Output file path for --save operation")

    def handle(self, params, store):
        try:
            if params.load:
                self._load_from_file(params.load, params.label, params.format, store)
            elif params.download:
                self._download_from_url(params.download, params.label, params.format, store)
            elif params.save:
                self._save_to_file(params.label, params.output, params.format, store)
            else:
                self.log("Please specify --load, --download, or --save")
        except Exception as e:
            self.log(f"Error: {str(e)}")

    def _load_from_file(self, file_path, label, fmt, store):
        """Load an RDF graph from a local file."""
        try:
            path = Path(file_path)
            if not path.exists():
                self.log(f"File not found: {file_path}")
                return

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            g = rdflib.Graph().parse(data=content, format=fmt)
            g.source = lambda: f"file://{path.absolute()}"

            # Use provided label or derive from filename
            if label is None:
                label = path.stem

            store["rdfgraphs"][label] = g
            store["rdfsources"][label] = content
            store["rdfgraphs"]["last"] = g
            store["rdfsources"]["last"] = content

            self.log(f"Loaded graph from '{file_path}' with label '{label}' ({len(g)} triples)")
        except Exception as e:
            self.log(f"Failed to load file '{file_path}': {str(e)}")
            raise StopCellExecution

    def _download_from_url(self, url, label, fmt, store):
        """Download an RDF graph from a remote URL."""
        try:
            self.log(f"Downloading from {url}...")

            headers = {'Accept': self._get_accept_header(fmt)}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            content = response.text

            g = rdflib.Graph().parse(data=content, format=fmt)
            g.source = lambda: url

            # Use provided label or derive from URL
            if label is None:
                label = url.split('/')[-1].split('.')[0] or "downloaded"

            store["rdfgraphs"][label] = g
            store["rdfsources"][label] = content
            store["rdfgraphs"]["last"] = g
            store["rdfsources"]["last"] = content

            self.log(f"Downloaded graph from '{url}' with label '{label}' ({len(g)} triples)")
        except requests.RequestException as e:
            self.log(f"Failed to download from '{url}': {str(e)}")
            raise StopCellExecution
        except Exception as e:
            self.log(f"Failed to parse downloaded graph: {str(e)}")
            raise StopCellExecution

    def _save_to_file(self, label, output, fmt, store):
        """Save a graph to a local file."""
        try:
            if label is None:
                self.log("Please specify --label to identify which graph to save")
                return

            if label not in store["rdfgraphs"]:
                self.log(f"Graph with label '{label}' not found")
                return

            g = store["rdfgraphs"][label]

            # Generate output filename if not provided
            if output is None:
                ext = self._get_file_extension(fmt)
                output = f"{label}.{ext}"

            # Ensure directory exists
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Serialize and save
            serialized = g.serialize(format=fmt, encoding="utf-8")
            if isinstance(serialized, bytes):
                with open(output_path, 'wb') as f:
                    f.write(serialized)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(serialized)

            self.log(f"Saved graph '{label}' to '{output}' ({len(g)} triples)")
        except Exception as e:
            self.log(f"Failed to save graph: {str(e)}")
            raise StopCellExecution

    @staticmethod
    def _get_file_extension(fmt):
        """Get file extension for a given RDF format."""
        extensions = {
            'turtle': 'ttl',
            'xml': 'rdf',
            'json-ld': 'jsonld',
            'n3': 'n3',
            'nt': 'nt',
            'trig': 'trig',
        }
        return extensions.get(fmt, 'rdf')

    @staticmethod
    def _get_accept_header(fmt):
        """Get HTTP Accept header for content negotiation."""
        accept_types = {
            'turtle': 'text/turtle',
            'xml': 'application/rdf+xml',
            'json-ld': 'application/ld+json',
            'n3': 'text/n3',
            'nt': 'application/n-triples',
            'trig': 'application/trig',
        }
        return accept_types.get(fmt, 'application/rdf+xml')
