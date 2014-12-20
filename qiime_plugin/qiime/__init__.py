from importlib import import_module

from qiime import create_plugin

qiime = create_plugin("qiime",
                      "2.0.0-dev",
                      "QIIME development team",
                      "Quantitative Insights Into Microbial Ecology")

import_module('qiime.plugins.qiime.types')
import_module('qiime.plugins.qiime.methods')
