#!/bin/bash

PYTHONPATH=repo_manager ./nosetests \
--with-coverage --cover-erase --cover-package=repo_manager $*
