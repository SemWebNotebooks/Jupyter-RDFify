import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jupyter-rdfify",
    version="1.0.2",
    author="Lars Pieschel",
    author_email="lars.pieschel@rwth-aachen.de",
    description="IPython Extension for semantic web technology support (Turtle, SPARQL, ShEx, etc.)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SemWebNotebooks/Jupyter-RDFify",
    packages=setuptools.find_packages(),
    install_requires=[
        "rdflib",
        "rdflib-jsonld",
        "ipython>=7.0.0",
        "graphviz",
        "sparqlwrapper",
        "owlrl",
        "PyShEx"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: IPython",
    ],
    python_requires='>=3.6',
)
