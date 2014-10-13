from setuptools import setup, find_packages
from distutils.command.build import build

requires_list = [
    'fusepy==2.0.2',
    'pygit2==0.21.3',
]

class CFFIBuild(build):
    """Hack to combat the chicken and egg problem that we need cffi
    to add cffi as an extension.
    """
    def finalize_options(self):
        # This ffi is pygit2.ffi due to the path trick used in the beginning
        # of the file
        from gitfs.utils import atomic

        self.distribution.ext_modules.append(atomic.ffi.verifier.get_extension())
        build.finalize_options(self)


cmdclass = {
    'build': CFFIBuild
}

setup(name='gitfs',
      version='0.0.1',
      platforms='any',
      description='Mount git repositories as local folders.',
      author='Presslabs',
      author_email='gitfs@gmail.com',
      url='https://github.com/Presslabs/git-fs',
      packages=find_packages(exclude=["tests", "tests.*"]),
      entry_points={'console_scripts': ['gitfs = gitfs:mount']},
      zip_safe=False,
      include_package_data=True,
      setup_requires=['cffi'] + requires_list,
      install_requires=requires_list,
      ext_modules=[],
      cmdclass=cmdclass,
      classifiers=[
          'Programming Language :: Python :: 2.7',
      ])
