#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: http://golismero-project.com
Golismero project mail: golismero.project<@>gmail.com


This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

__doc__ = """This file defines the methods to deploy and update GoLismero instalations"""


from fabric.api import local, abort, cd, run
from fabric.contrib.files import exists
from fabric.operations import prompt
import datetime
import os.path


REPOSITORIES     = {
    "https://github.com/cr0hn/golismero"                     : "golismero_free",
}

GOLISMERO_HOME = "~/.golismero_deployer"
VERBOSE=False



#----------------------------------------------------------------------
def __git_clone(repo, dst):
    """
    Clone a git repo int dst.

    :param repo: URL of repo to clone.
    :type repo: str

    :param dst: path of destination of clone.
    :type dst: str
    """
    if not isinstance(repo, basestring):
        raise TypeError("Expected bass, got '%s' instead" % type(repo))
    if not isinstance(dst, basestring):
        raise TypeError("Expected basestring, got '%s' instead" % type(dst))

    r = run("git clone %s %s" % (repo, dst))

    if r.failed:
        abort("Error while clonning repo '%s': %s.\n%s" % (repo, r.stderr,r.stdout))

#----------------------------------------------------------------------
def __git_update(repo):
    """
    Updates a git repo.

    :param repo: URL of repo to clone.
    :type repo: str
    """
    if not isinstance(repo, basestring):
        raise TypeError("Expected bass, got '%s' instead" % type(repo))

    if not exists(repo):
        abort("'%s' folder not exists.")

    with cd(repo):
        r = run("git pull")

        if r.failed:
            abort("Error while updating repo '%s': %s." % (repo, r.stderr))

#----------------------------------------------------------------------
def __backup(path, backup):
    """
    Backup a dir into out_dir

    :param path: dir path to backup.
    :type path: str

    :param backup: destination path to store the backup.
    :type backup: str
    """

    m_dst     = "%s/backup_%s.tar.gz" % (backup, datetime.datetime.now().strftime("%Y_%m_%d_%s"))
    m_command = "tar -cvf %s %s" % (m_dst , path)

    print "[*] Making backup of '%s' in '%s'." % (path, m_dst)

    run(m_command, quiet=VERBOSE)

#----------------------------------------------------------------------
def __copy(sources, dest_path):
    """
    Copy golismero files into deploy path

    :param dest_path: destination path.
    :type dest_path: str

    :param sources: golismero sources.
    :type sources: str
    """
    golismero_sources = [ os.path.join(sources, x) for x in REPOSITORIES.values()]

    for src in golismero_sources:
        run("cp -R %s/* %s/ " % (src, dest_path))


#----------------------------------------------------------------------
def __virtual_env_create(deploy_path):
    """
    Creates a virtualenv, copy files and requirements

    :param deploy_path: path folder to deploy.
    :type deploy_path: str
    """
    if exists(deploy_path):
        abort("'%s' already exists" % deploy_path)


    # Creating virtualenv
    print "[*] Generating virtualenv"
    run("virtualenv --no-site-packages %s" % deploy_path, quiet=VERBOSE)

    m_full_path = os.path.join(deploy_path, "golismero")

    # Create golismero folder
    run("mkdir %s" % m_full_path, quiet=VERBOSE)

    # Copy all files to environment
    __copy(GOLISMERO_HOME, m_full_path)

    # Create source for golismero
    with cd(m_full_path):
        # Install dependences
        r = run("source ../bin/activate && pip install -r requirements.txt", shell=False, quiet=VERBOSE)

        if r.failed:
            abort("Error while install requirements: %s" % r.stderr)

#----------------------------------------------------------------------
def __virtual_env_update(deploy_path):
    """
    Creates a virtualenv, copy files and requirements

    :param deploy_path: path folder to deploy.
    :type deploy_path: str
    """
    if not exists(deploy_path):
        abort("'%s' not exists" % deploy_path)

    m_full_path = os.path.join(deploy_path, "golismero")
    with cd(m_full_path):
        # Upgrade depencies
        run("source ../bin/activate && pip install --upgrade -r requirements.txt")



