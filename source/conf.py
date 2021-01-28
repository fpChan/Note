

project = 'fpchen'
copyright = '2019, 方平'
author = '方平'

# The full version, including alpha/beta/rc tags
version = 'technology'
release = 'technology'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
   'sphinx_markdown_tables',
   'recommonmark',
   'sphinx.ext.mathjax'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"


from recommonmark.parser import CommonMarkParser

source_parsers = {
   '.md': 'CommonMarkParser',
}
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}
html_theme_options = {
    "light_css_variables": {
        "font-stack": "Arial, sans-serif",
        "font-stack--monospace": "Courier, monospace",
    },
}
