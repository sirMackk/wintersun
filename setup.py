from codecs import open
from os import path

from setuptools import setup

from wintersun import __version__

here = path.abspath(path.dirname(__file__))

# TODO: change rst to readme
# TODO: get install_requires from requirements.txt
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wintersun',
    version=__version__,

    description='Simple static site generator',
    long_description=long_description,

    url='https://github.com/sirmackk/wintersun',
    author='Matt O.',
    author_email='matt@mattscodecave.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='blog static site generator',
    packages=['wintersun'],
    install_requires=['Jinja2', 'Markdown', 'pytz'],
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'sample': ['package_data.dat'],
    },
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'wintersun=wintersun.wintersun:main',
        ],
    },
)
