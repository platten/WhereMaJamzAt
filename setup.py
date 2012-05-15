#!/usr/bin/env python

from distutils.core import setup
import sys
import glob

sys.path.append('./src')
from wheremajamzat.wheremajamzat import __version__ as wheremajamzat_version

setup(
    name         = 'WhereMaJamzAt',
    author       = 'Paul Pietkiewicz',
    author_email = 'pawel.pietkiewicz@acm.org',
    description  = 'Get those Jamz',
    license      = 'PSF',
    keywords     = 'download music',
    url          = 'https://github.com/platten/WhereMaJamzAt/',

    version          = wheremajamzat_version,
    install_requires = ['bs4', 'ID3'],
    packages         = ['wheremajamzat'],
    package_dir      = {'wheremajamzat': 'src/wheremajamzat'},
    scripts          = glob.glob("bin/*")
)
