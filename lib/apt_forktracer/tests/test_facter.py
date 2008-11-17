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

from apt_forktracer.facter import Facter

class TestFacterWithoutArgs(unittest.TestCase):
	def setUp(self):
		self.facter = Facter()
	def testDistributorsIdReturnsSomething(self):
		self.assert_(self.facter.distributors_id)

class TestFacterWithLSBReleaseArg(unittest.TestCase):
	def setUp(self):
		self.facter = Facter(lsb_release = 'echo Foobar')
	def testDistributorsIdReturnsFoobar(self):
		self.assertEquals(self.facter.distributors_id, 'Foobar')

class TestFacterWithBrokenLSBReleaseArgAndValidFileArg(unittest.TestCase):
	def setUp(self):
		self.facter = Facter(lsb_release = 'false', file = 'test-data/lsb-release')
	def testDistributorsIdReturnsUbuntu(self):
		self.assertEquals(self.facter.distributors_id, 'Ubuntu')

class TestFacterReadFirstWord(unittest.TestCase):
	def setUp(self):
		self.facter = Facter()
	def testUsualIssueFile(self):
		self.assertEquals(self.facter.get_distrib_id_from_file('test-data/lsb-release'), 'Ubuntu')
	def testEmptyFile(self):
		self.assertEquals(self.facter.get_distrib_id_from_file('test-data/empty'), None)
	def testMissingFile(self):
		self.assertEquals(self.facter.get_distrib_id_from_file('test-data/does_not_exist'), None)

if __name__ == '__main__':
	unittest.main()
