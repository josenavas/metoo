from qiime import create_plugin
from importlib import import_module

qiime = create_plugin("qiime",
                      "2.0.0-dev",
                      "qiime development group",
                      "Quantitative Insights Into Many Environments")

import_module('qiime.plugins.test_plugin')

different = create_plugin("differentplugin", "", "", "")

create_plugin("somany", "", "", "")
create_plugin("picrust", "", "", "")
create_plugin("mothur", "", "", "")
