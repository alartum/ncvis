from setuptools import Command, setup, find_packages
from setuptools.command.install import install
from setuptools.extension import Extension
from glob import glob

# https://github.com/pypa/setuptools/issues/1347
from os.path import abspath, basename, dirname, join, normpath, relpath
from shutil import rmtree
here = normpath(abspath(dirname(__file__)))
class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    CLEAN_FILES = './build ./dist ./*.pyc ./*.tgz ./*.egg-info ./__pycache__'.split(' ')

    # Support the "all" option. Setuptools expects it in some situations.
    user_options = [
        ('all', 'a',
         "provided for compatibility, has no extra functionality")
    ]

    boolean_options = ['all']

    def initialize_options(self):
        self.all = None

    def finalize_options(self):
        pass

    def run(self):
        global here

        for path_spec in self.CLEAN_FILES:
            # Make paths absolute and relative to this path
            abs_paths = glob(normpath(join(here, path_spec)))
            for path in [str(p) for p in abs_paths]:
                if not path.startswith(here):
                    # Die if path in CLEAN_FILES is absolute + outside this directory
                    raise ValueError("%s is not a path inside %s" % (path, here))
                print('removing %s' % relpath(path))
                rmtree(path)

# Install all dependencies by default
runtime_deps = ['scipy']
deps = []
class InstallCommand(install):
    description = "Adds custom flags to normal install."
    user_options = install.user_options + [
        ('no-deps', None, 'Do not install runtime dependencies.'),
    ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def initialize_options(self):
        super().initialize_options()
        self.no_deps = False
    def finalize_options(self):
        super().finalize_options()
        global deps
        self.no_deps = bool(self.no_deps) 
        if self.no_deps:
            deps = []
        else:
            deps = runtime_deps

try:
    from Cython.Build import cythonize
    import numpy
except ImportError:
    print("numpy and/or cython are not installed:")
    print(">> pip install numpy cython")
    exit(1)

__version__ = "0.0.0"
exec(open('wrapper/_version.py').read())
DISTNAME = 'ncvis'
VERSION = __version__
DESCRIPTION = 'Noise contrastive data visualization'
with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()
MAINTAINER = 'Aleksandr Artemenkov'
MAINTAINER_EMAIL = 'alartum@gmail.com'
URL = 'https://github.com/alartum/ncvis'
LICENSE = 'MIT'
PROJECT_URLS = {
    'Source Code': 'https://github.com/alartum/ncvis'
}

#Add all sources except main
src = glob('src/*.cpp')

import sys
if sys.platform.startswith('darwin'):
    omp_lib = ["omp"]
    omp_flag = ["-fopenmp=libomp"]
elif sys.platform.startswith('linux'):
    omp_lib = ["gomp"]
    omp_flag = ["-fopenmp"]
extensions = [Extension("ncvis",
                        ["wrapper/*.pyx",
                        *src],
                        extra_compile_args=(["-O3", "-std=c++11", "-fpic", "-ffast-math"] + omp_flag),
                        libraries=(['m'] + omp_lib),
                        include_dirs=[numpy.get_include()],
                        language="c++")]

metadata = dict(name=DISTNAME,
                maintainer=MAINTAINER,
                maintainer_email=MAINTAINER_EMAIL,
                description=DESCRIPTION,
                license=LICENSE,
                url=URL,
                project_urls=PROJECT_URLS,
                version=VERSION,
                long_description=LONG_DESCRIPTION,
                long_description_content_type="text/markdown",
                classifiers=['Intended Audience :: Science/Research',
                            'Intended Audience :: Developers',
                            'License :: OSI Approved :: MIT License',
                            'Programming Language :: C++',
                            'Programming Language :: Python :: 3',
                            'Operating System :: OS Independent',
                            ],
                install_requires=deps,
                python_requires=">=3",
                cmdclass={'clean': CleanCommand,
                          'install': InstallCommand,
                })

setup(ext_modules=cythonize(extensions, language_level=3),
      **metadata)