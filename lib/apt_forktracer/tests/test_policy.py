#!/usr/bin/python
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
import unittest

from apt_forktracer.testlib import test_helper
from apt_forktracer.apt_pkg_adapter import AptPkgAdapter
from apt_forktracer.config_stanza import ConfigStanza
from apt_forktracer.testlib.fake_package_file import FakePackageFile
from apt_forktracer.package_file_adapter import PackageFileAdapter
from apt_forktracer.policy import Policy
from apt_forktracer.status import Status

	
class TestPolicyBase(test_helper.TestCase):
	def _create_mock_version_adapter(self, version_string):
		if version_string == None:
			return None
		mva = self.mock()
		mva.files = []
		if type(version_string) == tuple:
			mva.string = version_string[0]
			for o in version_string[1]:
				mva.files.append(PackageFileAdapter(FakePackageFile(origin = o)))
		else:
			mva.string = version_string
			mva.files.append(PackageFileAdapter(FakePackageFile(origin = 'Debian')))
		return mva
	def _create_mock_status(self, package, current_version, candidate_version, _official_versions, other_versions = {}):
		official_versions = [self._create_mock_version_adapter(v) for v in _official_versions]
		vbo = {}
		vbo['Debian'] = official_versions
		for o, vers in other_versions.items():
			vbo[o] = [self._create_mock_version_adapter((v, o,)) for v in vers]
		return Status(package, self._create_mock_version_adapter(current_version), self._create_mock_version_adapter(candidate_version), vbo)
	def _create_mock_config(self, hashes):
		stanzas = []
		for hash in hashes:
			stanza = ConfigStanza()
			stanza.set('package', 'apackage', 1)
			stanza.set('accept-origin', hash['accepted_origin'], 2)
			stanza.set('track-origin', hash['track_origin'], 3)
			stanza.set('track-version', hash['track_version'], 4)
			stanza.finish(4)
			stanzas.append(stanza)
		mock_config = self.mock()
		mock_config.stubs().package(pmock.eq('apackage')).will(pmock.return_value(stanzas))
		mock_config.stubs().package(pmock.eq('package_without_config')).will(pmock.return_value([]))
		return mock_config
	def setUp(self):
		self.apt_pkg_adapter = AptPkgAdapter(self._create_mock_apt_pkg_module())
		self.apt_pkg_adapter.init()
		self.mock_facter = self._create_mock_facter('Debian')
		self.set_up_policy_creation()
	def set_up_policy_creation(self):
		self.policy = Policy(self.apt_pkg_adapter, self.mock_facter, self._create_mock_config([]))
	def assert_should_report_yes(self, current_version, candidate_version, official_versions, package = 'apackage', other_versions = {}):
		s = self._create_mock_status(package, current_version, candidate_version, official_versions, other_versions = other_versions)
		self.assert_(self.policy.should_report(s))
	def assert_should_report_NOT(self, current_version, candidate_version, official_versions, package = 'apackage', other_versions = {}):
		s = self._create_mock_status(package, current_version, candidate_version, official_versions, other_versions = other_versions)
		self.assert_(not self.policy.should_report(s))
	def test_missing_version(self):
		self.assert_should_report_yes('2.1~1', None, ['2.1'])
		self.assert_should_report_yes(None, '2.1~1', ['2.1'])
		self.assert_should_report_yes('2.1~1', '2.1~1', [])

class Test_Policy_Base_Version(TestPolicyBase):
	def test_base_version(self):
		self.assertRaises(TypeError, self.policy.base, None)
		self.assertEquals(self.policy.base(''), '')
		self.assertEquals(self.policy.base('1'), '1')
		self.assertEquals(self.policy.base('1~1'), '1')
		self.assertEquals(self.policy.base('1~1~2'), '1~1')

