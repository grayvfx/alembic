import os
import re
import sys
import platform
import subprocess
import shutil

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

cmake_command = 'cmake'

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        global cmake_command
        try:
            out = subprocess.check_output([cmake_command, '--version'])
            cmake_version = LooseVersion(
                re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.0.0':
                cmake_command = 'cmake3'
                out = subprocess.check_output([cmake_command, '--version'])
                cmake_version = LooseVersion(
                    re.search(r'version\s*([\d.]+)', out.decode()).group(1))

        except OSError:
            raise RuntimeError("CMake3 must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")


        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        # required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep
        
        python_major = str(sys.version_info.major)

        # create the output directory if it doesn't exist yet
        if not os.path.isdir(extdir):
            os.makedirs(extdir)

        # Copy missing dependencies from /usr/local/lib/
        # do this before running expensive cmake build
        if sys.version_info.major >= 3:
            missing_packages = ["iex.so",
                                "imath.so",
                                "imathnumpy.so"]
        else:
            missing_packages = ["iexmodule.la",
                                "iexmodule.so",
                                "imathmodule.la",
                                "imathmodule.so",
                                "imathnumpymodule.la",
                                "imathnumpymodule.so"]
        for package in missing_packages[:]:
            for site_dir in sys.path:
                package_path = os.path.join(site_dir, package)
                if not os.path.isfile(package_path):
                    continue
                shutil.copyfile(package_path, os.path.join(extdir, package))
                print("Copying %s" % package_path)
                del missing_packages[missing_packages.index(package)]
                break

        if missing_packages:
            error = "Unable to find packages: %s" % missing_packages
            # raise Exception(error)

        # build
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable,
                      '-DPYALEMBIC_PYTHON_MAJOR=' + str(sys.version_info.major)]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        cmake_args += ['-DUSE_PYALEMBIC=On']
        subprocess.check_call(
            [cmake_command, ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(
            [cmake_command, '--build', '.'] + build_args, cwd=self.build_temp)


setup(
    name='alembic',
    version='1.8.2', # Needs to be updated manually to match alembic version in CMakeLists.txt
    author='Alembic',
    author_email='',
    description='Alembic is an open framework for storing and sharing scene data that includes a C++ library, a file format, and client plugins and applications.',
    long_description='',
    ext_modules=[CMakeExtension('alembic')],
    install_requires=["numpy"],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
