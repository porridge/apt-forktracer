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

from apt_forktracer.package_file_adapter import PackageFileAdapter

class FakePackageFile:
	"""Pretends to be the pkgCache::PackageFile object from apt_pkg. We cannot
	use the real one, because it is tied to the binary cache, which is
	difficult to construct and control."""
	def __init__(self, path = '/a/fake', type = 'normal', origin = 'Debian', archive = 'stable-proposed-updates'):
		self.filename = path
		self.archive = archive
		self.component = 'main'
		# release version
		self.version = '1.0'
		# provider of the archive
		self.origin = origin
		# name of the distribution
		self.label = 'Debian'
		# apt will not consider taking packages unless told explicitly to do so
		self.not_automatic = 0
		if type == 'normal':
			self.index_type = PackageFileAdapter.TYPE_PACKAGE_FILE
		elif type == 'dpkg':
			self.index_type = PackageFileAdapter.TYPE_DPKG_STATUS
			self.filename = '/var/lib/dpkg/status'
			self.archive = 'now'
			self.component = ''
			self.version = ''
			self.origin = ''
			self.label = ''
		else:
			raise ValueError('Unknown type "%s"' % type)
	def __str__(self):
		return '<FakePackageFile(%s) path=%s a=%s c=%s v=%s o=%s l=%s %s>' % (self.index_type, self.filename, self.archive, self.component, self.version, self.origin, self.label, self.not_automatic)