class Test_Policy_Should_Report_With_Same_Candidate_Version_As_Installed(TestPolicyBase):
	def test_official_not_available(self):
		self.assert_should_report_yes('2.1~1', '2.1~1', [])
	def test_candidate_newer_than_available_official(self):
		self.assert_should_report_yes('2.1~1', '2.1~1', ['2.0'])
	def test_candidate_same_as_latest_official(self):
		# This would probably be skipped by Checker, but in case it wasn't, we should not report it.
		self.assert_should_report_NOT('2.1', '2.1', ['2.1'])
		self.assert_should_report_NOT('2.1~1', '2.1~1', ['2.1~1'])
	def test_candidate_derived_directly_from_latest_official(self):
		self.assert_should_report_NOT('2.1~1', '2.1~1', ['2.1'])
	def test_candidate_derived_from_previous_official_version(self):
		self.assert_should_report_yes('2.1~1', '2.1~1', ['2.2', '2.1'])

class Test_Policy_Should_Report_With_Newer_Candidate_Version_Than_Installed(TestPolicyBase):
	"""A candidate version newer than the installed one means that an upgrade
	   is pending. If the _candidate_ version is recent enough not to cause a
	   report, then reporting the status based on the _currently_ installed
	   version will cause noise on machines which have not yet been upgraded.
	   Therefore we report what the situation would be _after_ the upgrade, as
	   the system administrator has other tools to notify her when there are
	   pending upgrades. The VerbosePolicy can be used to display all packages
	   identified by Checker."""
	# none available
	def test_official_not_available(self):
		self.assert_should_report_yes('2.1~1', '2.1~2', [])
	# newer than available
	def test_installed_and_candidate_package_newer_than_available_official(self):
		self.assert_should_report_yes('2.1~1', '2.1~2', ['2.0'])
	def test_installed_package_derived_directly_from_latest_official_while_candidate_is_even_newer(self):
		self.assert_should_report_yes('2.1~1', '2.2~2', ['2.1'])
	# same as or derived from newest available
	def test_installed_and_candidate_package_derived_directly_from_latest_official(self):
		self.assert_should_report_NOT('2.1~1', '2.1~2', ['2.1'])
		self.assert_should_report_NOT('2.1~1', '2.1', ['2.1'])
		self.assert_should_report_NOT('2.1~1', '2.1~2', ['2.1~2'])
	def test_installed_package_derived_from_previous_official_version_while_candidate_derived_from_newest_official(self):
		self.assert_should_report_NOT('2.1~1', '2.2~1', ['2.2', '2.1'])
		self.assert_should_report_NOT('2.1~1', '2.2', ['2.2', '2.1'])
		self.assert_should_report_NOT('2.1~1', '2.2~2', ['2.2~2', '2.1'])
	# older than available
	def test_both_installed_and_candidate_package_derived_from_previous_official_version(self):
		self.assert_should_report_yes('2.1~1', '2.1~2', ['2.2', '2.1'])

class Test_Policy_Should_Report_With_Older_Candidate_Version_Than_Installed(TestPolicyBase):
	"""An older candidate version means that a downgrade is pending. This calls
	   for the same behaviour as described in
	   Test_Policy_Should_Report_With_Newer_Candidate_Version_Than_Installed."""
	# none available
	def test_official_not_available(self):
		self.assert_should_report_yes('2.1~2', '2.1~1', [])
	# newer than available
	def test_both_installed_and_candidate_package_newer_than_available_official(self):
		self.assert_should_report_yes('2.1~2', '2.1~1', ['2.0'])
	# same as or derived from available
	def test_both_installed_and_candidate_package_newer_than_available_official(self):
		self.assert_should_report_NOT('2.1~2', '2.0~1', ['2.0'])
		self.assert_should_report_NOT('2.1~2', '2.0', ['2.0'])
		self.assert_should_report_NOT('2.1~2', '2.0~1', ['2.0~1'])
	# older than available
	def test_installed_package_derived_directly_from_latest_official_while_candidate(self):
		self.assert_should_report_yes('2.1~1', '2.0~1', ['2.1'])


