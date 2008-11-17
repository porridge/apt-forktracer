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

class Status:
	"""Models a potentially interesting piece of information about the status
	   of an installed version of a package, WRT other available versions.
	   """
	def __init__(self, package_name, installed_version, candidate_version, versions_by_origin = {}):
		self.package_name = package_name
		self.installed_version = installed_version
		self.candidate_version = candidate_version
		self.versions_by_origin = versions_by_origin

	def versions_from(self, origin):
		"""Returns a list of versions available from a given origin."""
		if self.versions_by_origin.has_key(origin):
			return self.versions_by_origin[origin]
		else:
			return []

	def all_available_versions(self):
		"""Returns a list of all versions available from any source.
		Does not include the installed or candidate versions, if they are not
		available from some source."""
		ret = []
		for a in self.versions_by_origin.values():
			ret.extend(a)
		return ret

	def __str__(self):
		version_info = ''
		for origin,versions in self.versions_by_origin.items():
			version_info += '[%s: %s]' % (origin, ','.join([v.string for v in versions]))
		return '<Status %s %s->%s %s>' % (self.package_name, self.installed_version, self.candidate_version, version_info)
	__repr__ = __str__
