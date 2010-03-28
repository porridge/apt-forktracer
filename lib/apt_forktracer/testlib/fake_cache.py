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

class FakeCache:
	"""Pretends to be the pkgCache::Header object from apt_pkg. We cannot use
	the real one, because it is tied to the binary cache file, which is
	difficult to construct and control."""
	def __init__(self):
		self.packages = []
	def append_package(self, package):
		self.packages.append(package)
	def __str__(self):
		pkgs = ''
		for p in self.packages:
			pkgs += str(p)+','
		return '<FakeCache [%s]>' % pkgs
