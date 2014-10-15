from setuptools import setup, find_packages
from distutils.command.build import build

REQUIREMENTS = [line.strip() for line in open("requirements.txt").readlines()]

setup(name='gitfs',
      version='0.1.0',
      platforms='any',
      description='Mount git repositories as local folders.',
      author='Presslabs',
      author_email='gitfs@gmail.com',
      url='https://github.com/Presslabs/git-fs',
      packages=find_packages(exclude=["tests", "tests.*"]),
      entry_points={'console_scripts': ['gitfs = gitfs:mount']},
      zip_safe=False,
      include_package_data=True,
      install_requires=REQUIREMENTS,
      classifiers=[
          'Programming Language :: Python :: 2.7',
      ])
