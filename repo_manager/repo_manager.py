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

TS = rpm.ts()
TS.setVSFlags(rpm._RPMVSF_NOSIGNATURES)

logging.basicConfig()
LOG = logging.getLogger("repo_manager")


def get_rpm_headers(rpmfile):
    ''' Open an rpm file and returns the dict containing all its headers
    information.
    '''
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
    return get_rpm_headers(rpmfile)[tag]


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
    return '%s-%s' % (
        get_rpm_tag(rpmfile, rpm.RPMTAG_VERSION),
        get_rpm_tag(rpmfile, rpm.RPMTAG_RELEASE),
    )


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


def clean_repo(folder, keep=3, srpm=False, dry_run=False):
    ''' Remove duplicates from a given folder.
    '''
    LOG.debug('clean_repo')
    folder = os.path.expanduser(folder)

    before = len(os.listdir(folder))
    dups = get_duplicated_rpms(folder)
    cnt = 0
    for dup in sorted(dups):
        versions = [rpmfile['version'] for rpmfile in sorted(dups[dup])]
        keep_versions = versions[-keep:]
        for rpmfile in sorted(dups[dup]):
            if rpmfile['version'] not in keep_versions:
                cnt += 1
                filename = os.path.join(folder, rpmfile['filename'])
                if dry_run:
                    print('Remove file {0}'.format(filename))
                else:
                    LOG.debug('Remove file {0}', filename)
                    os.unlink(filename)


    srpm_cnt = 0
    if srpm:
        for rpmfile in os.listdir(folder):
            if rpmfile.endswith('.src.rpm'):
                srpm_cnt += 1
                filename = os.path.join(folder, rpmfile)
                if dry_run:
                    print('Remove file {0}'.format(filename))
                else:
                    LOG.debug('Remove file %s', filename)
                    os.unlink(filename)

    print folder
    print '  %s files before' % before
    print '  %s RPMs removed' % cnt
    if srpm:
        print '  %s source RPMs removed' % srpm_cnt
    print '  %s files after' % len(os.listdir(folder))


def info_repo(folder, keep=3):
    ''' Returns some info/stats about the specified repo.
    '''
    LOG.debug('info_repo')
    folder = os.path.expanduser(folder)

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

    print '  %s SRPMs/RPMs could be removed' % cnt
