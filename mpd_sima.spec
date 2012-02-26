Summary:	Automagically add titles to mpd playlist
Name:		mpd_sima
Version:	0.9.1
Release:	1
License:	GPL v3+
Group:		Applications
Source0:	http://codingteam.net/project/sima/download/file/%{name}_%{version}.tar.xz
# Source0-md5:	45ed7c6078338b0c41f66a87fcd7c75b
Source1:	%{name}.service
Patch0:		man.patch
URL:		http://codingteam.net/project/sima
BuildRequires:	rpm-pythonprov
BuildRequires:	sed >= 4.0
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
Requires:	python-mpd
Requires:	systemd-units >= 37-0.10
Provides:	group(mpd_sima)
Provides:	user(mpd_sima)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
MPD Sima is a python daemon meant to feed MPD playlist with artist
similar to your currently playing track, provided that this artist is
found in MPD library.

This python code allows you to never run out of music when your
playlist queue is getting short.

%prep
%setup -q -n %{name}_%{version}
%patch0 -p1
for f in src/mpd_sima src/simadb_cli; do
	sed -i -e 's=#!/usr/bin/env python=#!/usr/bin/python=' $f
done
for f in data/wrappers/mpd-sima data/wrappers/simadb_cli; do
	sed -i -e 's=#!/usr/bin/env sh=#!/bin/sh=' $f
done

%build
%{__make} PREFIX=%{_prefix}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sharedstatedir}/%{name},%{_sysconfdir},%{systemdunitdir}}

%{__make} install \
	PREFIX=%{_prefix} \
	DESTDIR=$RPM_BUILD_ROOT

install doc/examples/mpd_sima.cfg $RPM_BUILD_ROOT%{_sysconfdir}/mpd-sima.cfg
install %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
%py_comp $RPM_BUILD_ROOT%{_datadir}/mpd-sima
%py_ocomp $RPM_BUILD_ROOT%{_datadir}/mpd-sima
%{__rm} $RPM_BUILD_ROOT%{_datadir}/mpd-sima/{lib,utils}/*.py

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 275 mpd_sima
%useradd -u 275 -r -d /home/services/mpd_sima -s /bin/false -c "MPD_sima user" -g mpd_sima mpd_sima

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove mpd_sima
	%groupremove mpd_sima
fi
%systemd_reload

%files
%defattr(644,root,root,755)
%doc doc/AUTHORS doc/Changelog doc/copyright_holders doc/examples doc/FAQ doc/README.* doc/THANKS doc/sima_db.dia
%attr(600,mpd_sima,mpd_sima) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mpd-sima.cfg
%attr(755,root,root) %{_bindir}/mpd-sima
%attr(755,root,root) %{_bindir}/simadb_cli
%dir %{_datadir}/mpd-sima
%attr(755,root,root) %{_datadir}/mpd-sima/mpd_sima
%attr(755,root,root) %{_datadir}/mpd-sima/simadb_cli
%dir %{_datadir}/mpd-sima/lib
%{_datadir}/mpd-sima/lib/*.py[co]
%dir %{_datadir}/mpd-sima/utils
%{_datadir}/mpd-sima/utils/*.py[co]
%{_mandir}/man1/mpd-sima.1*
%{_mandir}/man1/simadb_cli.1*
%{_mandir}/man5/mpd-sima.cfg.5*
%{systemdunitdir}/%{name}.service
%attr(770,mpd_sima,mpd_sima) %{_sharedstatedir}/mpd_sima
