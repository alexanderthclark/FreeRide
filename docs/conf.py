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
    'myst_parser',
    'sphinx.ext.viewcode',  # Add source code links
    'sphinx.ext.githubpages',  # GitHub Pages optimization
    'sphinx_sitemap',  # Generate sitemap.xml for SEO
    'sphinxext.opengraph',  # OpenGraph meta tags for social sharing
    'sphinx_copybutton',  # Copy button for code blocks (UX improvement)
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

autodoc_mock_imports = ['IPython', 'pandas', 'numpy', 'matplotlib', 'bokeh']

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

# -- SEO Configuration -------------------------------------------------------

# Sitemap configuration
sitemap_url_scheme = "{link}"
html_baseurl = "https://alexanderthclark.github.io/FreeRide/"

# OpenGraph configuration for social media sharing
ogp_site_url = "https://alexanderthclark.github.io/FreeRide/"
ogp_site_name = "FreeRide - Python Package for Microeconomics Education"
ogp_description_length = 160
ogp_type = "website"
ogp_image = "https://alexanderthclark.github.io/FreeRide/_static/freeride-banner.png"
ogp_image_alt = "FreeRide Economics Package Banner"

# Additional HTML meta tags for SEO
html_meta = {
    'description': 'FreeRide: Python package for introductory microeconomics education. Create supply/demand curves, analyze market equilibrium, model game theory, and visualize economic concepts.',
    'keywords': 'microeconomics, economics education, python package, supply and demand, market equilibrium, game theory, monopoly analysis, policy analysis, economics python, undergraduate economics, Econ 101, economic modeling, educational software',
    'author': 'Alexander Clark',
    'robots': 'index, follow',
    'googlebot': 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1',
    'viewport': 'width=device-width, initial-scale=1.0',
    'theme-color': '#1a2332',
    'msapplication-TileColor': '#1a2332',
    'apple-mobile-web-app-capable': 'yes',
    'apple-mobile-web-app-status-bar-style': 'default',
}

# Copy button configuration
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_remove_prompts = True

# Language and locale for better SEO
language = 'en'
html_search_language = 'en'

# Last updated information
html_last_updated_fmt = '%Y-%m-%d'
