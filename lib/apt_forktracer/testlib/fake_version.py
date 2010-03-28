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

from apt_forktracer.testlib.fake_package_file import FakePackageFile

class FakeVersion(object):
	"""Pretends to be the pkgCache::version object from apt_pkg. We cannot use
	the real one, because it is tied to the binary cache, which is difficult to
	construct and control."""
	def __init__(self, version_string = '1.2.3'):
		self.ver_str = version_string
		self.file_list = []
	def append_package_file(self, package_file):
		tuple = (package_file,1)
		self.file_list.append(tuple)
	def __str__(self):
		files = ''
		for f in self.file_list:
			files += '(%s,%d),' % (str(f[0]), f[1])
		return '<FakeVersion %s [%s]>' % (self.ver_str, files)
	def _create(string, origins):
		"""Factory method."""
		fv = FakeVersion(string)
		for o in origins:
			if o == 'dpkg':
				fv.append_package_file(FakePackageFile(type = 'dpkg'))
			else:
				fv.append_package_file(FakePackageFile(origin = o))
		return fv
	_create = staticmethod(_create)

