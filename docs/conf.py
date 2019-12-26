import os
import sys
from recommonmark.transform import AutoStructify


project = 'Generi'
copyright = '2019, Nick Lehmann'
author = 'Nick Lehmann'

release = '0.1.0'

extensions = [
    'recommonmark'
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = []
html_theme = 'alabaster'
# html_static_path = ['_static']

GITHUB_DOC_ROOT = 'https://github.com/nick-lehmann/generi/tree/master/doc/'
sys.path.insert(0, os.path.abspath('.'))


def setup(app):
    app.add_config_value('recommonmark_config', {
            'url_resolver': lambda url: GITHUB_DOC_ROOT + url,
            'auto_toc_tree_section': 'Contents',
            'enable_eval_rst': True
            }, True)
    app.add_transform(AutoStructify)

