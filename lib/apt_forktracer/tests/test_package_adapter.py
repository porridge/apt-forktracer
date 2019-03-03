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
from apt_forktracer.apt_pkg_adapter import AptPkgAdapter
from apt_forktracer.testlib.fake_package import FakePackage
from apt_forktracer.testlib.fake_version import FakeVersion
from apt_forktracer.package_adapter import PackageAdapter

class TestBasePackageAdapter(test_helper.MoxTestCase):
	def setUp(self):
		super(TestBasePackageAdapter, self).setUp()
		self.fake_package = FakePackage()
		self.setUp_mangle_fake_package()
		self.pa = PackageAdapter(self.fake_package)
		self.setUp_mangle_package_adapter()
		self.facter = self._create_mock_facter('Debian')
		self.apt_pkg_adapter = AptPkgAdapter(self._create_mock_apt_pkg_module())
		self.apt_pkg_adapter.init()
		self.status = self.pa.get_status(self.facter)
	def setUp_mangle_fake_package(self):
		pass
	def setUp_mangle_package_adapter(self):
		pass
	def testProperties(self):
		self.assertEqual(self.pa.name, 'afake')
		self.assertEqual(self.pa.apt_package, self.fake_package)
	def testLenOfVersionsNonNegative(self):
		self.assertTrue(len(self.pa.versions) >= 0)
	def testBasicStringificationWorks(self):
		self.assertContains(str(self.pa), 'PackageAdapter')
	def setUpAddAVersion(self, source = 'NonDebian', version = 'blah'):
		self.fake_package.append_version(FakeVersion._create(version, [source]))
	def test_get_status_returns_an_object(self):
		self.assertTrue(self.status)
		self.assertEqual(self.status.package_name, 'afake')
		self.assertEqual(self.status.installed_version, self.pa.current_version)
		self.assertEqual(self.status.candidate_version, self.pa.candidate_version)
		self.assertTrue(len(self.status.versions_by_origin) >= 0)

class TestZeroVersionPackageAdapter(TestBasePackageAdapter):
	def testEmptyVersions(self):
		self.assertEqual(self.pa.versions, [])
		self.assertEqual(len(self.status.versions_by_origin), 0)
	def testStringificationWorks(self):
		self.assertContains(str(self.pa), 'v=None->None')

class TestOneOfficialVersionPackageAdapter(TestBasePackageAdapter):
	def setUp_mangle_fake_package(self):
		self.setUpAddAVersion('Debian')
	def testOneVersion(self):
		self.assertEqual(len(self.pa.versions), 1)
		self.assertEqual(len(self.status.versions_by_origin), 1)

class TestOneUnofficialVersionPackageAdapter(TestBasePackageAdapter):
	def setUp_mangle_fake_package(self):
		self.setUpAddAVersion()
	def testOneVersion(self):
		self.assertEqual(len(self.pa.versions), 1)
		self.assertEqual(len(self.status.versions_by_origin), 1)

class TestFourVersionPackageAdapter(TestBasePackageAdapter):
	def setUp_mangle_fake_package(self):
		self.setUpAddAVersion('NonDebian', '0')
		self.setUpAddAVersion('NonDebian', '4')
		self.setUpAddAVersion('Debian', '1')
		self.setUpAddAVersion('Debian', '2')
		self.setUpAddAVersion('dpkg', '5')
	def testFourVersions(self):
		self.assertEqual(len(self.pa.versions), 5)
		self.assertEqual(len(self.status.versions_by_origin), 2)
		self.assertEqual(len(self.status.versions_by_origin['Debian']), 2)
		self.assertEqual(len(self.status.versions_by_origin['NonDebian']), 2)

class TestPackageAdapterWithInstalledVersion(TestBasePackageAdapter):
	def setUp_mangle_fake_package(self):
		self.setUpAddAVersion()
		self.fake_package.current_ver = FakeVersion('1.xx.yy')
		self.official_version = FakeVersion._create('2.3.4', ['Debian'])
		self.fake_package.append_version(self.official_version)
	def setUp_mangle_package_adapter(self):
		self.pa.candidate_version = '2.3.4'
	def test_versions(self):
		self.assertEqual(self.pa.current_version.string, '1.xx.yy')
		self.assertEqual(len(self.status.versions_by_origin), 2)
	def testStringificationWorks(self):
		self.assertMatches(str(self.pa), r'VersionAdapter.*1\.xx\.yy.*->2\.3\.4')

if __name__ == '__main__':
	unittest.main()
