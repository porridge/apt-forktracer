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
import mox
import unittest

from apt_forktracer.testlib import test_helper
from apt_forktracer.testlib.fake_package import FakePackage
from apt_forktracer.testlib.fake_package_file import FakePackageFile
from apt_forktracer.testlib.fake_version import FakeVersion
from apt_forktracer.depcache_adapter import DepCacheAdapter
from apt_forktracer.package_adapter import PackageAdapter,PackageAdapterFactory
from apt_forktracer.version_adapter import VersionAdapter

class Test_Package_And_Version_Reading(test_helper.MoxTestCase):
	def setUp(self):
		super(Test_Package_And_Version_Reading, self).setUp()
		self.fake = FakePackage()
		v1 = FakeVersion()
		v1.VerStr = '1.2.3'
		v1.append_package_file(FakePackageFile())
		fpf = FakePackageFile()
		fpf.NotAutomatic = 1
		v1.append_package_file(fpf)
		v2 = FakeVersion()
		v2.VerStr = '4.5.6'
		self.fake.VersionList.append(v1)
		self.fake.VersionList.append(v2)
		self.fake.CurrentVer = v1
		self.set_up_package_adapter_and_replay_all()
	def set_up_package_adapter_and_replay_all(self):
		self.mox.ReplayAll()
		self.p = PackageAdapter(self.fake)
	def testPackageAndVersionsReadCorrectly(self):
		self.assertEquals(self.p.name, 'afake')
		self.assertEquals(len(self.p.versions), 2)
		v1 = self.p.versions[0]
		self.assertEquals(v1.string, '1.2.3')
		self.assertEquals(len(v1.files), 2)
		v1pf0 = v1.files[0]
		self.assertEquals(v1pf0.name, '/a/fake')
		v1pf1 = v1.files[1]
		self.assert_(v1pf1.not_automatic)
		v2 = self.p.versions[1]
		self.assertEquals(v2.string, '4.5.6')
	def testStringificationWorks(self):
		s = str(self.p)
		self.assertContains(s, 'PackageAdapter')
		self.assertContains(s, ' afake ')
		self.assertMatches(s, 'v=<.*1.2.3.*->')
		vs = str(self.p.versions[0])
		self.assertContains(vs, 'VersionAdapter')
		self.assertContains(vs, '1.2.3')
		vpfs = str(self.p.versions[0].files[0])
		self.assertContains(vpfs, 'PackageFileAdapter')
		self.assertContains(vpfs, 'path=/a/fake')
		self.assertContains(vpfs, 'a=stable-proposed-updates')
		self.assertContains(vpfs, 'c=main')
		self.assertContains(vpfs, 'v=1.0')
		self.assertContains(vpfs, 'o=Debian')
		self.assertContains(vpfs, 'l=Debian')
		self.assertNotContains(vpfs, 'NONAUTO')
		vpfs2 = str(self.p.versions[0].files[1])
		self.assertContains(vpfs2, 'NONAUTO')

class Test_With_Factory_Creation(Test_Package_And_Version_Reading):
	def set_up_package_adapter_and_replay_all(self):
		self.mox.ReplayAll()
		self.p = PackageAdapterFactory().create_package_adapter(self.fake)

class Test_With_Factory_Creation_With_Candidate(Test_Package_And_Version_Reading):
	def set_up_package_adapter_and_replay_all(self):
		mock_depcache_adapter = self.mox.CreateMock(DepCacheAdapter)
		self.va = VersionAdapter(FakeVersion._create('1.2.4', []))
		mock_depcache_adapter.get_candidate_version(mox.Func(lambda pa: pa.name == 'afake')).AndReturn(self.va)
		self.mox.ReplayAll()

		self.p = PackageAdapterFactory(mock_depcache_adapter).create_package_adapter(self.fake)
	def test_candidate_version(self):
		self.assertEquals(self.p.candidate_version, self.va)
		s = str(self.p)
		self.assertMatches(s, 'v=<.*1.2.3.*->.*<.*1.2.4')

if __name__ == '__main__':
	unittest.main()
