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

class Reporter:
	"""Reports a status to the user. Currently just pretty-prints it to standard output. Might syslog or whatever..."""
	def report(self, status):
		"""Prints a formatted report for a given status to standard output."""
		print self.format(status)
	def format(self, status):
		"""Returns a formatted report for a given status."""
		if (not status.installed_version) and (not status.candidate_version):
			pending_version_info = ''
		elif not status.installed_version:
			pending_version_info = '->%s' % status.candidate_version.string
		elif not status.candidate_version:
			pending_version_info = '%s->' % status.installed_version.string
		elif status.installed_version.string == status.candidate_version.string:
			pending_version_info = status.installed_version.string
		else:
			pending_version_info = '%s->%s' % (status.installed_version.string, status.candidate_version.string)
		version_info = ''
		for origin,versions in status.versions_by_origin.items():
			version_info += ' [%s: %s]' % (origin, ' '.join([v.string for v in versions]))
		return '%s (%s)' % (status.package_name, pending_version_info) + version_info

