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

# Runs all tests.
#
# This script must be run from the directory it is in.
# Individual tests may also be executed directly like: ./tests/test_whatever.py
from unittest import TestLoader, TextTestRunner
import sys
sys.path.append('lib')

# The following is ugly, but it's the only method I've found of loading all
# tests from all subpackages of package 'tests', without hardcoding their names
# here.

# We have to import both tests and its subpackages, otherwise dir() does not
# find subpackages.
from apt_forktracer import tests
from apt_forktracer.tests import *

def run_tests(verbosity):
	# Filter out special attributes of the package, to get only subpackages.
	test_names = [n for n in dir(tests) if not n.startswith('__')]
	# Load and run all tests
	all_tests = TestLoader().loadTestsFromNames(test_names, tests)
	TextTestRunner(verbosity=verbosity).run(all_tests)

if __name__ == '__main__':
	if len(sys.argv) == 2:
		run_tests(int(sys.argv[1]))
	else:
		run_tests(1)
