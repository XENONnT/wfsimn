import ast
import re
import os

from setuptools import setup

PACKAGE_NAME = 'wfsimn'

with open(os.path.join(PACKAGE_NAME, '__init__.py')) as f:
    match = re.search(r'__version__\s+=\s+(.*)', f.read())
version = str(ast.literal_eval(match.group(1)))

setup(
    # metadata
    name=PACKAGE_NAME,
    version=version,

    description='Waveform simulator of neutron Veto in XENONnT',

    # options
    packages=[PACKAGE_NAME],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.4',
    install_requires=[],
    extras_require={
        'dev': [
            'pytest>=3',
            'coverage',
            'tox',
        ],
    },
    entry_points='''
        [console_scripts]
        {app}={pkg}.cli:main
    '''.format(app=PACKAGE_NAME.replace('_', '-'), pkg=PACKAGE_NAME),
    package_data = {PACKAGE_NAME:['data/wave_one_pe_short.csv','data/wave_pedestal_short.csv','data/mc_nsorted_short.root']}
)
