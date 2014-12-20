from importlib import import_module

from framework import create_plugin

qiime = create_plugin("qiime",
                      "2.0.0-dev",
                      "QIIME development team",
                      "Quantitative Insights Into Microbial Ecology")

import_module('qiime_plugin.types')
import_module('qiime_plugin.methods')
