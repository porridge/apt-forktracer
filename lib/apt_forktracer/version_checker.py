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

class VersionChecker:
	"""Given a VersionAdapter object, determines whether it is sufficiently
	non-standard (i.e. non-official, or inconsistent state) to be reported.
	Checks whether the version is available and official. Does not do detailed
	version string analyses (this is the job of Policy, which also decides
	whether to ignore any reports). See also Checker, which invokes methods of
	this class."""
	def __init__(self, facter):
		self.facter = facter

	def analyze(self, version):
		"""Returns True if this version is somehow suspicious.
		Currently just checks whether a version is officially available."""
		return not version.is_officially_available(self.facter)
