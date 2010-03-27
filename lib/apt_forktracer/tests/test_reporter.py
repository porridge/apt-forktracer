#!/usr/bin/python
# apt-forktracer - a utility for managing package versions
# Copyright (C) 2008,2010 Marcin Owsiany <porridge@debian.org>
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
from apt_forktracer.reporter import Reporter
from apt_forktracer.status import Status

class TestReporter(test_helper.TestCase):
	def setUp(self):
		self.reporter = Reporter()

	def testFormattingNoCandidateVersion(self):
		v1 = self.mock()
		v1.string = '1.2'
		status = Status('apackage', v1, None)
		report = self.reporter.format(status)
		self.assertContains(report, '1.2->)')
		self.assertNotContains(report, '[')

	def testFormattingNoCurrentVersion(self):
		v1 = self.mock()
		v1.string = '1.2'
		status = Status('apackage', None, v1)
		report = self.reporter.format(status)
		self.assertContains(report, '(->1.2')
		self.assertNotContains(report, '[')

	def testFormatting(self):
		v1 = self.mock()
		v1.string = '1.2'
		v2 = self.mock()
		v2.string = '1.3'
		v3, v4 = self.mock(), self.mock()
		v3.string = '1.2.3'
		v4.string = 'x.y.z'
		status = Status('apackage', v1, v2, {'Debian': [v3, v4], 'another origin': [v3, v4]})
		report = self.reporter.format(status)
		self.assertContains(report, 'apackage (1.2->1.3) ')
		self.assertContains(report, ' [Debian: 1.2.3 x.y.z]')
		self.assertContains(report, ' [another origin: 1.2.3 x.y.z]')

	def testFormattingSameVersion(self):
		v = self.mock()
		v.string = '1.2'
		status = Status('apackage', v, v)
		report = self.reporter.format(status)
		self.assertNotContains(report, '[')
		self.assertContains(report, 'apackage (1.2)')

	def testReporting(self):
		"""Since this should print to stdout, we don't call it, just check the method's there."""
		mock_status = self.mock()
		self.assert_(self.reporter.report)

if __name__ == '__main__':
	unittest.main()
