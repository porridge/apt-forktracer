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

from apt_forktracer.version_adapter import VersionAdapter
from apt_forktracer.status import Status

class PackageAdapterFactory:
	"""Factory for the PackageAdapter objects."""
	def __init__(self, depcache_adapter = None):
		"""The depcache_adapter argument is an optional DepCacheAdapter object."""
		self.depcache_adapter = depcache_adapter

	def create_package_adapter(self, apt_package):
		"""Instantiates a new PackageAdapter from the given apt_package object.
		Sets the candidate_version attribute on the created object, if a
		DepCacheAdapter was provided when creating the factory.
		"""
		pa = PackageAdapter(apt_package)
		if self.depcache_adapter:
			pa.candidate_version = self.depcache_adapter.get_candidate_version(pa)
		return pa

class PackageAdapter:
	"""Wrapper for the pkgCache::Package class. See AptPkgAdapter for why it is
	necessary.
	"""
	def __init__(self, apt_package):
		self.apt_package = apt_package
		self.name = apt_package.name
		if apt_package.current_ver:
			self.current_version = VersionAdapter(apt_package.current_ver)
		else:
			self.current_version = None
		self.candidate_version = None
		self.versions = [VersionAdapter(v) for v in apt_package.version_list]

	def get_status(self, facter):
		"""Creates a new Status object based on this one, given a Facter."""
		versions_by_origin = {}
		for version in self.versions:
			for pfa in version.files:
				origin = pfa.origin
				if not origin:
					continue
				if origin in versions_by_origin:
					versions_by_origin[origin].append(version)
				else:
					versions_by_origin[origin] = [version]
		return Status(self.name, self.current_version, self.candidate_version, versions_by_origin)

	def __str__(self):
		"""Returns a string which includes the package name and current and candidate versions."""
		return '<PackageAdapter %s v=%s->%s >' % (self.name, str(self.current_version), str(self.candidate_version))

	__repr__ = __str__
