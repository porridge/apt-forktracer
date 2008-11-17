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

from apt_forktracer.config_stanza import ConfigStanza

class ConfigParser:
	"""Parses a text file, producing ConfigStanza objects."""

	def __add(self, stanza, lineno, ret, config):
		"""Private method for gathering stanzas."""	
		if not stanza.is_empty():
			ret.append(stanza.finish(lineno))
			if config:
				config.add(stanza)
			stanza = ConfigStanza()
		return stanza

	def load(self, file, config = None):
		"""Parses an open file object, and returns a list of stanzas found. If
		an optional config argument (a Config object) is provided, it also adds
		the stanzas to it.
		
		Parsing errors are raised as exceptions.
		"""
		ret = []
		stanza = ConfigStanza()
		lineno = 0
		for line in file:
			lineno += 1
			line = line.strip()
			if line == '':
				stanza = self.__add(stanza, lineno, ret, config)
				continue
			colon = line.find(':')
			if colon != -1:
				key, val = line.split(':', 1)
				stanza.set(key.strip(), val.strip(), lineno)
			else:
				raise ValueError('invalid line %d: %s' % (lineno, repr(line)))
		stanza = self.__add(stanza, lineno, ret, config)
		return ret
