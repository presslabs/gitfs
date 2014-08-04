from setuptools import setup

requires_list = [
    'Jinja2==2.7.3',
    'MarkupSafe==0.23',
    'PyYAML==3.11',
    'Pygments==1.6',
    'Sphinx==1.2.2',
    'argparse==1.2.1',
    'cffi==0.8.6',
    'docutils==0.11',
    'fusepy==2.0.2',
    'nose==1.3.3',
    'pyaml==14.05.7',
    'pycparser==2.10',
    'pygit2==0.21.0',
    'sphinx-rtd-theme==0.1.6',
    'wsgiref==0.1.2',
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
