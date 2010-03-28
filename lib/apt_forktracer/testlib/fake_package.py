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

class FakePackage:
	"""Pretends to be the pkgCache::Package object from apt_pkg. We cannot use
	the real one, because it is tied to the binary cache, which is difficult to
	construct and control."""
	def __init__(self, current_state = apt_pkg.CURSTATE_INSTALLED, name = 'afake'):
		self.Name = name
		self.VersionList = []
		self.current_state = current_state
		self.current_ver = None
	def append_version(self, version, current = False):
		self.VersionList.append(version)
		if current:
			self.current_ver = version
	def __str__(self):
		vers = ''
		for v in self.VersionList:
			vers += str(v) + ','
		return '<FakePackage(%s) %s v=%s [%s]>' % (self.current_state, self.Name, str(self.current_ver), vers)
