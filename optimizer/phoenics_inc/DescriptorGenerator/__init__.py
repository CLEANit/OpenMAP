#!/usr/bin/env 

__author__ = 'Florian Hase'

#========================================================================

import sys 

from utilities import PhoenicsModuleError, PhoenicsVersionError

#========================================================================

try:
	import tensorflow as tf
except ModuleNotFoundError:
	_, error_message, _ = sys.exc_info()
	extension = '\n\tAutomatic descriptor generation requires the tensorflow package. Please install tensorflow or disable automatic descriptor generation by setting auto_desc_gen="False".'
	PhoenicsModuleError(str(error_message) + extension)

#========================================================================

from DescriptorGenerator.descriptor_generator import DescriptorGenerator
