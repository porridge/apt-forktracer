#!/usr/bin/python3
# apt-forktracer - a utility for managing package versions
# Copyright (C) 2008,2010,2019 Marcin Owsiany <porridge@debian.org>
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
import unittest

from apt_forktracer.testlib import test_helper
from apt_forktracer.config_stanza import ConfigStanza

class Test_ConfigStanza(test_helper.MoxTestCase):
	def setUp(self):
		super(Test_ConfigStanza, self).setUp()
		self.cs = ConfigStanza()
		self.assertTrue(self.cs.is_empty())
	def test_empty(self):
		self.assertRaisesWithMessageContaining(ValueError, 'line 2', self.cs.finish, 2)
	def test_all_attributes(self):
		self.cs.set('Package', 'dpkg', 2)
		self.assertTrue(not self.cs.is_empty())
		self.cs.set('Accept-Origin', 'NonDebian Stuff', 3)
		self.cs.set('Track-oriGIN', 'Debian', 4)
		self.cs.set('track-version', '1.2.3', 5)
		self.assertEqual(self.cs.get('package'), 'dpkg')
		self.assertEqual(self.cs.get('accept-origin'), 'NonDebian Stuff')
		self.assertTrue(self.cs.matches('accept-origin', 'NonDebian Stuff'))
		self.assertTrue(not self.cs.matches('accept-origin', 'Debian'))
		self.assertEqual(self.cs.get('track-origin'), 'Debian')
		self.assertEqual(self.cs.get('track-version'), '1.2.3')
		self.assertTrue(not self.cs.is_empty())
		self.assertEqual(self.cs.finish(6), self.cs)
	def test_invalid_attribute(self):
		self.assertRaisesWithMessageContaining(ValueError, 'invalid tag', self.cs.set, 'FoO', 'bar', 2)
		self.assertRaisesWithMessageContaining(ValueError, 'line 2', self.cs.set, 'FoO', 'bar', 2)
	def test_wildcard_attributes(self):
		self.cs.set('Package', 'dpkg', 2)
		self.assertTrue(not self.cs.is_empty())
		self.cs.set('Accept-Origin', '*', 3)
		self.cs.set('Track-oriGIN', '*', 4)
		self.cs.set('track-version', '1.2.3', 5)
		self.assertEqual(self.cs.get('accept-origin'), '*')
		self.assertTrue(self.cs.matches('accept-origin', 'whatever'))
		self.assertEqual(self.cs.get('track-origin'), '*')
		self.assertTrue(self.cs.matches('track-origin', 'whatever'))
		self.assertTrue(not self.cs.is_empty())
		self.assertEqual(self.cs.finish(6), self.cs)

if __name__ == '__main__':
	unittest.main()
