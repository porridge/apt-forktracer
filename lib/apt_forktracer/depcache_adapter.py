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

from apt_forktracer.version_adapter import VersionAdapter

class DepCacheAdapterFactory:
	"""Factory for DepCacheAdapter objects."""
	def create_depcache_adapter(self, apt_dep_cache):
		return DepCacheAdapter(apt_dep_cache)

class DepCacheAdapter:
	"""Wrapper for the pkgDepCache class. See the AptPkgAdapter for why this
	class is necessary."""
	def __init__(self, apt_dep_cache):
		self.apt_dep_cache = apt_dep_cache
	def get_candidate_version(self, pkg):
		"""Returns a VersionAdapter object representing the candidate version
		of the given PackageAdapter object pkg. Returns None if there is no
		candidate version."""
		apt_version = self.apt_dep_cache.GetCandidateVer(pkg.apt_package)
		if not apt_version:
			return None
		else:
			return VersionAdapter(apt_version)
