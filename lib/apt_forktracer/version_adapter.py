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

from apt_forktracer.package_file_adapter import PackageFileAdapter

class VersionAdapter:
	"""Mirror of the aptCache::version libapt class. See AptPkgAdapter for an
	explanation of why this is needed."""
	def __init__(self, apt_version):
		self.string = apt_version.ver_str
		self.files = [PackageFileAdapter(pf[0]) for pf in apt_version.file_list]

	def is_officially_available(self, facter):
		"""Returns True if any of the files considers itself official."""
		for file in self.files:
			if file.is_official(facter):
				return True
		return False

	def __str__(self):
		files = ''
		for f in self.files:
			files += str(f) + ','
		return '<VersionAdapter %s [%s]>' % (self.string, files)
	__repr__ = __str__
