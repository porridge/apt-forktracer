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
from apt_forktracer.depcache_adapter import DepCacheAdapterFactory
from apt_forktracer.package_adapter import PackageAdapter
from apt_forktracer.testlib.fake_package import FakePackage
from apt_forktracer.testlib.fake_package_file import FakePackageFile
from apt_forktracer.testlib.fake_version import FakeVersion

class TestDepCacheAdapter(test_helper.MoxTestCase):
	def setUp(self):
		super(TestDepCacheAdapter, self).setUp()
		self.mock_depcache = self.mox.CreateMockAnything()
		self.a_fake_package = FakePackage()
		self.package_adapter = PackageAdapter(self.a_fake_package)
		self.dca = DepCacheAdapterFactory().create_depcache_adapter(self.mock_depcache)
	def testNoCandidate(self):
		self.mock_depcache.GetCandidateVer(self.a_fake_package).AndReturn(None)
		self.mox.ReplayAll()

		version_adapter = self.dca.get_candidate_version(self.package_adapter)
		self.assertEquals(version_adapter, None)
	def testWithCandidate(self):
		fake_version = FakeVersion('1.2')
		fake_version.append_package_file(FakePackageFile())
		self.mock_depcache.GetCandidateVer(self.a_fake_package).AndReturn(fake_version)
		self.mox.ReplayAll()

		version_adapter = self.dca.get_candidate_version(self.package_adapter)
		self.assertEquals(version_adapter.string, '1.2')

if __name__ == '__main__':
	unittest.main()
