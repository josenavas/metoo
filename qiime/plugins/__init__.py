from qiime import create_plugin
from importlib import import_module

qiime = create_plugin("qiime",
					  "2.0.0-dev",
					  "qiime developement group",
					  "Quantitative Insights Into Many Environments")

import_module('qiime.plugins.test_plugin')
