# /setup.py
#
# Installation and setup script for travis-container-runner
#
# See LICENCE.md for Copyright information
"""Installation and setup script for travis-runner."""

from setuptools import find_packages
from setuptools import setup

setup(name="travis-container-runner",
      version="0.0.1f",
      description="Travis Container Runner",
      long_description="Opens a .travis.yml and runs the commands in it",
      author="Sam Spilsbury",
      author_email="smspillaz@gmail.com",
      url="http://github.com/polysquare/travis-runner",
      classifiers=["Development Status :: 3 - Alpha",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.1",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4",
                   "Intended Audience :: Developers",
                   "Topic :: Software Development :: Build Tools",
                   "License :: OSI Approved :: MIT License"],
      license="MIT",
      keywords="development linters",
      packages=find_packages(exclude=["tests"]),
      install_requires=["pyaml"],
      extras_require={
          "test": ["coverage",
                   "nose",
                   "nose-parameterized",
                   "testtools"]
      },
      entry_points={
          "console_scripts": [
              "travis-container-runner=traviscontainerrunner.runner:main"
          ]
      },
      test_suite="nose.collector",
      zip_safe=True,
      include_package_data=True)