class Test_Policy_With_Config(TestPolicyBase):
	def set_up_policy_creation(self):
		self.policy = Policy(self.apt_pkg_adapter, self.mock_facter,
			self._create_mock_config([
				{'accepted_origin': 'accepted origin', 'track_origin': 'foo', 'track_version': '1.0'},
				{'accepted_origin': 'accepted origin', 'track_origin': 'Debian', 'track_version': '2.0'}]))
	def test_configured_origin_is_ignored(self):
		self.assert_should_report_NOT(('2.2',   ['accepted origin']), ('2.2',   ['accepted origin']), ['2.0'])
		self.assert_should_report_NOT(('2.2',   ['accepted origin']), ('2.2',   ['accepted origin']), ['1.0'], other_versions = {'foo': ['1.0']})
	def test_unconfigured_origin_is_not_ignored(self):
		self.assert_should_report_yes(('2.2',   ['ANOTHER origin']),  ('2.2',   ['ANOTHER origin']),  ['2.0'])
	def test_configured_origin_is_not_ignored_if_official_version_does_not_meet_condition(self):
		# official sources have too new a version
		self.assert_should_report_yes(('2.2',   ['accepted origin']), ('2.2',   ['accepted origin']), ['2.1'])
		# official sources have too old version
		self.assert_should_report_yes(('2.2',   ['accepted origin']), ('2.2',   ['accepted origin']), ['1.9'])
		# official sources have no versions at all
		self.assert_should_report_yes(('2.2',   ['accepted origin']), ('2.2',   ['accepted origin']), [])
	def test_default_rule_not_referenced_if_config_is_provided_for_a_given_package(self):
		self.assert_should_report_yes(('2.0~1', ['ANOTHER origin']),  ('2.0~1', ['ANOTHER origin']),  ['2.0'])
	def test_default_rules_are_referenced_for_packages_without_configuration(self):
		self.assert_should_report_yes(('2.2',   ['ANOTHER origin']),  ('2.2',   ['ANOTHER origin']),  ['2.0'], package = 'package_without_config')
		self.assert_should_report_NOT(('2.0~1', ['ANOTHER origin']),  ('2.0~1', ['ANOTHER origin']),  ['2.0'], package = 'package_without_config')

class Test_Policy_With_Config_Track_Candidate_Version(TestPolicyBase):
	def set_up_policy_creation(self):
		self.policy = Policy(self.apt_pkg_adapter, self.mock_facter, self._create_mock_config([{'accepted_origin': 'accepted origin', 'track_origin': 'Debian', 'track_version': '=candidate'}]))
	def test_configured_origin_is_ignored(self):
		self.assert_should_report_NOT(('2.2',   ['accepted origin']), ('2.2',   ['accepted origin']), ['2.2'])
	def test_unconfigured_origin_is_not_ignored(self):
		self.assert_should_report_yes(('2.2',   ['ANOTHER origin']),  ('2.2',   ['ANOTHER origin']),  ['2.2'])
	def test_configured_origin_is_not_ignored_if_official_version_does_not_meet_condition(self):
		# official sources have too new a version
		self.assert_should_report_yes(('2.2',   ['accepted origin']), ('2.2',   ['accepted origin']), ['2.3'])
		# official sources have too old version
		self.assert_should_report_yes(('2.2',   ['accepted origin']), ('2.2',   ['accepted origin']), ['2.1'])
		# official sources have no versions at all
		self.assert_should_report_yes(('2.2',   ['accepted origin']), ('2.2',   ['accepted origin']), [])
	def test_default_rule_not_referenced_if_config_is_provided_for_a_given_package(self):
		self.assert_should_report_yes(('2.0~1', ['ANOTHER origin']),  ('2.0~1', ['ANOTHER origin']),  ['2.0'])
	def test_default_rules_are_referenced_for_packages_without_configuration(self):
		self.assert_should_report_yes(('2.2',   ['ANOTHER origin']),  ('2.2',   ['ANOTHER origin']),  ['2.0'], package = 'package_without_config')
		self.assert_should_report_NOT(('2.0~1', ['ANOTHER origin']),  ('2.0~1', ['ANOTHER origin']),  ['2.0'], package = 'package_without_config')

