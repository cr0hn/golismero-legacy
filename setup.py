import os

from distutils.core import setup
from platform import system

#
# This code was taken from: http://gpiot.com/blog/creating-a-python-package-and-publish-it-to-pypi/
#
CLASSIFIERS = [
    'Topic :: Security',
    'Environment :: Console',
    'Development Status :: 4 - Beta',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
]

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('admin_tools'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[12:] # Strip "admin_tools/" or "admin_tools\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

# Get requirements
with open(os.path.join(os.path.split(__file__)[0], "requirements.txt"), "rU") as f:
    install_requires = [x.replace("\n", "").replace("\r", "") for x in f.readlines()]

# Get UNIX requirements
if "windows" not in system().lower():
    with open(os.path.join(os.path.split(__file__)[0], "requirements_unix.txt"), "rU") as f:
        install_requires.extend([x.replace("\n", "").replace("\r", "") for x in f.readlines()])

setup(
    name='golismero',
    version='2.0.3',
    packages=packages,
    url='https://github.com/golismero',
    license='GPL2',
    author='GoLismero team',
    author_email='golismero.project@gmail.com',
    description="GoLismero: The web knife. GoLismero is an open source framework for security testing.It's currently \
    geared towards web security, but it can easily be expanded to other kinds of scans.",
    download_url="https://github.com/golismero/golismero/archive/master.zip",
    install_requires=install_requires,
    classifiers=CLASSIFIERS,
    scripts=['golismero.py']
)
