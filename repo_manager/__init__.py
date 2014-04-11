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
