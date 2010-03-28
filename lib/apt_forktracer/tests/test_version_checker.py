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
from apt_forktracer.testlib.fake_package import FakePackage
from apt_forktracer.testlib.fake_version import FakeVersion
from apt_forktracer.version_adapter import VersionAdapter
from apt_forktracer.version_checker import VersionChecker

class VersionCheckerTest(test_helper.MoxTestCase):
	def setUp(self):
		super(VersionCheckerTest, self).setUp()
		self.fp = FakePackage()
		self.facter = self._create_mock_facter('Debian')
		self.setUpChecker()
	def setUpChecker(self):
		self.vchecker = VersionChecker(self.facter)
	def test_analyze_version_without_sources_returns_true(self):
		v = VersionAdapter(FakeVersion._create('1.2.3', []))
		self.assert_(self.vchecker.analyze(v))
	def test_analyze_version_only_in_dpkg_status_file_returns_true(self):
		v = VersionAdapter(FakeVersion._create('1.2.3', ['dpkg']))
		self.assert_(self.vchecker.analyze(v))
	def test_analyze_version_in_dpkg_status_file_and_unofficial_source_returns_true(self):
		v = VersionAdapter(FakeVersion._create('1.2.3', ['dpkg', 'NonDebian']))
		self.assert_(self.vchecker.analyze(v))
	def test_analyze_version_in_dpkg_status_file_and_official_source_returns_false(self):
		v = VersionAdapter(FakeVersion._create('1.2.3', ['dpkg', 'Debian']))
		self.assert_(not self.vchecker.analyze(v))
	def test_analyze_version_in_dpkg_status_file_and_both_official_and_unofficial_source_returns_false(self):
		v = VersionAdapter(FakeVersion._create('1.2.3', ['dpkg', 'Debian', 'NonDebian']))
		self.assert_(not self.vchecker.analyze(v))

if __name__ == '__main__':
	unittest.main()
