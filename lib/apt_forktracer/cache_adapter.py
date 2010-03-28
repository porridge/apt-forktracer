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

class CacheAdapterFactory:
	"""A factory of CacheAdapter objects."""
	def create_cache_adapter(self, apt_cache, apt_pkg_adapter, reporter):
		return _CacheAdapter(apt_cache, apt_pkg_adapter, reporter)

class _CacheAdapter:
	"""Wrapper for the pkgCache class. See AptPkgAdapter for why this class is necessary."""
	def __init__(self, apt_cache, apt_pkg_adapter, reporter):
		self.apt_cache = apt_cache
		self.reporter = reporter
		self.states_we_check = [ apt_pkg_adapter.state_installed, apt_pkg_adapter.state_half_configured, apt_pkg_adapter.state_half_installed, apt_pkg_adapter.state_unpacked ]
	def run(self, checker, policy, package_adapter_factory):
		for package in self.apt_cache.packages:
			if package.current_state not in self.states_we_check:
				continue
			pa = package_adapter_factory.create_package_adapter(package)
			status = checker.check(pa)
			if not status:
				continue
			if policy.should_report(status):
				self.reporter.report(status)

	def __str__(self):
		return '<CacheAdapter with %d package(s)>' % len(self.apt_cache.packages)
	__repr__ = __str__

