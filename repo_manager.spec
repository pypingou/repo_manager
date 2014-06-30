Name:           repo_manager
Version:        0.1.0
Release:        1%{?dist}
Summary:        Manage your RPM repositories easily

License:        GPLv3+
URL:            https://github.com/pypingou/repo_manager
Source0:        https://ambre.pingoured.fr/public/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-argparse
BuildRequires:  python-setuptools
BuildRequires:  createrepo

Requires:       python2
Requires:       python-argparse
Requires:       python-setuptools
Requires:       createrepo


%description
repo_manager allows you to easily manage your RPM repositories. It helps
you add or remove RPMs from your repositories, it allows you to 'upgrade' a
RPM from one repo into another one (for example from testing to prod).
Repo_manager can also give you some information about the state of your
repositories (number of RPMs, SRPMs, duplicates) and clean them (ie: remove
the duplicates while keeping the last X versions available, X being set by
the user).

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install --root=%{buildroot}

# Install the sameple configuration file
mkdir -p %{buildroot}/%{_sysconfdir}/%{name}/
install repo_manager.cfg.sample %{buildroot}/%{_sysconfdir}/%{name}/

%check
%{__python} setup.py test

%files
%doc README.rst LICENSE repo_manager.cfg.sample
%{_sysconfdir}/%{name}/
%{python_sitelib}/%{name}
%{python_sitelib}/%{name}*.egg-info/
%{_bindir}/%{name}

%changelog
* Sat Jun 28 2014 Pierre-Yves Chibon <pingou@pingoured.fr> 0.1.0-1
- First packaging effort
