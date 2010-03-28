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
from apt_forktracer.testlib.fake_package_file import FakePackageFile
from apt_forktracer.testlib.fake_version import FakeVersion
from apt_forktracer.status import Status
from apt_forktracer.version_adapter import VersionAdapter

class TestInstantiation(test_helper.MoxTestCase):
	def setUp(self):
		super(TestInstantiation, self).setUp()
		fv1 = FakeVersion()
		fv1.append_package_file(FakePackageFile())
		installed_version = VersionAdapter(fv1)
		fv2 = FakeVersion('1.2.4')
		fv2.append_package_file(FakePackageFile())
		candidate_version = VersionAdapter(fv2)
		self.versions_by_origin = {'Debian': [VersionAdapter(FakeVersion('foo'))], 'Another': [VersionAdapter(FakeVersion('bar')), VersionAdapter(FakeVersion('baz'))]}
		self.s = Status('foo', installed_version, candidate_version, self.versions_by_origin)
	def testCorrectness(self):
		self.assertEquals(self.s.package_name, 'foo')
		self.assertEquals(self.s.installed_version.string, '1.2.3')
		self.assertEquals(self.s.candidate_version.string, '1.2.4')
		installed_ver_pkgs = self.s.installed_version.files
		self.assertEquals(installed_ver_pkgs[0].origin, 'Debian')
		self.assertEquals(self.s.versions_from('Debian')[0].string, 'foo')
		self.assertEquals(self.s.versions_from('Another')[0].string, 'bar')
		self.assertEquals(self.s.versions_from('Another')[1].string, 'baz')
		self.assertEquals(self.s.versions_from('nowhere'), [])
		all = self.s.all_available_versions()
		self.assertEquals(len(all), 3)
		all_strings = [v.string for v in all]
		all_strings.sort()
		self.assert_('foo' in [v.string for v in all])
		self.assert_('bar' in [v.string for v in all])
	def testStringification(self):
		self.assertMatches(str(self.s), r'<Status foo .*1\.2\.3.*->.*1\.2\.4.*\[Debian: foo\]')
		self.assertMatches(str(self.s), r'<Status foo .*1\.2\.3.*->.*1\.2\.4.*\[Another: bar,baz\]')

class Test_Instantiation_Without_Official_Versions(test_helper.MoxTestCase):
	def setUp(self):
		super(Test_Instantiation_Without_Official_Versions, self).setUp()
		fv1 = FakeVersion('1.2.5')
		fv1.append_package_file(FakePackageFile())
		installed_version = VersionAdapter(fv1)
		fv2 = FakeVersion('1.2.6')
		fv2.append_package_file(FakePackageFile())
		candidate_version = VersionAdapter(fv2)
		self.versions_by_origin = {'NonDebian': [VersionAdapter(FakeVersion('foo'))]}
		self.s = Status('foo', installed_version, candidate_version, self.versions_by_origin)
	def testCorrectness(self):
		self.assertEquals(self.s.package_name, 'foo')
		self.assertEquals(self.s.installed_version.string, '1.2.5')
		self.assertEquals(self.s.candidate_version.string, '1.2.6')
		installed_ver_pkgs = self.s.installed_version.files
		self.assertEquals(installed_ver_pkgs[0].origin, 'Debian')
		self.assertEquals(self.s.versions_from('NonDebian')[0].string, 'foo')
		self.assertEquals(self.s.versions_from('nowhere'), [])
	def testStringification(self):
		self.assertMatches(str(self.s), r'<Status foo .*1\.2\.5.*->.*1\.2\.6.*')

if __name__ == '__main__':
	unittest.main()
