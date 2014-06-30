# -*- coding: utf-8 -*-

"""
# repo_manager - a python module to interact with RPMs repository
#
# Copyright (C) 2014 Red Hat Inc
# Author: Pierre-Yves Chibon <pingou@pingoured.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or (at
# your option) any later version.
# See http://www.gnu.org/copyleft/gpl.html  for the full text of the
# license.
"""

import logging
import rpm
import os
import shutil
import subprocess

TS = rpm.ts()
TS.setVSFlags(rpm._RPMVSF_NOSIGNATURES)

# set up logging to file - see previous section for more details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    filename='/var/tmp/repo_manager.log',
    filemode='a')
# define a Handler which writes INFO messages or higher to the sys.stderr
CSL = logging.StreamHandler()
CSL.setLevel(logging.WARNING)
# set a format which is simpler for console use
# tell the handler to use this format
CSL.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
# add the handler to the root logger
logging.getLogger('').addHandler(CSL)

LOG = logging.getLogger('repo_manager')


def is_rpm(rpmfile):
    ''' Check if the provided rpm is indeed one.
    '''
    if not os.path.isfile(rpmfile):
        return False
    stream = open(rpmfile, 'rb')
    start = stream.read(4)
    stream.close()
    return start == '\xed\xab\xee\xdb'


def get_rpm_headers(rpmfile):
    ''' Open an rpm file and returns the dict containing all its headers
    information.
    '''
    if not is_rpm(rpmfile):
        return
    LOG.debug('get_rpm_headers')
    fd = os.open(rpmfile, os.O_RDONLY)
    headers = TS.hdrFromFdno(fd)
    os.close(fd)
    return headers


def get_rpm_tag(rpmfile, tag):
    ''' Return the specified tags from the headers of the specified rpm tag.
    '''
    LOG.debug('get_rpm_tag')
    LOG.debug('rpmfile :  %s', rpmfile)
    LOG.debug('tag     :  %s', tag)
    headers = get_rpm_headers(rpmfile)
    if headers:
        return headers[tag]


def get_rpm_name(rpmfile):
    ''' Return the name of the rpm according to its headers information.
    '''
    return get_rpm_tag(rpmfile, rpm.RPMTAG_NAME)


def get_rpm_version(rpmfile):
    ''' Return the version of the rpm according to its headers information.
    '''
    return get_rpm_tag(rpmfile, rpm.RPMTAG_VERSION)


def get_rpm_version_release(rpmfile):
    ''' Return the version-release of the rpm according to its headers
    information.
    '''
    vers = get_rpm_tag(rpmfile, rpm.RPMTAG_VERSION),
    rele = get_rpm_tag(rpmfile, rpm.RPMTAG_RELEASE),
    if vers and rele and vers[0] and rele[0]:
        return '%s-%s' % (vers[0], rele[0])


def get_duplicated_rpms(folder):
    ''' Browse all the files in a folder and find out which are RPMs and
    return the RPMs of an application present multiple time.
    '''
    LOG.debug('get_duplicated_rpms')
    folder = os.path.expanduser(folder)

    seen = {}
    for filename in os.listdir(folder):
        if not filename.endswith('.rpm'):
            continue

        filename = os.path.join(folder, filename)
        name = get_rpm_name(filename)
        version = get_rpm_version_release(filename)

        if not name or not version:
            continue

        if name in seen:
            seen[name].append(
                {'version': version, 'filename': filename}
            )
        else:
            seen[name] = [
                {'version': version, 'filename': filename}
            ]

    dups = {}
    for rpmfile in sorted(seen):
        if len(seen[rpmfile]) > 1:
            dups[rpmfile] = seen[rpmfile]
    return dups


def clean_repo(folder, keep=3, srpm=False, dry_run=False,
               no_createrepo=False, createrepo_cmd=None):
    ''' Remove duplicates from a given folder.
    '''
    LOG.debug('clean_repo')
    folder = os.path.expanduser(folder)

    if not os.path.exists(folder):
        print '%s not found' % folder
        return

    before = len(os.listdir(folder))
    dups = get_duplicated_rpms(folder)
    cnt = 0
    if not dry_run:
        LOG.info(
            'Cleaning duplicates files (keeping the last %s) in %s',
            keep, folder)
    for dup in sorted(dups):
        versions = [rpmfile['version'] for rpmfile in sorted(dups[dup])]
        keep_versions = versions[-keep:]
        for rpmfile in sorted(dups[dup]):
            if rpmfile['version'] not in keep_versions:
                cnt += 1
                filename = rpmfile['filename']
                if dry_run:
                    print('Remove file {0}'.format(filename))
                else:
                    LOG.info(
                        'Remove file %s while cleaning the repo', filename)
                    os.unlink(filename)

    srpm_cnt = 0
    if srpm:
        LOG.info('Cleaning duplicates srpm')
        for rpmfile in os.listdir(folder):
            if rpmfile.endswith('.src.rpm'):
                srpm_cnt += 1
                filename = os.path.join(folder, rpmfile)
                if dry_run:
                    print('Remove file {0}'.format(filename))
                else:
                    LOG.info(
                        'Remove file %s while cleaning the repo', filename)
                    os.unlink(filename)

    print folder
    print '  %s files before' % before
    print '  %s RPMs removed' % cnt
    if srpm:
        print '  %s source RPMs removed' % srpm_cnt
    print '  %s files after' % len(os.listdir(folder))

    if not dry_run and not no_createrepo:
        run_createrepo(folder, createrepo_cmd=createrepo_cmd)


