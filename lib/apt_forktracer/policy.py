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

import re

from apt_forktracer.config_stanza import ConfigStanza

class VerbosePolicy:
	"""Just says yes, i.e. "report everything that Checker found to be interesting"."""
	def should_report(self, something):
		return True

class Policy:
	"""Decides whether to report a given Status object, taking into account
	default and/or user-defined rules for what should be reported.
	"""
	def __init__(self, apt_pkg_adapter, facter, config):
		self.apt_pkg_adapter = apt_pkg_adapter
		self.facter = facter
		self.tilde_stripper = re.compile(r'^(.*)~[^~]+$')
		self.config = config

	def base(self, version_string):
		"""Strips off the last tilde and whatever follows it, to get a base version string."""
		if version_string == '':
			return version_string
		m = self.tilde_stripper.search(version_string)
		if m:
			return m.group(1)
		else:
			return version_string

	def _match(self, status, stanza):
		"""Returns True if any of the sources of the status object's candidate
		version matches accept-origin of the given stanza.
		"""
		for file in status.candidate_version.files:
			if stanza.matches('accept-origin', file.origin):
				return True
		return False

	def stanzas_for_status(self, status):
		"""If there are no config stanzas at all for the given package, returns
		a set of "default config stanzas".
		Otherwise returns a (possibly empty) list of stanzas whose
		accept-origin matches any origin of the candidate version of the
		package.
		"""
		stanzas = self.config.package(status.package_name)
		if len(stanzas) == 0:
			return self._create_default_stanzas(status)
		ret = []
		for stanza in stanzas:
			if self._match(status, stanza):
				ret.append(stanza)
		return ret

	def _create_default_stanza(self, status, base = False):
		"""Creates a stanza used when there is no configuration for a given
		package.

		Such Stanza has a matching Package tag, Accept-origin that matches
		anything, Track-origin equal to the distributor ID according to facter,
		and Track-version equal to the candidate version (or the base of the
		candidate version, if base argument is True).
		"""
		s = ConfigStanza()
		s.set('package', status.package_name, 1)
		s.set('accept-origin', '*', 1)
		s.set('track-origin', self.facter.distributors_id, 1)
		if base:
			v = self.base(status.candidate_version.string)
		else:
			v = status.candidate_version.string
		s.set('track-version', v, 1)
		return s.finish(1)

	def _create_default_stanzas(self, status):
		"""Creates stanzas used when there is no configuration for a given package."""
		ret = []
		ret.append(self._create_default_stanza(status, False))
		ret.append(self._create_default_stanza(status, True))
		return ret

	def _track_version(self, stanza, status):
		"""Returns the track-version of a given stanza. The status argument is
		used to expand values such as =candidate or =candidate-base into an
		actual version string.
		"""
		track_version = stanza.get('track-version')
		if len(track_version) > 0 and track_version[0] == '=':
			specifier = track_version[1:]
			if specifier == 'candidate':
				track_version = status.candidate_version.string
			elif specifier == 'candidate-base':
				track_version = self.base(status.candidate_version.string)
			else:
				raise ValueError('invalid version specifier \'%s\'' % specifier)
		return track_version

	def _same_version(self, vs, vo):
		"""Returns True only if vs string is the same as the version string of
		the VersionAdapter object vo.
		"""
		return vo and self.apt_pkg_adapter.version_compare(vo.string, vs) == 0

	def _should_ignore_according_to_stanza(self, stanza, status):
		"""Returns True if the given config stanza says that the given status
		should be ignored.

		This is the case when the version to be tracked is the newest version
		available from the origin to be tracked.
		"""
		origin_to_be_tracked = stanza.get('track-origin')
		if origin_to_be_tracked == '*':
			permitted_versions = status.all_available_versions()
		else:
			permitted_versions = status.versions_from(origin_to_be_tracked)
		version_to_be_tracked = self._track_version(stanza, status)
		return self._same_version(version_to_be_tracked, self.apt_pkg_adapter.version_max(permitted_versions))

	def _should_ignore_according_to_any_of_stanzas(self, status, stanzas):
		"""Returns True if ANY of the given stanzas says that the given status
		should be ignored.
		"""
		for stanza in stanzas:
			if self._should_ignore_according_to_stanza(stanza, status):
				return True
		# do not ignore by default
		return False

	def should_report(self, status):
		"""Returns True unless the given status should be ignored according to
		the config or default rules.
		The default is only considered if there is no configuration for the
		given package whatsoever.
		Also returns True if either the candidate or installed version is None.

		The default rule is as follows:
		The candidate version or the base of the candidate version is the same as the newest available official version.
		"""
		if status.candidate_version == None or status.installed_version == None:
			return True
		stanzas = self.stanzas_for_status(status)
		return not self._should_ignore_according_to_any_of_stanzas(status, stanzas)

