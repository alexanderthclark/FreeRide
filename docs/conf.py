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
    with open("../freeride/__init__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1].strip())


project = 'FreeRide'
copyright = '2023, Alexander Clark'
author = 'Alexander Clark'
release = get_version()

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',  # Generate docs from docstrings
    'sphinx.ext.napoleon',  # Support for NumPy and Google style docstrings
    'sphinx.ext.mathjax',
    'myst_parser'
]

source_suffix = ['.rst', '.md']

autodoc_default_options = {
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_mock_imports = ['IPython', 'pandas', 'numpy', 'matplotlib', 'papermill', 'bokeh']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

# Custom CSS and JavaScript
html_css_files = [
    'custom.css',
]

html_js_files = [
    'custom.js',
]

# Theme options for sphinx-book-theme
html_theme_options = {
    "repository_url": "https://github.com/alexanderthclark/FreeRide",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "path_to_docs": "docs",
    "home_page_in_toc": True,
    "show_navbar_depth": 2,
    "show_toc_level": 2,
    "logo": {
        "image_light": "_static/logo.svg",
        "image_dark": "_static/logo.svg",
        "text": "FreeRide",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/alexanderthclark/FreeRide",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/freeride/",
            "icon": "fa-brands fa-python",
        },
    ],
    # Color customization through theme
    "primary_sidebar_end": ["indices.html"],
    "footer_content_items": ["copyright", "last-updated"],
    # Remove right sidebar for more content space
    "show_toc_level": 0,  # This removes the right table of contents
    "use_sidenotes": False,
}

# Add custom HTML title
html_title = "FreeRide"

# Favicon
html_favicon = "_static/favicon.svg"
