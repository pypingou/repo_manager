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

Unit-tests
"""

import unittest
import shutil
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import repo_manager
import repo_manager.repo_manager as repomgr


REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repo')
TEST_REPO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'repo_test')
TEST_REPO2 = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'repo_test2')


class RepoManagertests(unittest.TestCase):
    """ RepoManager tests. """

    # pylint: disable=C0103
    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        shutil.copytree(REPO, TEST_REPO)
        shutil.copytree(REPO, TEST_REPO2)

    # pylint: disable=C0103
    def tearDown(self):
        """ Remove the test.db database if there is one. """
        if os.path.exists(TEST_REPO):
            shutil.rmtree(TEST_REPO)
        if os.path.exists(TEST_REPO2):
            shutil.rmtree(TEST_REPO2)

    def test_is_rpm(self):
        """ Test the repo_manager.is_rpm function. """

        self.assertFalse(repomgr.is_rpm(TEST_REPO))
        self.assertTrue(repomgr.is_rpm(os.path.join(
            TEST_REPO, 'fedocal-0.5.1-1.el6.src.rpm')))

    def test_get_rpm_name(self):
        """ Test the repo_manager.get_rpm_name function. """

        self.assertEqual(repomgr.get_rpm_name(TEST_REPO), None)
        self.assertEqual(repomgr.get_rpm_name(os.path.join(
            TEST_REPO, 'fedocal-0.5.1-1.el6.src.rpm')), 'fedocal')

    def test_get_rpm_version(self):
        """ Test the repo_manager.get_rpm_version function. """

        self.assertEqual(repomgr.get_rpm_version(TEST_REPO), None)
        self.assertEqual(repomgr.get_rpm_version(os.path.join(
            TEST_REPO, 'fedocal-0.6.0-1.el6.src.rpm')), '0.6.0')

    def test_get_rpm_version_release(self):
        """ Test the repo_manager.get_rpm_version_release function. """

        self.assertEqual(
            repomgr.get_rpm_version_release(TEST_REPO), None)
        self.assertEqual(repomgr.get_rpm_version_release(os.path.join(
            TEST_REPO, 'fedocal-0.6.1-1.el6.src.rpm')), '0.6.1-1.el6')

    def test_get_duplicated_rpms(self):
        """ Test the repo_manager.get_duplicated_rpms function. """

        # Create an empty file
        emptyfile = os.path.join(TEST_REPO, 'tmp')
        stream = open(emptyfile, 'w')
        stream.close()

        # Create another empty file but ending with .rpm
        emptyfile = os.path.join(TEST_REPO, 'fake.rpm')
        stream = open(emptyfile, 'w')
        stream.close()

        obs = repomgr.get_duplicated_rpms(TEST_REPO)
        self.assertEqual(sorted(obs.keys()), ['fedocal', 'pkgdb2'])
        pkgdb2_versions = [el['version'] for el in obs['pkgdb2']]
        self.assertEqual(
            sorted(pkgdb2_versions),
            [
                '0.5-1.el6',
                '0.6-1.el6',
                '0.7-1.el6',
                '0.8-1.el6',
            ]
        )

    def test_clean_repo(self):
        """ Test the repo_manager.clean_repo function. """
        # Before cleaning
        exp = [
            'fedocal-0.5.0-1.el6.src.rpm',
            'fedocal-0.5.1-1.el6.src.rpm',
            'fedocal-0.6.0-1.el6.src.rpm',
            'fedocal-0.6.1-1.el6.src.rpm',
            'pkgdb2-0.5-1.el6.src.rpm',
            'pkgdb2-0.6-1.el6.src.rpm',
            'pkgdb2-0.7-1.el6.src.rpm',
            'pkgdb2-0.8-1.el6.src.rpm',
        ]
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

        # Dry run
        obs = repomgr.clean_repo(TEST_REPO, dry_run=True, srpm=True)
        # No changes
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

        # Clean RPMs
        obs = repomgr.clean_repo('Fake')
        self.assertEqual(obs, None)

        obs = repomgr.clean_repo(TEST_REPO)
        self.assertEqual(obs, None)

        # After cleaning
        files = os.listdir(TEST_REPO)
        self.assertEqual(
            sorted(files),
            [
                'fedocal-0.5.1-1.el6.src.rpm',
                'fedocal-0.6.0-1.el6.src.rpm',
                'fedocal-0.6.1-1.el6.src.rpm',
                'pkgdb2-0.6-1.el6.src.rpm',
                'pkgdb2-0.7-1.el6.src.rpm',
                'pkgdb2-0.8-1.el6.src.rpm',
                'repodata'
            ]
        )

        # Remove all the src.rpm when cleaning the repo
        obs = repomgr.clean_repo(TEST_REPO, srpm=True)

        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), ['repodata'])

    def test_info_repo(self):
        """ Test the repo_manager.info_repo function. """
        self.assertEqual(repomgr.info_repo(TEST_REPO), None)

        obs = repomgr.info_repo('fake')
        self.assertEqual(obs, None)

    def test_delete_rpm(self):
        """ Test the repo_manager.delete_rpm function. """

        # Before delete
        exp = [
            'fedocal-0.5.0-1.el6.src.rpm',
            'fedocal-0.5.1-1.el6.src.rpm',
            'fedocal-0.6.0-1.el6.src.rpm',
            'fedocal-0.6.1-1.el6.src.rpm',
            'pkgdb2-0.5-1.el6.src.rpm',
            'pkgdb2-0.6-1.el6.src.rpm',
            'pkgdb2-0.7-1.el6.src.rpm',
            'pkgdb2-0.8-1.el6.src.rpm',
        ]
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

        # Create another empty file but ending with .rpm
        emptyfile = os.path.join(TEST_REPO, 'fake.rpm')
        stream = open(emptyfile, 'w')
        stream.close()

        repomgr.delete_rpm('fakefile', TEST_REPO)
        repomgr.delete_rpm(TEST_REPO, TEST_REPO)
        repomgr.delete_rpm('fake.rpm', TEST_REPO)
        repomgr.delete_rpm(
            'fedocal-0.6.1-1.el6.src.rpm', TEST_REPO, message='unit-tests')

        # After delete
        exp = [
            'fake.rpm',
            'fedocal-0.5.0-1.el6.src.rpm',
            'fedocal-0.5.1-1.el6.src.rpm',
            'fedocal-0.6.0-1.el6.src.rpm',
            'pkgdb2-0.5-1.el6.src.rpm',
            'pkgdb2-0.6-1.el6.src.rpm',
            'pkgdb2-0.7-1.el6.src.rpm',
            'pkgdb2-0.8-1.el6.src.rpm',
            'repodata',
        ]
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

    def test_add_rpm(self):
        """ Test the repo_manager.add_rpm function. """

        self.test_delete_rpm()

        # Before adding
        exp = [
            'fake.rpm',
            'fedocal-0.5.0-1.el6.src.rpm',
            'fedocal-0.5.1-1.el6.src.rpm',
            'fedocal-0.6.0-1.el6.src.rpm',
            'pkgdb2-0.5-1.el6.src.rpm',
            'pkgdb2-0.6-1.el6.src.rpm',
            'pkgdb2-0.7-1.el6.src.rpm',
            'pkgdb2-0.8-1.el6.src.rpm',
            'repodata',
        ]
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

        # test wrong inputs
        repomgr.add_rpm('fakefile', TEST_REPO)
        repomgr.add_rpm(TEST_REPO, TEST_REPO)
        repomgr.add_rpm('fake.rpm', TEST_REPO)
        repomgr.add_rpm(
            os.path.join(REPO, 'fedocal-0.6.1-1.el6.src.rpm'),
            'fakefolder')
        repomgr.add_rpm(
            os.path.join(REPO, 'fedocal-0.6.1-1.el6.src.rpm'),
            os.path.join(TEST_REPO, 'fake.rpm'))

        # Valid inputs
        repomgr.add_rpm(
            os.path.join(REPO, 'fedocal-0.6.1-1.el6.src.rpm'),
            TEST_REPO, message='unit-tests')

        # After delete
        exp = [
            'fake.rpm',
            'fedocal-0.5.0-1.el6.src.rpm',
            'fedocal-0.5.1-1.el6.src.rpm',
            'fedocal-0.6.0-1.el6.src.rpm',
            'fedocal-0.6.1-1.el6.src.rpm',
            'pkgdb2-0.5-1.el6.src.rpm',
            'pkgdb2-0.6-1.el6.src.rpm',
            'pkgdb2-0.7-1.el6.src.rpm',
            'pkgdb2-0.8-1.el6.src.rpm',
            'repodata',
        ]
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

    def test_replace_rpm(self):
        """ Test the repo_manager.replace_rpm function. """

        # Before replacing
        exp = [
            'fedocal-0.5.0-1.el6.src.rpm',
            'fedocal-0.5.1-1.el6.src.rpm',
            'fedocal-0.6.0-1.el6.src.rpm',
            'fedocal-0.6.1-1.el6.src.rpm',
            'pkgdb2-0.5-1.el6.src.rpm',
            'pkgdb2-0.6-1.el6.src.rpm',
            'pkgdb2-0.7-1.el6.src.rpm',
            'pkgdb2-0.8-1.el6.src.rpm',
        ]
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

        # test wrong inputs
        repomgr.replace_rpm('fakefile', TEST_REPO)
        repomgr.replace_rpm(TEST_REPO, TEST_REPO)
        repomgr.replace_rpm('fake.rpm', TEST_REPO)
        repomgr.replace_rpm(
            os.path.join(REPO, 'fedocal-0.6.1-1.el6.src.rpm'),
            'fakefolder')
        repomgr.replace_rpm(
            os.path.join(REPO, 'fedocal-0.6.1-1.el6.src.rpm'),
            os.path.join(TEST_REPO, 'fake.rpm'))

        # Valid inputs
        repomgr.replace_rpm(
            os.path.join(REPO, 'fedocal-0.6.1-1.el6.src.rpm'),
            TEST_REPO, message='unit-tests')

        # After replacing
        exp = [
            'fedocal-0.5.0-1.el6.src.rpm',
            'fedocal-0.5.1-1.el6.src.rpm',
            'fedocal-0.6.0-1.el6.src.rpm',
            'fedocal-0.6.1-1.el6.src.rpm',
            'pkgdb2-0.5-1.el6.src.rpm',
            'pkgdb2-0.6-1.el6.src.rpm',
            'pkgdb2-0.7-1.el6.src.rpm',
            'pkgdb2-0.8-1.el6.src.rpm',
            'repodata',
        ]
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

    def test_ugrade_rpm(self):
        """ Test the repo_manager.ugrade_rpm function. """

        self.test_delete_rpm()

        # Before Upgrading
        exp = [
            'fake.rpm',
            'fedocal-0.5.0-1.el6.src.rpm',
            'fedocal-0.5.1-1.el6.src.rpm',
            'fedocal-0.6.0-1.el6.src.rpm',
            'pkgdb2-0.5-1.el6.src.rpm',
            'pkgdb2-0.6-1.el6.src.rpm',
            'pkgdb2-0.7-1.el6.src.rpm',
            'pkgdb2-0.8-1.el6.src.rpm',
            'repodata',
        ]
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

        # test wrong inputs
        repomgr.ugrade_rpm('fakefile', TEST_REPO, TEST_REPO2)
        repomgr.ugrade_rpm(TEST_REPO, 'fakefile', TEST_REPO2)
        repomgr.ugrade_rpm('fake.rpm', TEST_REPO, TEST_REPO2)

        repomgr.ugrade_rpm(
            'fedocal-0.6.1-1.el6.src.rpm',
            'fakefolder', TEST_REPO)
        repomgr.ugrade_rpm(
            'fedocal-0.6.1-1.el6.src.rpm',
            TEST_REPO2, 'fakefolder')
        repomgr.ugrade_rpm(
            'fedocal-0.6.1-1.el6.src.rpm',
            TEST_REPO2, os.path.join(TEST_REPO, 'fake.rpm'))

        # Valid inputs
        repomgr.ugrade_rpm(
            'fedocal-0.6.1-1.el6.src.rpm',
            TEST_REPO2, TEST_REPO, message='unit-tests')

        # After upgrading
        exp = [
            'fake.rpm',
            'fedocal-0.5.0-1.el6.src.rpm',
            'fedocal-0.5.1-1.el6.src.rpm',
            'fedocal-0.6.0-1.el6.src.rpm',
            'fedocal-0.6.1-1.el6.src.rpm',
            'pkgdb2-0.5-1.el6.src.rpm',
            'pkgdb2-0.6-1.el6.src.rpm',
            'pkgdb2-0.7-1.el6.src.rpm',
            'pkgdb2-0.8-1.el6.src.rpm',
            'repodata',
        ]
        files = os.listdir(TEST_REPO)
        self.assertEqual(sorted(files), exp)

    def test_run_createrepo(self):
        """ Test the repo_manager.run_createrepo function. """

        self.assertEqual(repomgr.run_createrepo('Fake'), None)
        self.assertEqual(
            repomgr.run_createrepo(
                os.path.join(REPO, 'fedocal-0.6.1-1.el6.src.rpm')),
            None)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(RepoManagertests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
