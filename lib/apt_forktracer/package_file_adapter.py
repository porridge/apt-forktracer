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

class PackageFileAdapter:
	"""Wrapper for the aptCache::PackageFile libapt class. See AptPkgAdapter
	for an explanation of why this is needed."""
	TYPE_PACKAGE_FILE = 'Debian Package Index'
	TYPE_DPKG_STATUS = 'Debian dpkg status file'
	def __init__(self, apt_package_file):
		self.name = apt_package_file.FileName
		self.archive = apt_package_file.Archive
		self.component = apt_package_file.Component
		self.version = apt_package_file.Version
		self.origin = apt_package_file.Origin
		self.label = apt_package_file.Label
		self.not_automatic = apt_package_file.NotAutomatic
		self.index_type = apt_package_file.IndexType

	def is_official(self, facter):
		"""Returns True if the package file's origin matches distributor's ID
		according to facter."""
		if self.index_type != PackageFileAdapter.TYPE_PACKAGE_FILE:
			return False
		else:
			return self.origin == facter.distributors_id

	def __str__(self):
		"""Returns a string which includes some attributes of the object."""
		if self.index_type == PackageFileAdapter.TYPE_DPKG_STATUS:
			return '<PackageFileAdapter(dpkg status) path=%s>' % (self.name)
		auto = ''
		if self.not_automatic:
			auto = ' NONAUTO'
		return '<PackageFileAdapter path=%s a=%s c=%s v=%s o=%s l=%s%s>' % (self.name, self.archive, self.component, self.version, self.origin, self.label, auto)
	__repr__ = __str__
