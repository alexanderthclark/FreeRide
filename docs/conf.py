import os
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------


def get_version():
    with open("../microecon/__init__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1].strip())


project = 'Microecon'
copyright = '2023, Alexander Clark'
author = 'Alexander Clark'
release = get_version()

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',  # Generate docs from docstrings
    'sphinx.ext.napoleon',  # Support for NumPy and Google style docstrings
    'sphinx.ext.mathjax',
]

autodoc_default_options = {
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_mock_imports = ['IPython', 'pandas', 'numpy', 'matplotlib']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
