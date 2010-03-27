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
import unittest

from apt_forktracer.testlib import test_helper
from apt_forktracer.config import Config
from apt_forktracer.config_stanza import ConfigStanza

class Test_Config(test_helper.MoxTestCase):
	def setUp(self):
		super(Test_Config, self).setUp()
		self.c = Config()
	def test_addition_and_retrieval(self):
		foo_stanza1 = self.mox.CreateMock(ConfigStanza)
		foo_stanza1.get('package').AndReturn('foo')
		foo_stanza2 = self.mox.CreateMock(ConfigStanza)
		foo_stanza2.get('package').AndReturn('foo')
		bar_stanza = self.mox.CreateMock(ConfigStanza)
		bar_stanza.get('package').AndReturn('bar')
		self.mox.ReplayAll()

		self.c.add(foo_stanza1)
		self.c.add(foo_stanza2)
		self.c.add(bar_stanza)
		foo_stanzas = self.c.package('foo')
		bar_stanzas = self.c.package('bar')
		baz_stanzas = self.c.package('baz')
		self.assertEquals(len(foo_stanzas), 2)
		self.assertEquals(foo_stanzas[0], foo_stanza1)
		self.assertEquals(foo_stanzas[1], foo_stanza2)
		self.assertEquals(len(bar_stanzas), 1)
		self.assertEquals(bar_stanzas[0], bar_stanza)
		self.assertEquals(len(baz_stanzas), 0)


if __name__ == '__main__':
	unittest.main()
