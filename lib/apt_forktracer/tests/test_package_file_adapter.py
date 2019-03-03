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
from apt_forktracer.package_file_adapter import PackageFileAdapter

class BasePFATest(test_helper.MoxTestCase):
	def setUpPF(self):
		self.fake_package_file = FakePackageFile()
	def setUp(self):
		super(BasePFATest, self).setUp()
		self.setUpPF()
		self.pfa = PackageFileAdapter(self.fake_package_file)
		self.mock_debian_facter = self._create_mock_facter('Debian')
		self.mock_ubuntu_facter = self._create_mock_facter('Ubuntu')

class BasePFATestWithOfficial(BasePFATest):
	def testIsOfficialTrue(self):
		self.assertTrue(self.pfa.is_official(self.mock_debian_facter))
	def testIsOfficialFalse(self):
		self.assertTrue(not self.pfa.is_official(self.mock_ubuntu_facter))

class TestBasePackageFileAdapter(BasePFATestWithOfficial):
	def testAttributes(self):
		self.assertEqual(self.pfa.name, '/a/fake')
		self.assertEqual(self.pfa.archive, 'stable-proposed-updates')
		self.assertEqual(self.pfa.component, 'main')
		self.assertEqual(self.pfa.version, '1.0')
		self.assertEqual(self.pfa.origin, 'Debian')
		self.assertEqual(self.pfa.label, 'Debian')
		self.assertEqual(self.pfa.not_automatic, 0)
		self.assertEqual(self.pfa.index_type, 'Debian Package Index')
	def testStringification(self):
		self.assertMatches(str(self.pfa), '<PackageFileAdapter path=/a/fake a=stable-proposed-updates c=main v=1.0 o=Debian l=Debian>')

class TestBasePackageFileAdapterNonAuto(BasePFATestWithOfficial):
	def setUpPF(self):
		BasePFATest.setUpPF(self)
		self.fake_package_file.not_automatic = 1
	def testAttributes(self):
		self.assertEqual(self.pfa.name, '/a/fake')
		self.assertEqual(self.pfa.archive, 'stable-proposed-updates')
		self.assertEqual(self.pfa.component, 'main')
		self.assertEqual(self.pfa.version, '1.0')
		self.assertEqual(self.pfa.origin, 'Debian')
		self.assertEqual(self.pfa.label, 'Debian')
		self.assertEqual(self.pfa.not_automatic, 1)
		self.assertEqual(self.pfa.index_type, 'Debian Package Index')
	def testStringification(self):
		self.assertMatches(str(self.pfa), '<PackageFileAdapter path=/a/fake a=stable-proposed-updates c=main v=1.0 o=Debian l=Debian NONAUTO>')

class TestBasePackageFileAdapterDpkgStatus(BasePFATest):
	def setUpPF(self):
		self.fake_package_file = FakePackageFile(type = 'dpkg')
	def testAttributes(self):
		self.assertEqual(self.pfa.name, '/var/lib/dpkg/status')
		self.assertEqual(self.pfa.index_type, 'Debian dpkg status file')
	def testStringification(self):
		self.assertMatches(str(self.pfa), '<PackageFileAdapter\(dpkg status\) path=/var/lib/dpkg/status>')
	def testIsOfficialFalse(self):
		self.assertTrue(not self.pfa.is_official(self.mock_debian_facter))
		self.assertTrue(not self.pfa.is_official(self.mock_ubuntu_facter))

if __name__ == '__main__':
	unittest.main()
