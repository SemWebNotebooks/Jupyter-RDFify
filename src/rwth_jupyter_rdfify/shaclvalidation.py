from .rdf_module import RDFModule


class ShaclValidationModule(RDFModule):

    def __init__(self, name, parser, logger, description, displayname):
        super().__init__(name, parser, logger, description, displayname)
        self.parser.add_argument(
            "--data-graph", "-d", help="Reference the data graph to validate by label", required=True)
        self.parser.add_argument(
            "--shapes-graph", "-s", help="Reference the SHACL shapes graph by label", required=True)

    def check_label(self, label, store, label_type="graph"):
        """Verify that a graph label exists in the store."""
        if label is not None:
            if label in store["rdfgraphs"]:
                return True
            else:
                self.log(f"{label_type.capitalize()} labelled '{label}' not found.")
        else:
            self.log(
                f"Please specify the label of a {label_type} with the appropriate parameter.")
        return False

    def handle(self, params, store):
        """Execute SHACL validation on the data graph using the shapes graph."""
        try:
            from pyshacl import validate
        except ImportError:
            self.log("pyshacl is not installed. Install it with: pip install pyshacl")
            return

        # Check if both graphs exist
        if not self.check_label(params.data_graph, store, "data graph"):
            return
        if not self.check_label(params.shapes_graph, store, "shapes graph"):
            return

        data_graph = store["rdfgraphs"][params.data_graph]
        shapes_graph = store["rdfgraphs"][params.shapes_graph]

        try:
            # Execute SHACL validation
            conforms, report_graph, report_text = validate(
                data_graph,
                shacl_graph=shapes_graph,
                inference="rdfs",
                abort_on_first=False,
                allow_warnings=True,
                meta_shacl=False
            )

            # Format output based on validation result
            if conforms:
                # Success: Display green info box
                html_output = """
                <div style="background-color: #d4edda; border: 1px solid #c3e6cb;
                            padding: 12px; border-radius: 4px; color: #155724; margin: 8px 0;">
                    <strong style="font-size: 1.1em;">✓ SHACL Validation Passed</strong><br>
                    <span style="font-size: 0.95em;">The data graph conforms to the shapes graph.</span>
                </div>
                """
                self.logger.display_html(html_output)
            else:
                # Failure: Display red error box with violation details
                # Escape HTML in report text for safe display
                report_text_escaped = report_text.replace("<", "&lt;").replace(">", "&gt;")

                html_output = f"""
                <div style="background-color: #f8d7da; border: 1px solid #f5c6cb;
                            padding: 12px; border-radius: 4px; color: #721c24; margin: 8px 0;">
                    <strong style="font-size: 1.1em;">✗ SHACL Validation Failed</strong><br>
                    <span style="font-size: 0.95em;">The data graph does not conform to the shapes graph.</span>
                    <br><br>
                    <details style="margin-top: 8px;">
                        <summary style="cursor: pointer; font-weight: bold;">View Violation Details</summary>
                        <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 3px;
                                   overflow-x: auto; margin-top: 8px; font-size: 0.85em;">
{report_text_escaped}
                        </pre>
                    </details>
                </div>
                """
                self.logger.display_html(html_output)

                # Store the validation report for potential further analysis
                store["rdfgraphs"][f"validation_report_{params.data_graph}"] = report_graph

        except Exception as e:
            # Handle any errors during validation
            error_msg = str(e)
            error_msg_escaped = error_msg.replace("<", "&lt;").replace(">", "&gt;")

            html_output = f"""
            <div style="background-color: #f8d7da; border: 1px solid #f5c6cb;
                        padding: 12px; border-radius: 4px; color: #721c24; margin: 8px 0;">
                <strong style="font-size: 1.1em;">⚠ SHACL Validation Error</strong><br>
                <span style="font-size: 0.95em;">An error occurred during validation:</span>
                <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 3px;
                           overflow-x: auto; margin-top: 8px; font-size: 0.85em;">
{error_msg_escaped}
                </pre>
            </div>
            """
            self.logger.display_html(html_output)
