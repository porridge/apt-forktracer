#!/usr/bin/python
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
import pmock
import unittest

from apt_forktracer.testlib import test_helper
from apt_forktracer.config_parser import ConfigParser

class Test_ConfigParser(test_helper.TestCase):
	def setUp(self):
		self.cp = ConfigParser()
		self.c = self.mock()
	def test_loading_empty_file(self):
		self.c.expects(pmock.never()).method("add")
		self.assertEquals(self.cp.load([], self.c), [])
	def test_loading_invalid_syntax_file(self):
		fake_file = ['\n', 'invalid line\n']
		self.assertRaisesWithMessageContaining(Exception, 'line 2', self.cp.load, fake_file)
	def test_loading_invalid_stanza_file(self):
		fake_file = ['\n', 'package:val\n', 'acCepT-OrigiN: val2\n']
		self.assertRaisesWithMessageContaining(Exception, 'line 3', self.cp.load, fake_file)
	def test_loading_valid_file(self):
		fake_file = ['\n', 'package:val\n', 'acCepT-OrigiN: val2\n', ' track-oriGin : a  spaced val \n', 'track-version:foo']
		self.c.expects(pmock.once()).add(pmock.functor(lambda stanza: stanza.get('package') == 'val'))
		ret = self.cp.load(fake_file, self.c)
		self.assertEquals(len(ret), 1)
		self.assertEquals(ret[0].get('package'), 'val')

if __name__ == '__main__':
	unittest.main()
