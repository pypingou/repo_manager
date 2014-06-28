repo_manager
============

:Author: Pierre-Yves Chibon <pingou@pingoured.fr>


repo_manager is a small application to manage RPMs repositories.


Get this project:
-----------------
Source:  https://github.com/pypingou/repo_manager


Actions:
--------

* ``Add`` a package to an existing repository.
* ``Remove`` a package from an existing repository.
* ``Clean`` a repository.
  This means remove duplicates while eventually keeping a number of the
  most recent ones for future downgrade.
* ``Upgrade`` a package from a repository into another (for example moving
  from a testing repository into a production one).
* ``Replace`` a package from a repository into another (ie: replacing a
  package in a repository with one having the same `nevr`).
* Get some ``info`` about the repository (number of RPMs, duplicates,
  applications)


License:
--------

This project is licensed GPLv3+.