#----------------------------------------------------------------------
def __clone_repositories(base_dir):
    """
    Clone repositories into base_dir

    :param base_dir: path to base dir installation.
    :type base_dir: str
    """
    for url, repo_name in REPOSITORIES.iteritems():

        # Path
        m_path_golismero = os.path.join(base_dir, repo_name)

        # Clone
        if exists(m_path_golismero):
            #r = promt("%s already exists. Would you like to remove and re-install source code?", default="no")
            print "%s already exists" % m_path_golismero
        else:
            print "[*] Cloning golismero %s" % repo_name.replace("_", " ")
            __git_clone(url, m_path_golismero)


#----------------------------------------------------------------------
#
# Availabe actions
#
#----------------------------------------------------------------------
def update(install_dir=None):
    """
    Updates a golismero installation: repositories and desployment.

    :param install_dir: golismero installation path.
    :type install_dir: str
    """
    m_golismero_src = GOLISMERO_HOME

    # Update git repos
    for url, repo_name in REPOSITORIES.iteritems():

        # Path
        m_path_golismero = os.path.join(m_golismero_src, repo_name)

        if not exists(m_path_golismero):
            abort("Directory %s not exists. You should run 'init' first." % m_path_golismero)

        # Update repositories
        __git_update(m_path_golismero)

    if not install_dir:
        return

    if not exists(install_dir):
        abort("'%s' installation dire doesn't exists." % install_dir)

    # Backuping virtual-env
    m_backup_path = os.path.join(m_golismero_src, "backups")
    if not exists(m_backup_path):
        print "Creating backup folder: %s" % m_backup_path
        run("mkdir %s" % m_backup_path)
    __backup(install_dir, m_backup_path)

    m_golismero_env = os.path.join(install_dir, "golismero")
    # Removing old source code
    run("rm -rf %s" % m_golismero_env)
    run("mkdir %s" % m_golismero_env)

    # Copy files to new virtualenv
    __copy(GOLISMERO_HOME, m_golismero_env)

    # Update virtualenv dependences
    __virtual_env_update(install_dir)



#----------------------------------------------------------------------
def init(base_dir):
    """
    FIRST EXECUTION: Creates an initial files and folders for golismero.

    :param base_dir: golismero path installation
    :type base_dir: str
    """
    #if exists(base_dir):
        #abort("'%s' already exists." % base_dir)

    # create repo into thir base_dir
    run("mkdir %s" % base_dir, warn_only=True, quiet=VERBOSE)

    m_home_folder = GOLISMERO_HOME

    # Create folder for repositories
    if not exists(m_home_folder):
        run("mkdir %s" % m_home_folder, warn_only=True, quiet=VERBOSE)

    # Clone repositories
    __clone_repositories(m_home_folder)

    # Copy repositories
    __copy(m_home_folder, base_dir)

#----------------------------------------------------------------------
def start(path):
    """
    Deploy golismero, using virtualenv, in selected path.

    :param path: path location.
    :type path: str
    """
    m_home_folder = GOLISMERO_HOME

    if not exists(m_home_folder):
        abort("'%s' not found. You must run 'init' command first." % m_home_folder)

    # Making virtualenv
    __virtual_env_create(path)


#----------------------------------------------------------------------
def run_devel(path, listen="0.0.0.0", port="9000"):
    """
    Run devel version of golismero as web server mode.

    :param path: installation path.
    :type path: str

    :param port: listen port.
    :type port: int

    :param listen: listen IP
    :type listen: str
    """
    if not exists(GOLISMERO_HOME):
        abort("'%s' not found. You must run 'init' command first." % m_home_folder)

    if not exists(path):
        abort("'%s' not found.")

    m_source_path = os.path.join(path, "golismero")
    with cd(m_source_path):
        run("source ../bin/activate; screen -S golismero_daemon -d -m -L python golismero-daemon.py") # start screen with daemon
        run("source ../bin/activate; screen -S golismer_server -d -m -L python golismero-web.py ") # start screen with web server