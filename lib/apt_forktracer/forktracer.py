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
import apt_pkg
import getopt

from apt_forktracer.apt_pkg_adapter import AptPkgAdapter, NullProgress
from apt_forktracer.cache_adapter import CacheAdapterFactory
from apt_forktracer.checker import Checker
from apt_forktracer.config import Config
from apt_forktracer.config_finder import ConfigFinder
from apt_forktracer.config_parser import ConfigParser
from apt_forktracer.depcache_adapter import DepCacheAdapterFactory
from apt_forktracer.facter import Facter
from apt_forktracer.package_adapter import PackageAdapterFactory
from apt_forktracer.policy import Policy, VerbosePolicy
from apt_forktracer.reporter import Reporter

def run(verbose):
	facter = Facter()
	reporter = Reporter()
	apt_pkg_adapter = AptPkgAdapter(apt_pkg)
	apt_pkg_adapter.init()
	cache_adapter = apt_pkg_adapter.get_cache_adapter(CacheAdapterFactory(), reporter, NullProgress())
	apt_depcache_adapter = apt_pkg_adapter.get_depcache_adapter(DepCacheAdapterFactory())
	package_adapter_factory = PackageAdapterFactory(apt_depcache_adapter)
	checker = Checker(facter, verbose)
	config = Config()
	config_finder = ConfigFinder('/etc/apt/forktracer.conf', '/etc/apt/forktracer.d')
	config_parser = ConfigParser()
	for path, file in config_finder:
		config_parser.load(file, config)
	if verbose:
		policy = VerbosePolicy()
	else:
		policy = Policy(apt_pkg_adapter, facter, config)
	cache_adapter.run(checker, policy, package_adapter_factory)

def main(sys):
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'v', ['verbose'])
	except getopt.GetoptError, err:
		print str(err)
		sys.exit(1)
	verbose = False
	for o, a in opts:
		if o in ('-v', '--verbose'):
			verbose = True
		else:
			assert False, 'unhandled option'
	run(verbose)

