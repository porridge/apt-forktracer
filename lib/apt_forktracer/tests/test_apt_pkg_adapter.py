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

from apt_forktracer.testlib import test_helper
from apt_forktracer.apt_pkg_adapter import AptPkgAdapter
from apt_forktracer.testlib.fake_version import FakeVersion
from apt_forktracer.version_adapter import VersionAdapter

from apt_forktracer.reporter import Reporter

from apt_forktracer.cache_adapter import CacheAdapterFactory

from apt_forktracer.depcache_adapter import DepCacheAdapter
from apt_forktracer.depcache_adapter import DepCacheAdapterFactory

class Base_Apt_Pkg_Adapter_Test(test_helper.MoxTestCase):
	def setUp(self):
		super(Base_Apt_Pkg_Adapter_Test, self).setUp()
		self.create_mock_apt_pkg()
		self.set_up_mock_apt_pkg()
		self.apa = AptPkgAdapter(self.mock_apt_pkg)
		self.set_up_apa()
	def create_mock_apt_pkg(self):
		self.mock_apt_pkg = self._create_mock_apt_pkg_module()
	def set_up_mock_apt_pkg(self):
		pass
	def set_up_apa(self):
		pass

class Newer_Apt_Pkg_Adapter_Test(Base_Apt_Pkg_Adapter_Test):
	def create_mock_apt_pkg(self):
		self.mock_apt_pkg = apt_pkg
	def test_states(self):
		self.mox.ReplayAll()
		self.assertEquals(self.apa.state_installed, apt_pkg.CURSTATE_INSTALLED)
		self.assertEquals(self.apa.state_half_installed, apt_pkg.CURSTATE_HALF_INSTALLED)
		self.assertEquals(self.apa.state_half_configured, apt_pkg.CURSTATE_HALF_CONFIGURED)
		self.assertEquals(self.apa.state_unpacked, apt_pkg.CURSTATE_UNPACKED)

class Uninitialized_Apt_Pkg_Adapter_Test(Base_Apt_Pkg_Adapter_Test):
	def test_methods_fail_on_uninitialized_adapter(self):
		self.mox.ReplayAll()
		self.assertRaisesWithMessageContaining(Exception, 'not initialized', self.apa.get_cache_adapter, 'foo', 'bar', 'baz')
		self.assertRaisesWithMessageContaining(Exception, 'not initialized', self.apa.get_depcache_adapter, 'foo')
		self.assertRaisesWithMessageContaining(Exception, 'not initialized', self.apa.version_compare, 'foo', 'bar')
		self.assertRaisesWithMessageContaining(Exception, 'not initialized', self.apa.version_sort, ['foo', 'bar'])
		self.assertRaisesWithMessageContaining(Exception, 'not initialized', self.apa.version_max, ['foo', 'bar'])

class Initialized_Apt_Pkg_Adapter_Test(Base_Apt_Pkg_Adapter_Test):
	def set_up_mock_apt_pkg(self):
		self.mock_apt_pkg.init_config()
		self.mock_apt_pkg.init_system()
	def set_up_apa(self):
		self.apa.init()
	def test_get_cache_adapters(self):
		mock_reporter = self.mox.CreateMock(Reporter)
		mock_progress = self.struct()

		mock_apt_cache = self.struct()
		mock_cache_adapter = self.struct()
		mock_cache_adapter_factory = self.mox.CreateMock(CacheAdapterFactory)

		mock_apt_depcache = self.struct()
		mock_depcache_adapter = self.mox.CreateMock(DepCacheAdapter)
		mock_depcache_adapter_factory = self.mox.CreateMock(DepCacheAdapterFactory)

		self.mock_apt_pkg.Cache(mock_progress).AndReturn(mock_apt_cache)
		self.mock_apt_pkg.DepCache(mock_apt_cache).AndReturn(mock_apt_depcache)

		mock_cache_adapter_factory.create_cache_adapter(mock_apt_cache, self.apa, mock_reporter).AndReturn(mock_cache_adapter)
		mock_depcache_adapter_factory.create_depcache_adapter(mock_apt_depcache).AndReturn(mock_depcache_adapter)
		self.mox.ReplayAll()

		ca = self.apa.get_cache_adapter(mock_cache_adapter_factory, mock_reporter, mock_progress)
		dca = self.apa.get_depcache_adapter(mock_depcache_adapter_factory)

		self.assertEquals(ca, mock_cache_adapter)
		self.assertEquals(dca, mock_depcache_adapter)
	def test_get_depcache_adapter_fails_without_earlier_get_cache_adapter(self):
		mock_depcache_adapter_factory = self.mox.CreateMock(DepCacheAdapterFactory)
		self.mox.ReplayAll()
		self.assertRaisesWithMessageContaining(Exception, 'must call get_cache_adapter() earlier', self.apa.get_depcache_adapter, mock_depcache_adapter_factory)
	def test_version_comparison(self):
		self.mox.ReplayAll()
		self.assertRaises(ValueError, self.apa.version_compare, None, '1')
		self.assertRaises(ValueError, self.apa.version_compare, '1', None)
		self.assertRaises(ValueError, self.apa.version_compare, None, None)
		self.assert_(self.apa.version_compare('0', '1') < 0)
		self.assert_(self.apa.version_compare('1', '1') == 0)
		self.assert_(self.apa.version_compare('1', '0') > 0)
	def test_version_sort(self):
		self.mox.ReplayAll()
		self.assertEquals(self.apa.version_sort([]), [])
		v1 = VersionAdapter(FakeVersion._create('1', []))
		v0 = VersionAdapter(FakeVersion._create('0', []))
		v2 = VersionAdapter(FakeVersion._create('2.0', []))
		v21 = VersionAdapter(FakeVersion._create('2.0~1', []))
		self.assertEquals(self.apa.version_sort([v21]), [v21])
		self.assertEquals(self.apa.version_sort([v1, v0, v21, v2]), [v2, v21, v1, v0])
	def test_version_max_returns_None_on_empty_list(self):
		self.mox.ReplayAll()
		self.assertEquals(self.apa.version_max([]), None)
		v2 = VersionAdapter(FakeVersion._create('2.0', []))
		v21 = VersionAdapter(FakeVersion._create('2.0~1', []))
		self.assertEquals(self.apa.version_max([v21]), v21)
		self.assertEquals(self.apa.version_max([v2, v21]), v2)
		self.assertEquals(self.apa.version_max([v21, v2]), v2)

if __name__ == '__main__':
	unittest.main()