class Test_Policy_With_Config_Track_Candidate_Base_Version(TestPolicyBase):
	def set_up_policy_creation(self):
		self.policy = Policy(self.apt_pkg_adapter, self.mock_facter, self._create_mock_config([{'accepted_origin': 'accepted origin', 'track_origin': 'Debian', 'track_version': '=candidate-base'}]))
	def test_configured_origin_is_ignored(self):
		self.assert_should_report_NOT(('2.2~1',   ['accepted origin']), ('2.2~1',   ['accepted origin']), ['2.2'])
	def test_unconfigured_origin_is_not_ignored(self):
		self.assert_should_report_yes(('2.2~1',   ['ANOTHER origin']),  ('2.2~1',   ['ANOTHER origin']),  ['2.2'])
	def test_configured_origin_is_not_ignored_if_official_version_does_not_meet_condition(self):
		# official sources have too new a version
		self.assert_should_report_yes(('2.2~1',   ['accepted origin']), ('2.2~1',   ['accepted origin']), ['2.3'])
		# official sources have too old version
		self.assert_should_report_yes(('2.2~1',   ['accepted origin']), ('2.2~1',   ['accepted origin']), ['2.1'])
		# official sources have no versions at all
		self.assert_should_report_yes(('2.2~1',   ['accepted origin']), ('2.2~1',   ['accepted origin']), [])
	def test_default_rule_not_referenced_if_config_is_provided_for_a_given_package(self):
		self.assert_should_report_yes(('2.0~1', ['ANOTHER origin']),  ('2.0~1', ['ANOTHER origin']),  ['2.0'])
	def test_default_rules_are_referenced_for_packages_without_configuration(self):
		self.assert_should_report_yes(('2.2',   ['ANOTHER origin']),  ('2.2',   ['ANOTHER origin']),  ['2.0'], package = 'package_without_config')
		self.assert_should_report_NOT(('2.0~1', ['ANOTHER origin']),  ('2.0~1', ['ANOTHER origin']),  ['2.0'], package = 'package_without_config')

class Test_Policy_With_Config_For_Non_Debian_Tracked_Origin(TestPolicyBase):
	def set_up_policy_creation(self):
		self.policy = Policy(self.apt_pkg_adapter, self.mock_facter, self._create_mock_config([{'accepted_origin': 'accepted origin', 'track_origin': 'tracked origin', 'track_version': '2.0'}]))
	def test_configured_origin_is_ignored(self):
		self.assert_should_report_NOT(('2.2', ['accepted origin']),  ('2.2',   ['accepted origin']), ['2.0'], other_versions = {'tracked origin': ['2.0']})
	def test_only_configured_origin_is_ignored(self):
		self.assert_should_report_yes(('2.2', ['ANOTHER origin']),   ('2.2',   ['ANOTHER origin']),  ['2.0'], other_versions = {'tracked origin': ['2.0']})
	def test_origin_is_not_ignored_if_tracked_version_does_not_meet_condition(self):
		# tracked origin has too new a version
		self.assert_should_report_yes(('2.2', ['accepted origin']),  ('2.2',   ['accepted origin']), ['2.0'], other_versions = {'tracked origin': ['2.1']})
		# tracked origin has too old version
		self.assert_should_report_yes(('2.2', ['accepted origin']),  ('2.2',   ['accepted origin']), ['2.0'], other_versions = {'tracked origin': ['1.9']})
		# tracked origin has no version at all
		self.assert_should_report_yes(('2.2', ['accepted origin']),  ('2.2',   ['accepted origin']), ['2.0'], other_versions = {'some other origin': ['2.0']})
		self.assert_should_report_yes(('2.2', ['accepted origin']),  ('2.2',   ['accepted origin']), ['2.0'], other_versions = {})
	def test_default_rule_not_referenced_if_config_is_provided_for_a_given_package(self):
		self.assert_should_report_yes(('2.0~1', ['ANOTHER origin']), ('2.0~1', ['ANOTHER origin']),  ['2.0'], other_versions = {'tracked origin': ['2.0']})
	def test_default_rule_IS_referenced_for_packages_without_configuration(self):
		self.assert_should_report_NOT(('2.0~1', ['ANOTHER origin']), ('2.0~1', ['ANOTHER origin']),  ['2.0'], package = 'package_without_config', other_versions = {'tracked origin': ['2.0']})

