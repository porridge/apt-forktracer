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

class NTimesInvocationMatcher(pmock.InvokedRecorderMatcher):
	def __init__(self, required_count):
		pmock.InvokedRecorderMatcher.__init__(self)
		self._invoked_times = 0
		self._required_count = required_count
	def invoked(self, invocation):
		pmock.InvokedRecorderMatcher.invoked(self, invocation)
		self._invoked_times += 1
	def matches(self, invocation):
		return True
	def verify(self):
		if self._invoked_times != self._required_count:
			raise AssertionError("expected method was invoked %d times, expected %d times" % (self._invoked_times, self._required_count))
	def __str__(self):
		return "expected %d times, invoked %d times" % (self._required_count, self._invoked_times)

