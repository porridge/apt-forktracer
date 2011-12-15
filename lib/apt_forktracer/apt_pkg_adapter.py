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

class NullProgress:
	"""Makes libapt shut up when passed to Cache()."""
	def __init__(self, *args, **kwargs):
		pass
	def update(self, *args, **kwargs):
		pass
	def done(self, *args, **kwargs):
		pass

class AptPkgAdapter:
	"""Wraps the apt_pkg module.
	
	The reason for all the *Adapter classes is because the APT API is declared
	as prone to change. By encapsulating access to the APT API in the adapter
	classes, we decouple the rest of the codebase from it, hopefully making it
	easier to port to potential newer incompatible libapt versions.
	"""
	def __init__(self, apt_pkg):
		"""apt_pkg is the imported libapt module to wrap."""
		self.apt_pkg = apt_pkg
		self.state_installed = apt_pkg.CURSTATE_INSTALLED
		self.state_half_installed = apt_pkg.CURSTATE_HALF_INSTALLED
		self.state_half_configured = apt_pkg.CURSTATE_HALF_CONFIGURED
		self.state_unpacked = apt_pkg.CURSTATE_UNPACKED
		self.apt_cache = None
		self.inited = False

	def init(self):
		"""Initializes libapt. Must be called before any other method."""
		self.apt_pkg.init_config()
		self.apt_pkg.init_system()
		self.inited = True

	def _assert_initialized(self):
		"""Helper method to check whether init() had been called."""
		if not self.inited:
			raise Exception('not initialized')

	def get_cache_adapter(self, cache_adapter_factory, reporter, progress):
		"""Returns a CacheAdapter object, given a CacheAdapterFactory, a
		Reporter and libapt progress reporting object.

		Throws an exception if called before init().
		"""
		self._assert_initialized()
		self.apt_cache = self.apt_pkg.Cache(progress)
		return cache_adapter_factory.create_cache_adapter(self.apt_cache, self, reporter)

	def get_depcache_adapter(self, depcache_adapter_factory):
		"""Returns a DepCacheAdapter object, given a DepCacheAdapterFactory.
		Must be called after get_cache_adapter() was invoked.

		Throws an exception if called before init(). 
		"""
		self._assert_initialized()
		if not self.apt_cache:
			raise Exception('you must call get_cache_adapter() earlier')
		apt_depcache = self.apt_pkg.DepCache(self.apt_cache)
		return depcache_adapter_factory.create_depcache_adapter(apt_depcache)

	def version_compare(self, version_a, version_b):
		"""Returns -1, 0 or 1 depending on whether version_a string is considered
		older, equal to, or newer than version_b string.
		
		Throws an exception if either version equals None.
		Throws an exception if called before init(). 
		"""
		self._assert_initialized()
		if version_a == None or version_b == None:
			raise ValueError('cannot compare a None version string')
		return self.apt_pkg.version_compare(version_a, version_b)

	def version_sort(self, versions):
		"""Sorts the given versions list of VersionAdapters in situ and also
		returns it. Sorted list is in newest to oldest order.

		Throws an exception if called before init(). 
		"""
		self._assert_initialized()
		versions.sort(lambda va,vb: self.version_compare(va.string, vb.string), reverse = True)
		return versions

	def version_max(self, versions):
		"""Returns the newest VersionAdapter object in the versions list, or
		None, if versions is empty.

		Throws an exception if called before init(). 
		"""
		self._assert_initialized()
		max = None
		for v in versions:
			if max == None or self.version_compare(v.string, max.string) > 0:
				max = v
		return max

