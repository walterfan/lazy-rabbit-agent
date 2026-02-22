# Configuration file for the Sphinx documentation builder.
# Project Knowledge Pack — Sphinx + MyST
# https://www.sphinx-doc.org/
# https://myst-parser.readthedocs.io/

import os

# -- Path setup ----------------------------------------------------------
# For linking to repo root (e.g. code paths in docs)
# sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))

# -- Project information -------------------------------------------------
project = 'Lazy Rabbit Agent — Project Knowledge Pack'
copyright = 'Walter Fan, CC-BY-NC-ND 4.0'
author = 'Walter Fan'
release = '1.0'

# -- General configuration -----------------------------------------------
extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.mermaid',
    'sphinxcontrib.plantuml',
]

# PlantUML: use 'plantuml' CLI if in PATH, or set to 'java -jar /path/to/plantuml.jar'
# For remote server, use a wrapper script that encodes and fetches from PlantUML server.
plantuml = 'plantuml'
plantuml_output_format = 'svg_img'
plantuml_cache_path = '_plantuml_cache'

# MyST: parse Markdown; tables, footnotes, linkify, etc.
# https://myst-parser.readthedocs.io/en/stable/syntax/optional.html
myst_enable_extensions = [
    'colon_fence',
    'deflist',
    'linkify',
    'tasklist',
]
myst_heading_anchors = 3

# Source suffixes: .md and .rst
source_suffix = {
    '.md': 'markdown',
    '.rst': 'restructuredtext',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_plantuml_cache']

# -- Options for HTML output ---------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_show_sphinx = False
