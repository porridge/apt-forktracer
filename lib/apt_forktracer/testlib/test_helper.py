# apt-forktracer - a utility for managing package versions
# Copyright (C) 2008,2010,2019 Marcin Owsiany <porridge@debian.org>
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

from mox3 import mox as mox
import re

from apt_forktracer.facter import Facter

def copy_state_constants(to_obj, from_obj):
	to_obj.CURSTATE_INSTALLED = from_obj.CURSTATE_INSTALLED
	to_obj.CURSTATE_HALF_CONFIGURED = from_obj.CURSTATE_HALF_CONFIGURED
	to_obj.CURSTATE_HALF_INSTALLED = from_obj.CURSTATE_HALF_INSTALLED
	to_obj.CURSTATE_UNPACKED = from_obj.CURSTATE_UNPACKED

class Advanced_Version_Comparator:
	def __init__(self):
		# tuple: v1, v2, relation
		# relation == 1 iff v1 << v2
		# == 0  iff v1 == v2
		# == -1 iff v1 >> v2
		self.comparisons = [
			('1', '0', 1),
			('1', '1', 0),
			('0', '1', -1),

			('0.1-1', '0.1-1', 0),
			('0.1-1', '0.1-2', -1),
			('0.1-2', '0.1-1~sl1', 1),
			('0.1-1', '0.1-1~sl1', 1),
			('2.6.1-2etch1', '2.6.1-2etch2', -1),
			('2.6.1-2etch1', '2.6.1-2etch1', 0),
			('2.6.1-2etch2', '2.6.1-2etch2', 0),
			('1:1.5.6.3-1.1ubuntu2~mowsiany.1', '1:1.5.6.3-1.1ubuntu2~mowsiany.1', 0),
			('0.5-5~sl1', '0.5-5~sl1', 0),
			('0.5-5', '0.5-5~sl1', 1),
			('0.5-5', '0.5-5', 0),
			('1:1.5.2.5-2build1', '1:1.5.2.5-2build1', 0),
			('1:1.5.2.5-2build1', '1:1.5.6.3-1.1ubuntu2~mowsiany.1', -1),
			('1:1.5.2.5-2build1', '1:1.5.6.3-1.1ubuntu2', -1),
	
			('1.9', '2.0', -1),
	
			('2.0~1', '0', 1),
			('2.0~1', '1', 1),
			('2.0~1', '2.0~1', 0),
			('2.0~1', '2.0', -1),
	
			('2.0', '0', 1),
			('2.0', '2.0~1', 1),
			('2.0', '2.0~1', 1),
			('2.0', '2.0', 0),
			('2.0', '2.1~1', -1),
			('2.0', '2.1~2', -1),
			('2.0', '2.1', -1),
			('2.0', '2.2', -1),
	
			('2.1~1', '2.1~1', 0),
			('2.1~1', '2.1', -1),
	
			('2.1~2', '2.1~2', 0),
			('2.1~2', '2.1', -1),
	
			('2.1', '2.0~1', 1),
			('2.1', '2.0', 1),
			('2.1', '2.1~1', 1),
			('2.1', '2.1~2', 1),
			('2.1', '2.1', 0),
			('2.1', '2.2~1', -1),
			('2.1', '2.2~2', -1),
			('2.1', '2.2', -1),
	
			('2.2~2', '2.2~2', 0),
			('2.2~2', '2.2', -1),
	
			('2.2', '2.1~1', 1),
			('2.2', '2.1~2', 1),
			('2.2', '2.1', 1),
			('2.2', '2.2~1', 1),
			('2.2', '2.2', 0),
		]
	def compare(self, v1, v2):
		if v1 == v2:
			return 0
		for comparison in self.comparisons:
			if v1 == comparison[0] and v2 == comparison[1]:
				return comparison[2]
		for comparison in self.comparisons:
			if v1 == comparison[1] and v2 == comparison[0]:
				return 0 - comparison[2]
		if v1.find('~') >= 0 or v2.find('~') >= 0:
			raise ValueError('not attempting to compare %s with %s (tilde found)' % (v1, v2))
		if v1 > v2:
			return 1
		return -1


class MoxTestCase(mox.MoxTestBase):
	def assertContains(self, haystack, needle):
		self.assertTrue(haystack.find(needle) >= 0, 'could not find %s in %s' % (needle, haystack))
	def assertNotContains(self, haystack, needle):
		self.assertTrue(haystack.find(needle) < 0, 'found "%s" in "%s"' % (needle, haystack))
	def assertMatches(self, haystack, regex):
		self.assertTrue(re.compile(regex).search(haystack), 'could not match "%s" against "%s"' % (haystack, regex))

	def assertRaisesWithMessageContaining(self, exception_class, message_snippet, method, *args, **kwargs):
		succeeded = False
		try:
			method(*args, **kwargs)
			succeeded = True
		except exception_class as e:
			self.assertContains(str(e), message_snippet)
		except Exception as e:
			self.fail('%s failed with %s(%s) instead of %s' % (method, type(e), e.message, exception_class))
		if succeeded:
			self.fail('%s did not fail with %s' % (method, exception_class))

	def _create_mock_facter(self, id):
		mock_facter = self.mox.CreateMock(Facter)
		mock_facter.distributors_id = id
		return mock_facter

	def struct(self, **kwargs):
		class Struct:
			def __init__(self, **entries): self.__dict__.update(entries)
		return Struct(**kwargs)

	def _create_mock_apt_pkg_module(self):
		mock_apt_pkg_module = self.mox.CreateMockAnything()
		comparator = Advanced_Version_Comparator()
		mock_apt_pkg_module.version_compare = lambda x, y: comparator.compare(x, y)
		mock_apt_pkg_module.init_config = lambda: None
		mock_apt_pkg_module.init_system = lambda: None
		return mock_apt_pkg_module

