#!/usr/bin/env python

from distutils.core import setup
import sys
import glob

sys.path.append('./src')
from wheremyjamzat.wheremyjamzat import __version__ as wheremyjamzat_version

setup(
	name         = 'WhereMaJamzAt',
	author       = 'Paul Pietkiewicz',
	author_email = 'pawel.pietkiewicz@acm.org',
	description  = 'Get those Jamz',
	license      = 'PSF',
	keywords     = 'download music',
	url          = 'https://github.com/platten/WhereMaJamzAt/',

	version          = wheremyjamzat_version,
	install_requires = ['bs4', 'ID3'],
	packages         = ['wheremyjamzat'],
	package_dir      = {'wheremyjamzat': 'src/wheremyjamzat'},
	scripts          = glob.glob("bin/*")
)
