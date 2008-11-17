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
import apt_pkg
import pmock
import unittest

from apt_forktracer.testlib import test_helper
from apt_forktracer.apt_pkg_adapter import AptPkgAdapter
from apt_forktracer.cache_adapter import CacheAdapterFactory
from apt_forktracer.testlib.fake_cache import FakeCache
from apt_forktracer.testlib.fake_package import FakePackage
from apt_forktracer.package_adapter import PackageAdapterFactory
from apt_forktracer.testlib.pmock_ntimes import NTimesInvocationMatcher

class Test_Base_Cache_Adapter(test_helper.TestCase):
	def setUp(self):
		self.set_up_fake_cache()
		self.mock_policy = self.mock()
		self.mock_reporter = self.mock()
		self.mock_depcache_adapter = self.mock()
		self.package_adapter_factory = PackageAdapterFactory(self.mock_depcache_adapter)
		self.set_up_apt_pkg()
		self.apt_pkg_adapter = AptPkgAdapter(self.fake_apt_pkg_module)
		self.ca = CacheAdapterFactory().create_cache_adapter(self.fake_cache, self.apt_pkg_adapter, self.mock_reporter)
		self.mock_checker = self.mock()
		self.version_adapter = self.mock()
		self.version_adapter.string = '1.2.3'
		self.mock_status = self.mock()
	def set_up_fake_cache(self):
		self.fake_cache = FakeCache()
		self.set_up_fake_cache_tweak()
	def set_up_fake_cache_tweak(self):
		pass
	def set_up_apt_pkg(self):
		self.fake_apt_pkg_module = self._create_mock_apt_pkg_module()
		test_helper.copy_state_constants(self.fake_apt_pkg_module, apt_pkg)
	def test_basic_stringification_works(self):
		self.assertContains(str(self.ca), 'CacheAdapter')
	def test_states_copied(self):
		self.assertEquals(self.ca.states_we_check[0], apt_pkg.CurStateInstalled)
		self.assertEquals(self.ca.states_we_check[1], apt_pkg.CurStateHalfConfigured)
		self.assertEquals(self.ca.states_we_check[2], apt_pkg.CurStateHalfInstalled)
		self.assertEquals(self.ca.states_we_check[3], apt_pkg.CurStateUnPacked)

class Test_Cache_Adapter_With_Old_Apt_Pkg_Class(Test_Base_Cache_Adapter):
	def set_up_apt_pkg(self):
		class Fake_Apt_Pkg_Class_Without_States:
			pass
		self.fake_apt_pkg_module = Fake_Apt_Pkg_Class_Without_States()

class Test_Empty_Cache_Adapter(Test_Base_Cache_Adapter):
	def test_stringification_with_empty_cache(self):
		self.assertContains(str(self.ca), '0 package(s)')
	def test_invokes_checker_zero_times_with_empty_cache(self):
		self.mock_checker.expects(pmock.never()).check()
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Installed_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage())
	def test_stringification_with_one_package(self):
		self.assertContains(str(self.ca), '1 package(s)')
	def test_invokes_checker_one_time_with_cache_containing_one_package(self):
		self.mock_depcache_adapter.expects(pmock.once()).get_candidate_version(pmock.functor(lambda o: o.name == 'afake')).will(pmock.return_value(self.version_adapter))
		self.mock_checker.expects(pmock.once()).method("check").will(pmock.return_value(self.mock_status))
		self.mock_policy.expects(pmock.once()).should_report(pmock.eq(self.mock_status)).will(pmock.return_value(True))
		self.mock_reporter.expects(pmock.once()).report(pmock.eq(self.mock_status))
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_Two_Installed_Packages_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(name = 'foo'))
		self.fake_cache.append_package(FakePackage(name = 'foo'))
	def test_invokes_checker_two_times_with_cache_containing_one_package(self):
		self.mock_depcache_adapter.expects(NTimesInvocationMatcher(2)).get_candidate_version(pmock.functor(lambda o: o.name == 'foo')).will(pmock.return_value(self.version_adapter))
		self.mock_checker.expects(NTimesInvocationMatcher(2)).method("check").will(pmock.return_value(self.mock_status))
		self.mock_policy.expects(NTimesInvocationMatcher(2)).should_report(pmock.eq(self.mock_status)).will(pmock.return_value(True))
		self.mock_reporter.expects(NTimesInvocationMatcher(2)).report(pmock.eq(self.mock_status))
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Not_Installed_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CurStateNotInstalled))
	def test_invokes_checker_zero_times_with_cache_containing_one_not_installed_package(self):
		self.mock_checker.expects(pmock.never()).method("check")
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Conffiles_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CurStateConfigFiles))
	def test_invokes_checker_zero_times_with_cache_containing_one_package_with_just_config_files(self):
		self.mock_checker.expects(pmock.never()).method("check")
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Half_Configured_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CurStateHalfConfigured))
	def test_invokes_checker_one_time_with_cache_containing_one_package_half_configured(self):
		self.mock_depcache_adapter.expects(pmock.once()).get_candidate_version(pmock.functor(lambda o: o.name == 'afake')).will(pmock.return_value(self.version_adapter))
		self.mock_checker.expects(pmock.once()).method("check").will(pmock.return_value(self.mock_status))
		self.mock_policy.expects(pmock.once()).should_report(pmock.eq(self.mock_status)).will(pmock.return_value(True))
		self.mock_reporter.expects(pmock.once()).report(pmock.eq(self.mock_status))
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Half_Installed_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CurStateHalfInstalled))
	def test_invokes_checker_one_time_with_cache_containing_one_package_half_installed(self):
		self.mock_depcache_adapter.expects(pmock.once()).get_candidate_version(pmock.functor(lambda o: o.name == 'afake')).will(pmock.return_value(self.version_adapter))
		self.mock_checker.expects(pmock.once()).method("check").will(pmock.return_value(None))
		self.mock_policy.expects(pmock.never()).method("should_report")
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

class Test_One_Unpacked_Package_Cache_Adapter(Test_Base_Cache_Adapter):
	def set_up_fake_cache_tweak(self):
		self.fake_cache.append_package(FakePackage(current_state = apt_pkg.CurStateUnPacked))
	def test_invokes_checker_one_time_with_cache_containing_one_package_half_configured(self):
		self.mock_depcache_adapter.expects(pmock.once()).get_candidate_version(pmock.functor(lambda o: o.name == 'afake')).will(pmock.return_value(self.version_adapter))
		self.mock_checker.expects(pmock.once()).check(pmock.functor(lambda o:o.name == 'afake' and o.candidate_version.string == '1.2.3')).will(pmock.return_value(self.mock_status))
		self.mock_policy.expects(pmock.once()).should_report(pmock.eq(self.mock_status)).will(pmock.return_value(False))
		self.mock_reporter.expects(pmock.never()).method("report")
		self.ca.run(self.mock_checker, self.mock_policy, self.package_adapter_factory)

if __name__ == '__main__':
	unittest.main()
