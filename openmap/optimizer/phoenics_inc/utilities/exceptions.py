#!/usr/bin/env python 

__author__ = 'Florian Hase'

#========================================================================

import sys
import traceback

#========================================================================

class AbstractError(object):

	def __init__(self, message):
		self.__call__(message)

	def __call__(self, message):
		error_traceback = traceback.format_exc()
		error_traceback = '\n'.join(error_traceback.split('\n')[:-2]) + '\n\n'
		error_type      = '\x1b[0;31m%s: %s\x1b[0m\n' % (self.name, message)

		if 'SystemExit' in error_traceback:	
			return None
		
		sys.stderr.write(error_traceback)
		sys.stderr.write(error_type)
		sys.exit()
	

class PhoenicsModuleError(AbstractError):
	name = 'PhoenicsModuleError'

class PhoenicsNotFoundError(AbstractError):
	name = 'PhoenicsNotFoundError'

class PhoenicsParseError(AbstractError):
	name = 'PhoenicsParseError'

class PhoenicsUnknownSettingsError(AbstractError):
	name = 'PhoenicsUnknownSettingsError'

class PhoenicsValueError(AbstractError):
	name = 'PhoenicsValueError'

class PhoenicsVersionError(AbstractError):
	name = 'PhoenicsVersionError'

