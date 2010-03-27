#!/usr/bin/python
# apt-forktracer - a utility for managing package versions
# Copyright (C) 2008,2010 Marcin Owsiany <porridge@debian.org>
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
from apt_forktracer.config_finder import ConfigFinder

class Test_Config_Finder(test_helper.TestCase):
	def test(self):
		cf = ConfigFinder('test-data/config', 'test-data/not_exists', 'test-data/config.d')
		entries = 0
		plan = [
			('test-data/config', 4),
			('test-data/config.d/sub.conf', 0),
			('INVALID ENTRY to catch unexpected files', 0)
		]
		for path, file in cf:
			self.assertEquals(path, plan[entries][0])
			self.assert_(file.readlines() > plan[entries][1])
			entries += 1
		self.assertEquals(entries, 2)


if __name__ == '__main__':
	unittest.main()
