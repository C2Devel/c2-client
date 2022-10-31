%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:    c2-client
Version: 0.13
Release: 1%{?dist}
Summary: CROC Cloud platform API client

Group:   Development/Tools
License: GPLv3
URL:     https://github.com/c2devel/c2-client
Source:  %name-%version.tar.gz

BuildArch:     noarch
BuildRequires: python2-devel
BuildRequires: python-setuptools

Requires: python-setuptools
Requires: python-boto >= 2.46.1
Requires: python-lxml python-six
%if 0%{?rhel} == 6
Requires: python-argparse
%endif
Obsoletes: c2-ec2

%description
Simple command-line utility for sending custom requests to CROC Cloud platform.


%prep
%setup -n %name-%version -q


%build
%__python2 setup.py build


%install
[ "%buildroot" = "/" ] || rm -rf "%buildroot"

%__python2 setup.py install -O1 \
	--skip-build \
	--root "%buildroot" \
	--install-lib="%python2_sitelib"


%files
%defattr(-,root,root,-)
%python2_sitelib/c2client
%python2_sitelib/c2client-*.egg-info

%_bindir/c2-cw
%_bindir/c2-ec2
%_bindir/c2-ct
%doc README.rst


%clean
[ "%buildroot" = "/" ] || rm -rf "%buildroot"


%changelog
* Mon Oct 31 2022 Evgeny Kovalev <aeko.study@gmail.com> - 0.13-1
- New version

* Thu Sep 29 2022 Ivan Konov <plushambush@gmail.com> - 0.12-1
-New version

* Mon Apr 11 2022 Andrey Kulaev <adkulaev@gmail.com> - 0.11-1
- New version

* Fri Jul 02 2021 Andrey Kulaev <adkulaev@gmail.com> - 0.10-1
- New version

* Fri Jul 02 2021 Andrey Kulaev <adkulaev@gmail.com> - 0.9-1
- New version

* Wed Mar 31 2021 Andrey Kulaev <adkulaev@gmail.com> - 0.8-1
- New version

* Mon Dec 02 2019 Andrey Kulaev <adkulaev@gmail.com> - 0.7-1
- New version

* Mon Nov 11 2019 Andrey Kulaev <adkulaev@gmail.com> - 0.6-1
- New version

* Tue Jun 18 2019 Andrey Kulaev <adkulaev@gmail.com> - 0.5-1
- New version.

* Fri Aug 11 2017 Mikhail Ushanov <gm.mephisto@gmail.com> - 0.4-1
- New version.

* Tue Apr 18 2017 Mikhail Ushanov <gm.mephisto@gmail.com> - 0.3-1
- New version.

* Mon Mar 28 2016 Mikhail Ushanov <gm.mephisto@gmail.com> - 0.2-1
- New package.
