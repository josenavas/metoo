import os
from importlib import import_module

def init():
	load_plugins()

def load_plugins():
	import_module('qiime.plugins')