class Test_Policy_With_Config_For_Any_Accepted_Origin(TestPolicyBase):
	def set_up_policy_creation(self):
		self.policy = Policy(self.apt_pkg_adapter, self.mock_facter, self._create_mock_config([{'accepted_origin': '*', 'track_origin': 'tracked origin', 'track_version': '2.0'}]))
	def test_any_origin_is_ignored(self):
		self.assert_should_report_NOT(('2.2',  ['accepted origin']), ('2.2', ['whatever origin']),  ['2.0'], other_versions = {'tracked origin': ['2.0']})
	def test_origin_is_not_ignored_if_tracked_version_does_not_meet_condition(self):
		# tracked origin has too new a version
		self.assert_should_report_yes(('2.2',  ['accepted origin']), ('2.2', ['whatever origin']),  ['2.0'], other_versions = {'tracked origin': ['2.1']})
		# tracked origin has too old version
		self.assert_should_report_yes(('2.2',  ['accepted origin']), ('2.2', ['whatever origin']),  ['2.0'], other_versions = {'tracked origin': ['1.9']})
		# tracked origin has no version at all
		self.assert_should_report_yes(('2.2',  ['accepted origin']), ('2.2', ['whatever origin']),  ['2.0'], other_versions = {'some other origin': ['2.0']})
		self.assert_should_report_yes(('2.2',  ['accepted origin']), ('2.2', ['whatever origin']),  ['2.0'], other_versions = {})
	def test_default_rule_IS_referenced_for_packages_without_configuration(self):
		self.assert_should_report_NOT(('2.0~1', ['ANOTHER origin']), ('2.0~1', ['ANOTHER origin']), ['2.0'], package = 'package_without_config', other_versions = {'tracked origin': ['2.0']})

class Test_Policy_With_Config_For_Any_Tracked_Origin(TestPolicyBase):
	def set_up_policy_creation(self):
		self.policy = Policy(self.apt_pkg_adapter, self.mock_facter, self._create_mock_config([{'accepted_origin': 'accepted origin', 'track_origin': '*', 'track_version': '2.0'}]))
	def test_origin_is_ignored_if_ANY_origin_meets_condition(self):
		self.assert_should_report_NOT(('2.2', ['accepted origin']), ('2.2', ['accepted origin']), ['2.0'], other_versions = {'whatever origin': ['2.0']})
	def test_origin_is_not_ignored_if_NO_origin_meets_version_condition(self):
		# too new version
		self.assert_should_report_yes(('2.2', ['accepted origin']), ('2.2', ['accepted origin']), ['2.0'], other_versions = {'whatever origin': ['2.1']})
		# too old version
		self.assert_should_report_yes(('2.2', ['accepted origin']), ('2.2', ['accepted origin']), ['2.1'], other_versions = {'whatever origin': ['1.9']})
		# no versions at all
		self.assert_should_report_yes(('2.2', ['accepted origin']), ('2.2', ['accepted origin']), ['2.1'], other_versions = {})
	def test_unconfigured_origin_is_not_ignored(self):
		self.assert_should_report_yes(('2.2', ['accepted origin']), ('2.2', ['ANOTHER origin']),  ['2.0'], other_versions = {'whatever origin': ['2.0']})
	def test_default_rule_IS_referenced_for_packages_without_configuration(self):
		self.assert_should_report_NOT(('2.0~1', ['ANOTHER origin']), ('2.0~1', ['ANOTHER origin']), ['2.0'], package = 'package_without_config', other_versions = {'tracked origin': ['2.0']})

if __name__ == '__main__':
	unittest.main()
