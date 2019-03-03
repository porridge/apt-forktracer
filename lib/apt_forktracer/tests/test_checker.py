#!/usr/bin/python3
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
import unittest

from apt_forktracer.testlib import test_helper
from apt_forktracer.apt_pkg_adapter import AptPkgAdapter
from apt_forktracer.checker import Checker
from apt_forktracer.testlib.fake_package import FakePackage
from apt_forktracer.testlib.fake_version import FakeVersion
from apt_forktracer.package_adapter import PackageAdapter
from apt_forktracer.version_adapter import VersionAdapter

class CheckerCheckTestCase(test_helper.MoxTestCase):
	"""Common plumbing."""
	def setUp(self):
		super(CheckerCheckTestCase, self).setUp()
		self.fp = FakePackage()
		self.apt_pkg_adapter = AptPkgAdapter(self._create_mock_apt_pkg_module())
		self.apt_pkg_adapter.init()
		self.setUpChecker()
	def setUpChecker(self):
		self.checker = Checker(self._create_mock_facter('Debian'))
	def _prepare_package_with_candidate_from_official_source_and_current_from_unofficial(self):
		self.fp.append_version(FakeVersion._create('1.2.2', ['NotDebian']), True)
		self.fp.append_version(FakeVersion._create('1.2.3', ['Debian']))
		pa = PackageAdapter(self.fp)
		pa.candidate_version = VersionAdapter(FakeVersion._create('1.2.3', ['Debian']))
		return pa
	def _prepare_package_with_candidate_different_from_current(self):
		self.fp.append_version(FakeVersion._create('1.2.3', ['Debian']), True)
		pa = PackageAdapter(self.fp)
		pa.candidate_version = VersionAdapter((FakeVersion._create('1.2.4', ['Debian'])))
		return pa

class GeneralNonVerboseCheckerCheckTest(CheckerCheckTestCase):
	"""Whether a status is returned depends on the CANDIDATE version, not the
	   currently installed one. This is to cut down on noise when machines are
	   behind WRT upgrades."""
	def test_aborts_on_package_without_versions(self):
		pa = PackageAdapter(self.fp)
		self.assertRaises(ValueError, self.checker.check, pa)
	def test_aborts_on_package_without_current_version(self):
		"""CacheAdapter should not pass such objects to us. It's better to know
		in such cases. If there will ever be a need to support this, it can be
		changed."""
		self.fp.append_version(FakeVersion._create('1.2.3', ['Debian']), True)
		pa = PackageAdapter(self.fp)
		pa.candidate_version = pa.current_version
		pa.current_version = None
		self.assertRaises(ValueError, self.checker.check, pa)
	def test_does_not_abort_and_returns_a_status_object_on_package_without_candidate_version(self):
		"""Because a candidate version is always reported by apt in normal
		situations, even when the only known version is installed and not
		available anywhere else. One case where no candidate version is
		reported is when there is a pin which cannot be met."""
		self.fp.append_version(FakeVersion._create('1.2.3', ['Debian']), True)
		pa = PackageAdapter(self.fp)
		pa.candidate_version = None
		status = self.checker.check(pa)
		self.assertTrue(status != None)
	def test_returns_none_in_common_case(self):
		"""Common case means: package with identical, officially-available
		current and candidate versions, which is also the newest available
		version."""
		self.fp.append_version(FakeVersion._create('1.2.3', ['Debian']), True)
		self.fp.append_version(FakeVersion._create('1.2.2', ['Debian']))
		pa = PackageAdapter(self.fp)
		pa.candidate_version = pa.current_version
		self.assertEqual(self.checker.check(pa), None)
	def test_returns_none_in_common_case_when_all_versions_available_additionally_from_unofficial_source(self):
		self.fp.append_version(FakeVersion._create('1.2.3', ['Debian', 'UnOfficial']), True)
		self.fp.append_version(FakeVersion._create('1.2.2', ['Debian', 'UnOfficial']))
		pa = PackageAdapter(self.fp)
		pa.candidate_version = pa.current_version
		self.assertEqual(self.checker.check(pa), None)
	def test_returns_a_status_object_on_package_with_same_current_and_candidate_both_only_locally(self):
		self.fp.current_ver = FakeVersion._create('1.2.3', ['dpkg'])
		pa = PackageAdapter(self.fp)
		pa.candidate_version = pa.current_version
		self.assertTrue(self.checker.check(pa) != None)
	def test_returns_a_status_object_on_package_with_candidate_from_unofficial_source(self):
		self.fp.append_version(FakeVersion._create('1.2.3', ['Unofficial']), True)
		self.fp.append_version(FakeVersion._create('1.2', ['Debian']))
		pa = PackageAdapter(self.fp)
		pa.candidate_version = VersionAdapter(FakeVersion._create('1.2.5', ['NonDebian']))
		status = self.checker.check(pa)
		self.assertTrue(status != None)
		self.assertEqual(status.package_name, 'afake')
		self.assertEqual(status.installed_version.string, '1.2.3')
		self.assertEqual(status.candidate_version.string, '1.2.5')
	def test_package_without_candidate_version_and_current_unofficial(self):
		self.fp.current_ver = FakeVersion._create('1.2.2', ['NotDebian'])
		pa = PackageAdapter(self.fp)
		pa.candidate_version = None
		status = self.checker.check(pa)
		self.assertTrue(status != None)

class NonVerboseCheckerCheckTest(GeneralNonVerboseCheckerCheckTest):
	def test_returns_none_on_package_with_candidate_from_official_source_and_current_from_unofficial(self):
		self.assertEqual(self.checker.check(self._prepare_package_with_candidate_from_official_source_and_current_from_unofficial()), None)
	def test_returns_none_when_candidate_different_from_current(self):
		pa = self._prepare_package_with_candidate_different_from_current()
		self.assertEqual(self.checker.check(pa), None)

class VerboseCheckerCheckTest(GeneralNonVerboseCheckerCheckTest):
	"""Returns None in less cases than in the non-verbose mode."""
	def setUpChecker(self):
		self.checker = Checker(self._create_mock_facter('Debian'), True)
	def test_returns_a_status_object_on_package_with_candidate_from_official_source_and_current_from_unofficial(self):
		status = self.checker.check(self._prepare_package_with_candidate_from_official_source_and_current_from_unofficial())
		self.assertTrue(status != None)
	def test_returns_a_status_object_when_candidate_different_from_current(self):
		pa = self._prepare_package_with_candidate_different_from_current()
		self.assertTrue(self.checker.check(pa) != None)

if __name__ == '__main__':
	unittest.main()
