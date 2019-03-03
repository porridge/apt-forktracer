# apt-forktracer - a utility for managing package versions
# Copyright (C) 2008,2019 Marcin Owsiany <porridge@debian.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os

class _ConfigFinderIterator:
	"""Iterator class used by ConfigFinder. See that class for more information."""

	def __init__(self, cf):
		self.cf = cf
		self.index = 0
		self.file = None

	def __iter__(self):
		return self

	def __next__(self):
		if len(self.cf.paths) > self.index:
			path = self.cf.paths[self.index]
			if self.file:
				self.file.close()
			self.file = open(path)
			self.index += 1
			return (path, self.file)
		else:
			if self.file:
				self.file.close()
			raise StopIteration()

class ConfigFinder:
	"""Provides a method to get all config files. Arguments are files or
	directories to look for. Files are opened, and directories are searched
	looking for files which end with '.conf' but do not start with a dot.

	Iterating over this object returns tuples (path, file), where path is the
	path to a config file, and file is the open file object.
	"""

	def __init__(self, *paths):
		self.paths = []
		for path in paths:
			if not os.path.exists(path):
				continue
			if os.path.isdir(path):
				for name in os.listdir(path):
					if name and name[0] != '.' and name.endswith('.conf'):
						self.paths.append(os.path.join(path, name))
			else:
				self.paths.append(path)

	def __iter__(self):
		return _ConfigFinderIterator(self)

