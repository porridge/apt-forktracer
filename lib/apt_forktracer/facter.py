# apt-forktracer - a utility for managing package versions
# Copyright (C) 2008-2020 Marcin Owsiany <porridge@debian.org>
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

import os
import re
import subprocess
import sys

class Facter:
	"""Reports some facts about the system. Currently just the distributor's id
	(available through the distributors_id attribute).

	Tries to import the lsb_release Python module, which should be fast and
	provide most correct information.

	If that fails, tries to run lsb_release(1) and read its output, which
	should be functionally equivalent, but not as fast, since it requires a
	fork/exec.

	If that fails too, reads /etc/lsb-release directly as the last resort. This
	might not be correct in all cases, as strictly speaking that file is not
	required, but just provides a way to override values detected from the
	system.

	Throws an exception if all methods fail.

	The optional attributes are mostly for testing purposes.
	"""
	def __init__(self, lsb_release_module = 'lsb_release', lsb_release = 'lsb_release --id --short', file = '/etc/lsb-release'):
		self.distributors_id = self.get_distrib_id_from_module(lsb_release_module)
		if not self.distributors_id:
			self.distributors_id = self.get_distrib_id_from_command(lsb_release)
		if not self.distributors_id:
			self.distributors_id = self.get_distrib_id_from_file(file)
		overridden_id = os.getenv('APT_FORKTRACER_OVERRIDE_DISTRIBUTOR_ID')
		if overridden_id:
			self.distributors_id = overridden_id
		if not self.distributors_id:
			raise RuntimeError('Could not obtain distributors id from lsb_release')

	def get_distrib_id_from_file(self, file_name):
		p = re.compile(r'DISTRIB_ID\s*=\s*(\S+)')
		try:
			f = open(file_name, 'r')
			for line in f:
				m = p.search(line)
				if m:
					f.close()
					return m.group(1)
		except IOError:
			pass

	def get_distrib_id_from_command(self, command):
		try:
			p = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True)
			output = p.stdout.readline().decode()
			p.stdout.close()
			p.wait()
			if p.returncode == 0:
				return output.rstrip('\n')
		except OSError:
			pass

	def get_distrib_id_from_module(self, module_name):
		try:
			__import__(module_name)
			# we need to look up in sys.modules as __import__(name) only returns top-level module if name contains dots
			module = sys.modules[module_name]
			distinfo = module.get_distro_information()
			return distinfo['ID']
		except ImportError:
			pass
