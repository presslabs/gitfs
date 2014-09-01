from setuptools import setup

requires_list = [
    'cffi==0.8.6',
    'fusepy==2.0.2',
    'pygit2==0.21.2',
]

setup(name='git-fs',
      version='0.01',
      platforms='any',
      description='A FUSE filesystem for git repositories, with local cache',
      author='Presslabs',
      author_email='gitfs@gmail.com',
      url='https://github.com/Presslabs/git-fs',
      packages=['gitfs'],
      entry_points={'console_scripts': ['gitfs = gitfs.mount']},
      include_package_data=True,
      install_requires=requires_list,
      classifiers=[
          'Programming Language :: Python :: 2.7',
      ])
