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
from apt_forktracer.testlib.fake_package_file import FakePackageFile
from apt_forktracer.testlib.fake_version import FakeVersion
from apt_forktracer.version_adapter import VersionAdapter

class TestBaseVersionAdapter(test_helper.MoxTestCase):
	def setUp(self):
		super(TestBaseVersionAdapter, self).setUp()
		self.setUpFakeVersion()
		self.setUpVersionAdapter()
	def setUpFakeVersion(self):
		self.fake_version = FakeVersion()
	def setUpVersionAdapter(self):
		self.va = VersionAdapter(self.fake_version)
	def testString(self):
		self.assertEqual(self.va.string, '1.2.3')
	def testBasicStringification(self):
		self.assertMatches(str(self.va), r'<VersionAdapter 1.2.3')
	def setUpAddAFile(self):
		self.fake_version.append_package_file(FakePackageFile(path = '/b/lah'))

class TestVersionOfficiallyAvailable(test_helper.MoxTestCase):
	"""Testing the is_officially_available() method."""
	def setUp(self):
		super(TestVersionOfficiallyAvailable, self).setUp()
		self.mock_apt_version = self.struct()
		self.mock_apt_version.ver_str = '1.2.3'
		self.mock_apt_version.file_list = [(FakePackageFile(type = 'dpkg'), 1)]
		self.mock_facter = self._create_mock_facter('Debian')
	def assertVersionIsOfficiallyAvailable(self):
		self.assertTrue(VersionAdapter(self.mock_apt_version).is_officially_available(self.mock_facter))
	def assertVersionIsNotOfficiallyAvailable(self):
		self.assertTrue(not VersionAdapter(self.mock_apt_version).is_officially_available(self.mock_facter))
	def testVersionNotAvailableApartFromInstalled(self):
		self.assertVersionIsNotOfficiallyAvailable()
	def testVersionAvailableFromUnofficialPackageFile(self):
		self.mock_apt_version.file_list.append((FakePackageFile(type = 'normal', origin = 'Unofficial'), 2))
		self.assertVersionIsNotOfficiallyAvailable()
	def testVersionAvailableFromOfficialPackageFile(self):
		self.mock_apt_version.file_list.append((FakePackageFile(type = 'normal', origin = 'Debian'), 2))
		self.assertVersionIsOfficiallyAvailable()
	def testVersionAvailableFromBothOfficialAndUnofficialPackageFiles(self):
		self.mock_apt_version.file_list.append((FakePackageFile(type = 'normal', origin = 'Debian'), 2))
		self.mock_apt_version.file_list.append((FakePackageFile(type = 'normal', origin = 'Unofficial'), 1))
		self.assertVersionIsOfficiallyAvailable()

class TestZeroFileVersionAdapter(TestBaseVersionAdapter):
	def testFileCount(self):
		self.assertEqual(len(self.va.files), 0)
	def testStringification(self):
		self.assertMatches(str(self.va), r'<VersionAdapter 1.2.3 \[\]>')

class TestOneFileVersionAdapter(TestBaseVersionAdapter):
	def setUp(self):
		super(TestOneFileVersionAdapter, self).setUp()
		self.setUpFakeVersion()
		self.setUpAddAFile()
		self.setUpVersionAdapter()
	def testFileCount(self):
		self.assertEqual(len(self.va.files), 1)
		self.assertEqual(self.va.files[0].name, '/b/lah')
	def testStringification(self):
		self.assertMatches(str(self.va), r'<VersionAdapter 1.2.3 \[.*/b/lah.*\]>')

class TestThreeFilesVersionAdapter(TestBaseVersionAdapter):
	def setUp(self):
		super(TestThreeFilesVersionAdapter, self).setUp()
		self.setUpFakeVersion()
		for i in range(3):
			self.setUpAddAFile()
		self.setUpVersionAdapter()
	def testThreeFiles(self):
		self.assertEqual(len(self.va.files), 3)
	def testStringification(self):
		self.assertMatches(str(self.va), r'<VersionAdapter 1.2.3 \[.*/b/lah.*/b/lah.*/b/lah.*\]>')

if __name__ == '__main__':
	unittest.main()
