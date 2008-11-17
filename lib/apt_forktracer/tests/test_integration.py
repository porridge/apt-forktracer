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
from apt_forktracer.checker import Checker
from apt_forktracer.config import Config
from apt_forktracer.config_finder import ConfigFinder
from apt_forktracer.config_parser import ConfigParser
from apt_forktracer.depcache_adapter import DepCacheAdapter
from apt_forktracer.testlib.fake_package import FakePackage
from apt_forktracer.testlib.fake_package_file import FakePackageFile
from apt_forktracer.testlib.fake_version import FakeVersion
from apt_forktracer.package_adapter import PackageAdapterFactory
from apt_forktracer.policy import Policy, VerbosePolicy

class TestIntegraton(test_helper.TestCase):
	def setUp(self):
		dpkg_status_file = FakePackageFile(type = 'dpkg')
		debian_stable_package_file = FakePackageFile(archive = 'stable')
		debian_proposed_updates_package_file = FakePackageFile(archive = 'stable-proposed-updates')
		debian_security_package_file = FakePackageFile(archive = 'stable-security')
		local_package_file = FakePackageFile(origin = 'SnakeOil, Inc.', archive = 'etch')

		libc6_version = FakeVersion('2.6.1-2etch1')
		libc6_version.append_package_file(debian_stable_package_file)
		libc6_version.append_package_file(debian_security_package_file)
		libc6_updates_version = FakeVersion('2.6.1-2etch2')
		libc6_updates_version.append_package_file(debian_proposed_updates_package_file)
		libc6_updates_version.append_package_file(dpkg_status_file)
		libc6 = FakePackage(name = 'libc6')
		libc6.append_version(libc6_updates_version, True)
		libc6.append_version(libc6_version)

		libspf_version = FakeVersion('0.1-1')
		libspf_version.append_package_file(debian_stable_package_file)
		libspf_updates_version = FakeVersion('0.1-2')
		libspf_updates_version.append_package_file(debian_proposed_updates_package_file)
		libspf_local_version = FakeVersion('0.1-1~sl1')
		libspf_local_version.append_package_file(dpkg_status_file)
		libspf_local_version.append_package_file(local_package_file)
		libspf = FakePackage(name = 'libspf')
		libspf.append_version(libspf_version)
		libspf.append_version(libspf_local_version, True)
		libspf.append_version(libspf_updates_version)

		libfoobar_version = FakeVersion('0.5-5')
		libfoobar_version.append_package_file(debian_stable_package_file)
		libfoobar_local_version = FakeVersion('0.5-5~sl1')
		libfoobar_local_version.append_package_file(dpkg_status_file)
		libfoobar_local_version.append_package_file(local_package_file)
		libfoobar = FakePackage(name = 'libfoobar')
		libfoobar.append_version(libfoobar_version)
		libfoobar.append_version(libfoobar_local_version, True)

		git_version = FakeVersion('1:1.5.2.5-2build1')
		git_version.append_package_file(debian_stable_package_file)
		git_backport_version = FakeVersion('1:1.5.6.3-1.1ubuntu2~mowsiany.1')
		git_backport_version.append_package_file(dpkg_status_file)
		git_backport_version.append_package_file(local_package_file)
		git = FakePackage(name = 'git-core')
		git.append_version(git_version)
		git.append_version(git_backport_version, True)

		self.apt_cache = self.mock()
		self.apt_cache.Packages = [git, libc6, libspf, libfoobar]

		self.apt_depcache = self.mock()
		self.apt_depcache.stubs().GetCandidateVer(self.functor(lambda o: o.Name == 'libc6', desc = 'name == libc6')).will(pmock.return_value(libc6_updates_version))
		self.apt_depcache.stubs().GetCandidateVer(self.functor(lambda o: o.Name == 'libspf', desc = 'name == libspf')).will(pmock.return_value(libspf_local_version))
		self.apt_depcache.stubs().GetCandidateVer(self.functor(lambda o: o.Name == 'libfoobar', desc = 'name == libfoobar')).will(pmock.return_value(libfoobar_local_version))
		self.apt_depcache.stubs().GetCandidateVer(self.functor(lambda o: o.Name == 'git-core', desc = 'name == git-core')).will(pmock.return_value(git_backport_version))

		self.reporter = self.mock()
		mock_progress = self.mock()

		self.apt_pkg = self._create_mock_apt_pkg_module()
		test_helper.copy_state_constants(self.apt_pkg, apt_pkg)
		self.apt_pkg.expects(pmock.once()).GetCache(pmock.eq(mock_progress)).will(pmock.return_value(self.apt_cache))

		self.apt_pkg_adapter = AptPkgAdapter(self.apt_pkg)
		self.apt_pkg_adapter.init()
		cache_adapter_factory = CacheAdapterFactory()
		self.package_adapter_factory = PackageAdapterFactory(DepCacheAdapter(self.apt_depcache))
		self.apt_pkg_adapter.get_cache_adapter(cache_adapter_factory, self.reporter, mock_progress)

		self.facter = self.mock()
		self.facter.distributors_id = 'Debian'

		config_finder = ConfigFinder('test-data/config')
		config_parser = ConfigParser()
		self.config = Config()
		for path, file in config_finder:
			config_parser.load(file, self.config)
		self.cache_adapter = cache_adapter_factory.create_cache_adapter(self.apt_cache, self.apt_pkg_adapter, self.reporter)

	def test_verbose(self):
		checker = Checker(self.facter, True)
		policy = VerbosePolicy()
		self.reporter.expects(pmock.never()).report(self.functor(lambda o: o.package_name == 'libc6', desc = 'name == libc6'))
		self.reporter.expects(pmock.once()).report(self.functor(lambda o: o.package_name == 'libspf', desc = 'name == libspf'))
		self.reporter.expects(pmock.once()).report(self.functor(lambda o: o.package_name == 'libfoobar', desc = 'name == libfoobar'))
		self.reporter.expects(pmock.once()).report(self.functor(lambda o: o.package_name == 'git-core', desc = 'name == git-core'))
		self.cache_adapter.run(checker, policy, self.package_adapter_factory)

	def test_non_verbose_empty_config(self):
		checker = Checker(self.facter)
		policy = Policy(self.apt_pkg_adapter, self.facter, Config())
		self.reporter.expects(pmock.never()).report(self.functor(lambda o: o.package_name == 'libc6', desc = 'name == libc6'))
		self.reporter.expects(pmock.once()).report(self.functor(lambda o: o.package_name == 'libspf', desc = 'name == libspf'))
		self.reporter.expects(pmock.never()).report(self.functor(lambda o: o.package_name == 'libfoobar', desc = 'name == libfoobar'))
		self.reporter.expects(pmock.once()).report(self.functor(lambda o: o.package_name == 'git-core', desc = 'name == git-core'))
		self.cache_adapter.run(checker, policy, self.package_adapter_factory)

	def test_non_verbose(self):
		checker = Checker(self.facter)
		policy = Policy(self.apt_pkg_adapter, self.facter, self.config)
		self.reporter.expects(pmock.never()).report(self.functor(lambda o: o.package_name == 'libc6', desc = 'name == libc6'))
		self.reporter.expects(pmock.once()).report(self.functor(lambda o: o.package_name == 'libspf', desc = 'name == libspf'))
		self.reporter.expects(pmock.never()).report(self.functor(lambda o: o.package_name == 'libfoobar', desc = 'name == libfoobar'))
		self.reporter.expects(pmock.never()).report(self.functor(lambda o: o.package_name == 'git-core', desc = 'name == git-core'))
		self.cache_adapter.run(checker, policy, self.package_adapter_factory)

if __name__ == '__main__':
	unittest.main()
