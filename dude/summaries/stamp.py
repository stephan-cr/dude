# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

import Filter

class Vacation(Filter.Filter):
	def splitAndSelect(self, line):
		return float(line.split('Time = ')[1])
	def getRegex(self):
		return '^Time = '
