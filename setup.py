#!/usr/bin/env python
from setuptools import setup
import os
import sys

__doc__ = """Command line tool and library wrapper around '/etc/wpa_supplicant/wpa_supplicant.conf'"""

version = '0.5.4'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires = [
    'setuptools',
    'ifconfig-parser'
]
try:
    import argparse
except:
    install_requires.append('argparse')



should_install_cli = os.environ.get('WPA_PYFI_INSTALL_CLI') not in ['False', '0']
command_name = os.environ.get('WPA_PYFI_CLI_NAME', 'wpa_pyfi')

if command_name == 'wpa_pyfi.py':
    print(
        "Having a command name of wpa_pyfi.py will result in a weird ImportError"
        " that doesn't seem possible to work around. Pretty much any other"
        " name seems to work though."
    )
    sys.exit(1)

entry_points = {}
data_files = []

if should_install_cli:
    entry_points['console_scripts'] = [
        '{command} = wpa_pyfi.cli:main'.format(command=command_name),
    ]
    # make sure we actually have write access to the target folder and if not don't
    # include it in data_files
    if os.access('/etc/bash_completion.d/', os.W_OK):
        data_files.append(('/etc/bash_completion.d/', ['extras/wpa_pyfi_completion.bash']))
    else:
        print("Not installing bash completion because of lack of permissions.")

setup(
    name='wpa_pyfi',
    version=version,
    author='Garrett Hagen, Rocky Meza, Gavin Wahl',
    author_email='garretthagen21@gmail.com',
    description=__doc__,
    url='https://github.com/garretthagen21/wpa_pyfi.git',
    long_description_content_type='text/x-rst',
    long_description='\n\n'.join([read('README.rst'), read('CHANGES.rst')]),
    packages=['wpa_pyfi'],
    entry_points=entry_points,
    test_suite='tests',
    platforms=["Debian"],
    license='BSD',
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Topic :: System :: Networking",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    data_files=data_files
)
