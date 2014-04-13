#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# repo_manager - a commandline application to manage RPMs repository
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

import ConfigParser
import argparse
import logging

import repo_manager


__version__ = '0.1.0'
logging.basicConfig()
LOG = logging.getLogger("repo-manager")


def do_info(args):
    ''' Return information about a repo. '''
    LOG.info("Info")
    LOG.info("repos   : {0}".format(args.repos))
    LOG.info("config  : {0}".format(args.configfile))
    for repo in args.repos:
        repo_manager.info_repo(repo)


def do_add(args):
    ''' Add a rpm to a repository. '''
    LOG.info("Add")
    LOG.info("rpms    : {0}".format(args.rpms))
    LOG.info("repo    : {0}".format(args.repo))
    LOG.info("config  : {0}".format(args.configfile))
    for rpm in args.rpms:
        repo_manager.add_rpm(rpm, args.repo)


def do_clean(args):
    ''' Clean a rpm repository from its duplicates. '''
    LOG.info("Clean")
    LOG.info("repos      : {0}".format(args.repos))
    LOG.info("keep       : {0}".format(args.keep))
    LOG.info("clean_srpm : {0}".format(args.clean_srpm))
    LOG.info("dry_run    : {0}".format(args.dry_run))
    LOG.info("config     : {0}".format(args.configfile))
    for repo in args.repos:
        repo_manager.clean_repo(
            repo,
            keep=args.keep,
            srpm=args.clean_srpm,
            dry_run=args.dry_run)


def do_delete(args):
    ''' Delete a rpm from a repository. '''
    LOG.info("Delete")
    LOG.info("rpms    : {0}".format(args.rpms))
    LOG.info("repo    : {0}".format(args.repo))
    LOG.info("config  : {0}".format(args.configfile))
    for rpm in args.rpms:
        repo_manager.delete_rpm(rpm, args.repo)


def do_replace(args):
    ''' Repleace a rpm of a repository. '''
    LOG.info("Repleace")
    LOG.info("rpms    : {0}".format(args.rpms))
    LOG.info("repo    : {0}".format(args.repo))
    LOG.info("config  : {0}".format(args.configfile))
    for rpm in args.rpms:
        repo_manager.replace_rpm(rpm, args.repo)


def setup_parser():
    '''
    Set the main arguments.
    '''
    parser = argparse.ArgumentParser(prog="repo-manager")
    # General connection options
    parser.add_argument(
        '--config', dest="configfile",
        help="Configuration file to use instead of the default one in "
        "~/.config/repo_manager")
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help="Gives more info about what's going on")
    parser.add_argument(
        '--debug', action='store_true',
        help="Outputs bunches of debugging info")
    parser.add_argument(
        '--version', action='version',
        version='repo-manager %s' % (__version__))

    subparsers = parser.add_subparsers(title='actions')

    ## INFO
    parser_acl = subparsers.add_parser(
        'info',
        help='Provides information / stats about a repo')
    parser_acl.add_argument(
        'repos', default=None, nargs="*",
        help="Repositories to investigate")
    parser_acl.add_argument(
        '--keep', default=3,
        help="Number of RPMs of an application to keep")
    parser_acl.set_defaults(func=do_info)

    ## ADD
    parser_acl = subparsers.add_parser(
        'add',
        help='Add one or more RPMs into a repository')
    parser_acl.add_argument(
        'rpms', default=None, nargs="+",
        help="RPMs to add")
    parser_acl.add_argument(
        '--repo', default=None, nargs="?",
        help="Repository to add the RPMs to")
    parser_acl.set_defaults(func=do_add)

    ## CLEAN
    parser_acl = subparsers.add_parser(
        'clean',
        help='Remove duplicates in the specified, or default, repo')
    parser_acl.add_argument(
        'repos', default=None, nargs="*",
        help="Repositories to clean")
    parser_acl.add_argument(
        '--keep', default=3,
        help="Number of RPMs of an application to keep")
    parser_acl.add_argument(
        '--clean-srpm', default=False, action='store_true',
        help="Clean source rpm from this repository")
    parser_acl.add_argument(
        '--dry-run', default=False, action='store_true',
        help="Does a dry-run, does not delete anything but outputs what it "
        "would do.")
    parser_acl.set_defaults(func=do_clean)

    ## DELETE
    parser_acl = subparsers.add_parser(
        'delete',
        help='delete one or more RPMs into a repository')
    parser_acl.add_argument(
        'rpms', default=None, nargs="+",
        help="RPMs to delete")
    parser_acl.add_argument(
        '--repo', default=None, nargs="?",
        help="Repository to delete the RPMs from")
    parser_acl.set_defaults(func=do_delete)

    ## REPLACE
    parser_acl = subparsers.add_parser(
        'replace',
        help='Replace one or more RPMs in a repository')
    parser_acl.add_argument(
        'rpms', default=None, nargs="+",
        help="RPMs to replace")
    parser_acl.add_argument(
        '--repo', default=None, nargs="?",
        help="Repository to replace the RPMs of")
    parser_acl.set_defaults(func=do_replace)

    return parser


def main():
    ''' Main function of the repo_manager project.
    '''
    # Set up parser for global args
    parser = setup_parser()
    # Parse the commandline
    try:
        arg = parser.parse_args()
    except argparse.ArgumentTypeError, err:
        print "\nError: {0}".format(err)
        return 2

    if arg.debug:
        LOG.setLevel(logging.DEBUG)
    elif arg.verbose:
        LOG.setLevel(logging.INFO)

    return_code = 0

    try:
        arg.func(arg)
    except KeyboardInterrupt:
        print "\nInterrupted by user."
        return_code = 1

    return return_code


if __name__ == '__main__':
    main()
