from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from setuptools.command.install_scripts import install_scripts
from setuptools.command.install import install as _install
import os, platform, sys


BAT_TEMPLATE = \
    r"""@echo off
REM wrapper to use shebang first line of {FNAME}

set mypath=%~dp0
set pyscript="%mypath%{FNAME}"
set /p line1=<%pyscript%

if "%line1:~0,2%" == "#!" (goto :goodstart)
echo First line of %pyscript% does not start with "#!"
exit /b 1

:goodstart
set py_exe=%line1:~2%
call "%py_exe%" %pyscript% %*
"""

NO_PYTHON_ERROR = """
WARNING: No #!python executable found in %s, skipping .bat wrapper'"""


printer = print  # noqa: T001

SCRIPTS_TO_INSTALL = 'leds', 'bp-color', 'bp-pid'


class InstallScripts(install_scripts):
    def run(self):
        install_scripts.run(self)
        if not os.name == 'nt':
            return

        for filepath in self.get_outputs():
            # If we can find an executable name in the #! top line of the script
            # file, make .bat wrapper for script.
            with open(filepath, 'rt') as fobj:
                first_line = fobj.readline().lower()

            if not (first_line.startswith('#!') and 'python' in first_line):
                printer(NO_PYTHON_ERROR % filepath)
                continue

            path, fname = os.path.split(filepath)
            froot, ext = os.path.splitext(fname)
            bat_file = os.path.join(path, froot + '.bat')
            bat_contents = BAT_TEMPLATE.replace('{FNAME}', fname)

            printer('Making %s wrapper for %s' % (bat_file, filepath))
            if self.dry_run:
                continue

            with open(bat_file, 'wt') as fobj:
                fobj.write(bat_contents)


# From here: http://pytest.org/2.2.4/goodpractises.html
class RunTests(TestCommand):
    DIRECTORY = 'test'

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [self.DIRECTORY]
        self.test_suite = True

    def run_tests(self):
        # Import here, because outside the eggs aren't loaded.
        import pytest
        errno = pytest.main(self.test_args)
        if errno:
            raise SystemExit(errno)


class RunBenchmark(RunTests):
    DIRECTORY = 'benchmark'


class RunCoverage(RunTests):
    def run_tests(self):
        import coverage
        cov = coverage.Coverage(config_file=True)

        cov.start()
        super().run_tests()
        cov.stop()

        cov.report(file=sys.stdout)
        coverage = cov.html_report(directory='htmlcov')
        fail_under = cov.get_option('report:fail_under')
        if coverage < fail_under:
            printer('ERROR: coverage %.2f%% was less than fail_under=%s%%' % (
                    coverage, fail_under))
            raise SystemExit(1)


def _get_version():
    from os.path import abspath, dirname, join
    filename = join(dirname(abspath(__file__)), 'bibliopixel', 'VERSION')
    return open(filename).read().strip()


if sys.version_info.major != 3:
    printer('leds requires Python 3')
    sys.exit(1)

VERSION = _get_version()

with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()

setup(
    name='leds',
    version=VERSION,
    description=(
        'leds is a pure python library for manipulating a wide variety '
        'of LED strip based displays, both in strip and matrix form.'),
    long_description=open('README.rst').read(),
    author='Tom Ritchford',
    author_email='tom@swirly.com',
    url='http://github.com/rec/leds/',
    license='MIT',
    packages=find_packages(exclude=['test']) + ['ui', 'scripts'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    tests_require=['pytest'],
    cmdclass={
        'benchmark': RunBenchmark,
        'coverage': RunCoverage,
        'test': RunTests,
        'install_scripts': InstallScripts
    },
    include_package_data=True,
    scripts=['scripts/to_install/' + s for s in SCRIPTS_TO_INSTALL],
    install_requires=REQUIRED
)
