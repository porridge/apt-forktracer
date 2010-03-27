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

import pmock
import re
import unittest

from apt_forktracer.testlib.fake_version import FakeVersion

def copy_state_constants(to_obj, from_obj):
	to_obj.CurStateInstalled = from_obj.CurStateInstalled
	to_obj.CurStateHalfConfigured = from_obj.CurStateHalfConfigured
	to_obj.CurStateHalfInstalled = from_obj.CurStateHalfInstalled
	to_obj.CurStateUnPacked = from_obj.CurStateUnPacked

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
		return cmp(v1, v2)

from pmock import FunctorConstraint

class DescriptionFunctorConstraint(FunctorConstraint):
	def __init__(self, boolean_functor, desc = ''):
		self._boolean_functor = boolean_functor
		self._description = desc
	def __repr__(self):
		if self._description == '':
			return "%s.functor(%s)" % (__name__, repr(self._boolean_functor))
		else:
			return "%s.functor(%s)" % (__name__, self._description)

class TestCase(pmock.MockTestCase):
	def functor(self, boolean_functor, desc = ''):
		return DescriptionFunctorConstraint(boolean_functor, desc)
	def assertContains(self, haystack, needle):
		self.assert_(haystack.find(needle) >= 0, 'could not find %s in %s' % (needle, haystack))
	def assertNotContains(self, haystack, needle):
		self.assert_(haystack.find(needle) < 0, 'found "%s" in "%s"' % (needle, haystack))
	def assertMatches(self, haystack, regex):
		self.assert_(re.compile(regex).search(haystack), 'could not match "%s" against "%s"' % (haystack, regex))
	def _create_mock_facter(self, id):
		mock_facter = self.mock()
		mock_facter.distributors_id = id
		return mock_facter

	def _create_mock_cache_adapter(self):
		mock_cache_adapter = self.mock()
		comparator = Advanced_Version_Comparator()
		class ComparatorStub:
			def __init__(self, comparator):
				self.comparator = comparator
			def invoke(self, invocation):
				return self.comparator.compare(invocation.args[0], invocation.args[1])
		mock_cache_adapter.stubs().method("version_compare").will(ComparatorStub(comparator))
		class SorterStub:
			def __init__(self, comparator):
				self.comparator = comparator
			def invoke(self, invocation):
				invocation.args[0].sort(lambda va, vb: self.comparator.compare(va.string, vb.string), reverse = True)
				return invocation.args[0]
		mock_cache_adapter.stubs().method("version_sort").will(SorterStub(comparator))
		class MaxVersionStub:
			def __init__(self, comparator):
				self.comparator = comparator
			def invoke(self, invocation):
				if len(invocation.args[0]) == 0:
					return None
				invocation.args[0].sort(lambda va, vb: self.comparator.compare(va.string, vb.string), reverse = True)
				return invocation.args[0][0]
		mock_cache_adapter.stubs().method("version_max").will(MaxVersionStub(comparator))
		return mock_cache_adapter

	def _create_mock_apt_pkg_module(self):
		mock_apt_pkg_module = self.mock()
		comparator = Advanced_Version_Comparator()
		class ComparatorStub:
			def __init__(self, comparator):
				self.comparator = comparator
			def invoke(self, invocation):
				return self.comparator.compare(invocation.args[0], invocation.args[1])
		mock_apt_pkg_module.stubs().method("VersionCompare").will(ComparatorStub(comparator))
		mock_apt_pkg_module.stubs().InitConfig()
		mock_apt_pkg_module.stubs().InitSystem()
		return mock_apt_pkg_module

	def assertRaisesWithMessageContaining(self, exception_class, message_snippet, method, *args, **kwargs):
		succeeded = False
		try:
			method(*args, **kwargs)
			succeeded = True
		except exception_class, e:
			self.assertContains(e.message, message_snippet)
		except Exception, e:
			self.fail('%s failed with %s(%s) instead of %s' % (method, type(e), e.message, exception_class))
		if succeeded:
			self.fail('%s did not fail with %s' % (method, exception_class))

import mox

class MoxTestCase(mox.MoxTestBase):
	def mock(self):
		"""This is here to mimic the old pmock infrastructure.

		TODO: It should probably be removed at some point to force usage of
		CreateMock(type).
		"""
		return self.mox.CreateMockAnything()

	def functor(self, boolean_functor, desc = ''):
		raise NotImplementedError()
	def assertContains(self, haystack, needle):
		raise NotImplementedError()
	def assertNotContains(self, haystack, needle):
		raise NotImplementedError()
	def assertMatches(self, haystack, regex):
		raise NotImplementedError()
	def _create_mock_facter(self, id):
		raise NotImplementedError()

	def _create_mock_cache_adapter(self):
		raise NotImplementedError()

	def _create_mock_apt_pkg_module(self):
		raise NotImplementedError()

	def assertRaisesWithMessageContaining(self, exception_class, message_snippet, method, *args, **kwargs):
		raise NotImplementedError()

