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

class Checker:
	"""Checks whether a package is non-standard enough to be reported."""
	def __init__(self, facter, verbose_mode = False):
		"""Optional last argument specifies whether this checker should run in
		verbose mode. By default it is not verbose.
		"""
		self.facter = facter
		self.verbose_mode = verbose_mode

	def check(self, package_adapter):
		"""Given a PackageAdapter object, determines whether it is sufficiently
		non-standard (i.e. non-official, or inconsistent state) to be reported.
		Returns a Status object in such case. Otherwise, returns None.

		Checks which versions are current, candidate, available and whether
		they are official. Does not do detailed version string analyses (this
		is the job of Policy, which also decides whether to ignore any
		reports).

		Currently, its algorithm is as follows:

		In default mode, returns a Status object if there is no candidate
		version, or if the candidate version is not available from an official
		source (as determined by the facter).

		In the verbose mode, additionally returns a Status object if the
		candidate and current versions are not the same (i.e. an upgrade or
		downgrade is pending).

		Raises an exception if current version is None.
		"""
		current = package_adapter.current_version
		candidate = package_adapter.candidate_version
		if current == None:
			raise ValueError('Package %s has no current version' % package_adapter)
		if candidate == None:
			return package_adapter.get_status(self.facter)
		if self.verbose_mode and candidate.string != current.string:
			return package_adapter.get_status(self.facter)
		if not candidate.is_officially_available(self.facter):
			return package_adapter.get_status(self.facter)
		return None

