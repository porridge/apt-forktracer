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
import apt_pkg
import mox
import unittest

from apt_forktracer.checker import Checker
from apt_forktracer.policy import Policy
from apt_forktracer.reporter import Reporter
from apt_forktracer.status import Status
from apt_forktracer.depcache_adapter import DepCacheAdapter
from apt_forktracer.testlib import test_helper
from apt_forktracer.apt_pkg_adapter import AptPkgAdapter
from apt_forktracer.cache_adapter import CacheAdapterFactory
from apt_forktracer.testlib.fake_cache import FakeCache
from apt_forktracer.testlib.fake_package import FakePackage
from apt_forktracer.package_adapter import PackageAdapterFactory
from apt_forktracer.version_adapter import VersionAdapter

class Test_Base_Cache_Adapter(test_helper.MoxTestCase):
	def setUp(self):
		super(Test_Base_Cache_Adapter, self).setUp()
		self.set_up_fake_cache()
		self.mock_policy = self.mox.CreateMock(Policy)
		self.mock_reporter = self.mox.CreateMock(Reporter)
		self.mock_depcache_adapter = self.mox.CreateMock(DepCacheAdapter)
		self.package_adapter_factory = PackageAdapterFactory(self.mock_depcache_adapter)
		self.set_up_apt_pkg()
		self.apt_pkg_adapter = AptPkgAdapter(self.fake_apt_pkg_module)
		self.ca = CacheAdapterFactory().create_cache_adapter(self.fake_cache, self.apt_pkg_adapter, self.mock_reporter)
		self.mock_checker = self.mox.CreateMock(Checker)
		self.version_adapter = self.mox.CreateMock(VersionAdapter)
		self.version_adapter.string = '1.2.3'
		self.mock_status = self.mox.CreateMock(Status)
	def set_up_fake_cache(self):
		self.fake_cache = FakeCache()
		self.set_up_fake_cache_tweak()
	def set_up_fake_cache_tweak(self):
		pass
	def set_up_apt_pkg(self):
		self.fake_apt_pkg_module = self._create_mock_apt_pkg_module()
		test_helper.copy_state_constants(self.fake_apt_pkg_module, apt_pkg)
	def test_basic_stringification_works(self):
		self.mox.ReplayAll()
		self.assertContains(str(self.ca), 'CacheAdapter')
	def test_states_copied(self):
		self.mox.ReplayAll()
		self.assertEquals(self.ca.states_we_check[0], apt_pkg.CURSTATE_INSTALLED)
		self.assertEquals(self.ca.states_we_check[1], apt_pkg.CURSTATE_HALF_CONFIGURED)
		self.assertEquals(self.ca.states_we_check[2], apt_pkg.CURSTATE_HALF_INSTALLED)
		self.assertEquals(self.ca.states_we_check[3], apt_pkg.CURSTATE_UNPACKED)

class Test_Empty_Cache_Adapter(Test_Base_Cache_Adapter):
	def test_stringification_with_empty_cache(self):
		self.mox.ReplayAll()
		self.assertContains(str(self.ca), '0 package(s)')
	def test_invokes_checker_zero_times_with_empty_cache(self):
		self.mox.ReplayAll()
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Installed_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage())
	def test_stringification_with_one_package(self):
		self.mox.ReplayAll()
		self.assertContains(str(self.ca), '1 package(s)')
	def test_invokes_checker_one_time_with_cache_containing_one_package(self):
		self.mock_depcache_adapter.get_candidate_version(mox.Func(lambda o: o.name == 'afake')).AndReturn(self.version_adapter)
		self.mock_checker.check(mox.IgnoreArg()).AndReturn(self.mock_status)
		self.mock_policy.should_report(self.mock_status).AndReturn(True)
		self.mock_reporter.report(self.mock_status)
		self.mox.ReplayAll()

		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_Two_Installed_Packages_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(name = 'foo'))
		self.fake_cache.append_package(FakePackage(name = 'foo'))
	def test_invokes_checker_two_times_with_cache_containing_one_package(self):
		self.mock_depcache_adapter.get_candidate_version(mox.Func(lambda o: o.name == 'foo')).AndReturn(self.version_adapter)
		self.mock_depcache_adapter.get_candidate_version(mox.Func(lambda o: o.name == 'foo')).AndReturn(self.version_adapter)
		self.mock_checker.check(mox.IgnoreArg()).AndReturn(self.mock_status)
		self.mock_checker.check(mox.IgnoreArg()).AndReturn(self.mock_status)
		self.mock_policy.should_report(self.mock_status).AndReturn(True)
		self.mock_policy.should_report(self.mock_status).AndReturn(True)
		self.mock_reporter.report(self.mock_status)
		self.mock_reporter.report(self.mock_status)
		self.mox.ReplayAll()

		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Not_Installed_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CURSTATE_NOT_INSTALLED))
	def test_invokes_checker_zero_times_with_cache_containing_one_not_installed_package(self):
		self.mox.ReplayAll()
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Conffiles_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CURSTATE_CONFIG_FILES))
	def test_invokes_checker_zero_times_with_cache_containing_one_package_with_just_config_files(self):
		self.mox.ReplayAll()
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Half_Configured_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CURSTATE_HALF_CONFIGURED))
	def test_invokes_checker_one_time_with_cache_containing_one_package_half_configured(self):
		self.mock_depcache_adapter.get_candidate_version(mox.Func(lambda o: o.name == 'afake')).AndReturn(self.version_adapter)
		self.mock_checker.check(mox.IgnoreArg()).AndReturn(self.mock_status)
		self.mock_policy.should_report(self.mock_status).AndReturn(True)
		self.mock_reporter.report(self.mock_status)
		self.mox.ReplayAll()
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Half_Installed_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CURSTATE_HALF_INSTALLED))
	def test_invokes_checker_one_time_with_cache_containing_one_package_half_installed(self):
		self.mock_depcache_adapter.get_candidate_version(mox.Func(lambda o: o.name == 'afake')).AndReturn(self.version_adapter)
		self.mock_checker.check(mox.IgnoreArg()).AndReturn(None)
		self.mox.ReplayAll()
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Unpacked_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CURSTATE_UNPACKED))
	def test_invokes_checker_one_time_with_cache_containing_one_package_half_configured(self):
		self.mock_depcache_adapter.get_candidate_version(mox.Func(lambda o: o.name == 'afake')).AndReturn(self.version_adapter)
		self.mock_checker.check(mox.Func(lambda o:o.name == 'afake' and o.candidate_version.string == '1.2.3')).AndReturn(self.mock_status)
		self.mock_policy.should_report(self.mock_status).AndReturn(False)
		self.mox.ReplayAll()
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

if __name__ == '__main__':
	unittest.main()
