# apt-forktracer - a utility for managing package versions
# Copyright (C) 2008 Marcin Owsiany <porridge@debian.org>
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

class Config:
	"""Encapsulates config file information."""
	def __init__(self):
		self._stanzas = []
		self._package_map = {}

	def add(self, stanza):
		"""Adds a given stanza for later retrieval."""
		self._stanzas.append(stanza)
		name = stanza.get('package')
		if self._package_map.has_key(name):
			self._package_map[name].append(stanza)
		else:
			self._package_map[name] = [ stanza ]

	def package(self, package_name):
		"""Returns a (potentially empty) list of all stanzas for the given
		package name."""
		if self._package_map.has_key(package_name):
			return self._package_map[package_name]
		else:
			return []
