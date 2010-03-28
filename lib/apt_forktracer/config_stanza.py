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

class ConfigStanza:
	"""Represents a single stanza in a configuration file, such as:

	Package: foo
	Accept-Origin: O1
	Track-Origin: O2
	Track-Version: 1.2.3

	Tags are on the left of the colons, and their values on the right.
	"""

	def __init__(self):
		self._dict = {}

	def finish(self, lineno):
		"""Should be called when parser has reached the end of the stanza. Does
		some integrity checks to make sure the stanza is correct. Any errors
		are raised as exceptions. lineno is the line number on which the stanza
		finished - it is used in the error messages.

		Returns the stanza itself.
		"""
		for tag in ['package', 'accept-origin', 'track-origin', 'track-version']:
			if not self._dict.has_key(tag):
				raise ValueError('invalid configuration stanza near line %d (missing field %s)' % (lineno, tag))
		return self

	def set(self, tag, value, lineno):
		"""Sets the value of the given tag (overriding any previously set one).
		Parameter lineno is used in case of an error message. Tag parameter is
		case-insensitive."""
		tag = tag.lower()
		if tag not in ['package', 'accept-origin', 'track-origin', 'track-version']:
			raise ValueError('invalid tag %s on line %d' % (tag, lineno))
		self._dict[tag] = value

	def is_empty(self):
		"""Returns True if nothing had been set on this stanza."""
		return len(self._dict) == 0

	def get(self, tag):
		"""Returns the most-recent set value of the given (case-insensitive) tag."""
		return self._dict[tag]

	def matches(self, tag, value):
		"""Returns True if the currently set value of the given tag is '*' or
		equal to the value parameter."""
		current_value = self.get(tag)
		if current_value == '*':
			return True
		else:
			return current_value == value