def info_repo(folder, keep=3):
    ''' Returns some info/stats about the specified repo.
    '''
    LOG.debug('info_repo')
    folder = os.path.expanduser(folder)

    if not os.path.exists(folder):
        print '%s not found' % folder
        return

    print folder
    cnt_rpm = 0
    cnt_srpm = 0
    for filename in os.listdir(folder):
        if filename.endswith('.src.rpm'):
            cnt_srpm += 1
        elif filename.endswith('.rpm'):
            cnt_rpm += 1

    print '  %s RPMs found' % cnt_rpm
    print '  %s source RPMs found' % cnt_srpm

    dups = get_duplicated_rpms(folder)
    cnt = 0
    for dup in sorted(dups):
        versions = [rpmfile['version'] for rpmfile in sorted(dups[dup])]
        keep_versions = versions[-keep:]
        for rpmfile in sorted(dups[dup]):
            if rpmfile['version'] not in keep_versions:
                cnt += 1

    print '  %s SRPMs/RPMs are present more than %s times and thus could '\
        'be removed' % (cnt, keep)


def add_rpm(rpm, folder, no_createrepo=False, createrepo_cmd=None,
            message=None):
    ''' Copy the provided RPM into the specified folder.
    '''
    LOG.debug('add_rpm')
    rpm = os.path.expanduser(rpm)
    folder = os.path.expanduser(folder)

    # Check input
    if not is_rpm(rpm):
        print '"%s" does not point to a RPM file' % rpm
        return

    # Check destination
    if not os.path.exists(folder):
        print 'Folder "%s" does not exist' % folder
        return
    elif not os.path.isdir(folder):
        print '"%s" is not a folder' % folder
        return

    LOG.info('Adding file "%s", into folder "%s"', rpm, folder)
    if message:
        LOG.info('   Message: %s', message)
    shutil.copy(rpm, folder)

    if not no_createrepo:
        run_createrepo(folder, createrepo_cmd=createrepo_cmd)


def delete_rpm(rpm, folder, no_createrepo=False, createrepo_cmd=None,
               message=None):
    ''' Delete the specified RPM of the specified folder.
    '''
    LOG.debug('delete_rpm')
    rpm = os.path.expanduser(rpm)
    folder = os.path.expanduser(folder)

    # Check input
    path = os.path.join(folder, rpm)
    if not os.path.exists(path):
        print 'File "%s" cannot be found' % path
        return
    if os.path.isdir(path):
        print '"%s" points to a directory' % path
        return

    if not is_rpm(path):
        print '"%s" does not point to a RPM file' % path
        return

    LOG.info('Deleting file "%s"', path)
    if message:
        LOG.info('   Message: %s', message)
    os.unlink(path)

    if not no_createrepo:
        run_createrepo(folder, createrepo_cmd=createrepo_cmd)


def replace_rpm(rpm, folder, no_createrepo=False, createrepo_cmd=None,
                message=None):
    ''' Replace an RPM in a repository, this means replacing an existing
    RPM of the repository by one being exactly the same (same name, version
    and release).
    '''
    LOG.debug('replace_rpm')
    rpm = os.path.expanduser(rpm)
    folder = os.path.expanduser(folder)

    # Check input
    if not is_rpm(rpm):
        print '"%s" does not point to a RPM file' % rpm
        return

    rpmfile = rpm
    if '/' in rpm:
        rpmfile = rpm.rsplit('/', 1)[1]

    delete_rpm(rpmfile, folder, message=message)
    if not no_createrepo:
        run_createrepo(folder, createrepo_cmd=createrepo_cmd)
    add_rpm(rpm, folder, message=message)
    if not no_createrepo:
        run_createrepo(folder, createrepo_cmd=createrepo_cmd)


def ugrade_rpm(rpm, folder_from, folder_to,
               no_createrepo=False, createrepo_cmd=None, message=None):
    ''' Upgrade/copy the specified RPM from one repo into another one.
    '''
    LOG.debug('update_rpm')
    rpm = os.path.expanduser(rpm)
    folder_from = os.path.expanduser(folder_from)
    folder_to = os.path.expanduser(folder_to)

    path = os.path.join(folder_from, rpm)
    # Check input
    if not os.path.exists(path):
        print 'RPM "%s" could not be found' % path
        return
    if not is_rpm(path):
        print '"%s" does not point to a RPM file' % path
        return

    # Check destination
    if not os.path.exists(folder_to):
        print 'Folder "%s" could not be found' % folder_to
        return
    elif not os.path.isdir(folder_to):
        print '"%s" is not a folder' % folder_to
        return

    add_rpm(
        path, folder_to,
        no_createrepo=no_createrepo,
        createrepo_cmd=createrepo_cmd,
        message=message)

    delete_rpm(
        rpm, folder_from,
        no_createrepo=no_createrepo,
        createrepo_cmd=createrepo_cmd,
        message=message)


def run_createrepo(folder, createrepo_cmd=None):
    ''' Run the ``createrepo`` command in the specified folder.
    '''
     # Check destination
    if not os.path.exists(folder):
        print 'Folder "%s" does not exist' % folder
        return
    elif not os.path.isdir(folder):
        print '"%s" is not a folder' % folder
        return

    LOG.debug('run_createrepo')
    cur_wd = os.getcwd()
    os.chdir(folder)
    createrepo_cmd = createrepo_cmd or 'createrepo'
    LOG.info('Run %s on %s', createrepo_cmd, os.getcwd())
    cmd = [createrepo_cmd, '.']
    LOG.debug('  Calling  : `%s` from %s', cmd, folder)
    subprocess.call(' '.join(cmd), shell=True)
    os.chdir(cur_wd)
