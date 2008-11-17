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

import subprocess
import re

class Facter:
	"""Reports some facts about the system. Currently just the distributor's id
	(available through the distributors_id attribute).

	The optional attributes are mostly for testing purposes.
	"""
	def __init__(self, lsb_release = 'lsb_release --id --short', file = '/etc/lsb-release'):
		self.distributors_id = self.get_distrib_id_from_command(lsb_release)
		if not self.distributors_id:
			self.distributors_id = self.get_distrib_id_from_file('/etc/lsb-release')
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
			output = p.stdout.readline()
			p.stdout.close()
			p.wait()
			if p.returncode == 0:
				return output.rstrip('\n')
		except OSError:
			pass
 
