%global forgeurl https://github.com/waydroid/waydroid
%global debug_package %{nil}
%global selinuxtype targeted

Version:        1.3.3
%global tag %{version}

%forgemeta
Name:           waydroid
Release:        101%{?dist}
Summary:        waydroid
License:        GPL-3.0-only
URL:            %{forgeurl}
Source:         %{forgesource}
Source1:        waydroid.te
Source2:        waydroid-gbinder.conf
Source3:        waydroid-container.service
Source4:        dev-binderfs.mount
Source5:        95-waydroid.preset
Source6:        waydroid.fc
Patch0:         setup-firealld.patch

BuildRequires:  make
BuildRequires:  selinux-policy-devel
BuildRequires:  systemd
BuildRequires:  python3-devel
BuildRequires:  systemd-rpm-macros

Requires:       python-gbinder >= 1.1.0
Requires:       python-gobject
Requires:       lxc
Requires:       gtk3
Requires:       (%{name}-selinux = %{version}-%{release} if selinux-policy-targeted)
Requires:       nftables iproute dnsmasq
Recommends:     python-pyclip
Recommends:     wl-clipboard

%description
A container-based approach to boot a full Android system on a regular GNU/Linux system.

%package selinux
Summary:            SELinux policy module required tu run waydroid
BuildArch:          noarch
Requires:           container-selinux
%{?selinux_requires}

%description selinux
This package contains SELinux policy module necessary to run waydroid.

%prep
%forgeautosetup -p1
mkdir SELinux
cp %{S:1} SELinux/
cp %{S:6} SELinux/

%build
# Remove link for ROM files
# sed -i -e '/"system_channel":/ s/: ".*"/: ""/' tools/config/__init__.py
# sed -i -e '/"vendor_channel":/ s/: ".*"/: ""/' tools/config/__init__.py
# Compile sepolicy
cd SELinux
%{__make} NAME=%{selinuxtype} -f /usr/share/selinux/devel/Makefile

%install
%make_install LIBDIR=%{_libdir} DESTDIR=%{buildroot} USE_SYSTEMD=0 USE_NFTABLES=1
%py_byte_compile %{python3} %{buildroot}%{_prefix}/lib/waydroid
%{__install} -d %{buildroot}%{_unitdir} %{buildroot}%{_systemd_util_dir}/system-preset
%{__install} -d %{buildroot}%{_datadir}/selinux/%{selinuxtype}
%{__install} -p -m 644 %{S:3} %{buildroot}%{_unitdir}/
%{__install} -p -m 644 %{S:4} %{buildroot}%{_unitdir}/
%{__install} -p -m 644 %{S:5} %{buildroot}%{_systemd_util_dir}/system-preset/
%{__install} -p -m 644 SELinux/%{name}.pp %{buildroot}%{_datadir}/selinux/%{selinuxtype}/%{name}.pp

%pre selinux
%selinux_relabel_pre -s %{selinuxtype}

%post selinux
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/%{selinuxtype}/%{name}.pp

%posttrans selinux
%selinux_relabel_post -s %{selinuxtype}

%postun selinux
if [ $1 -eq 0 ] ; then
  %selinux_modules_uninstall -s %{selinuxtype} %{name}
fi

%posttrans
waydroid upgrade -o >/dev/null
%systemd_post waydroid-container.service
if [ $1 -eq 1 ] && [ -x /usr/bin/systemctl ]; then
  /usr/bin/systemctl start waydroid-container.service || :
fi

%preun
%systemd_preun waydroid-container.service

%postun
%systemd_postun_with_restart waydroid-container.service

%triggerin -- %{name} < 1.2.1-13
/usr/lib/systemd/systemd-update-helper mark-restart-system-units waydroid-container.service || :

%files
%license LICENSE
%doc README.md
%{_prefix}/lib/waydroid
%{_datadir}/applications/Waydroid.desktop
%{_datadir}/applications/waydroid.market.desktop
%{_datadir}/metainfo/id.waydro.waydroid.metainfo.xml
%{_bindir}/waydroid
%{_unitdir}/waydroid-container.service
%{_unitdir}/dev-binderfs.mount
%{_systemd_util_dir}/system-preset/95-waydroid.preset

%files selinux
%doc SELinux/%{name}.te
%{_datadir}/selinux/targeted/%{name}.pp

%changelog
* Mon Oct 3 2022 Mosaab Alzoubi <mosaab[AT]parmg[DOT]sa> - 1.3.3-101
- Built for Ruya OS.

* Sun Sep 25 2022 Alessandro Astone <ales.astone@gmail.com> - 1.3.3-1
- Update to 1.3.3

* Fri Sep 02 2022 Alessandro Astone <ales.astone@gmail.com> - 1.3.1-1
- Update to 1.3.1

* Tue Aug 09 2022 Alessandro Astone <ales.astone@gmail.com> - 1.3.0-1
- Update to 1.3.0

* Sun Apr 17 2022 Alessandro Astone <ales.astone@gmail.com> - 1.2.1-1
- Update to 1.2.1

* Mon Mar 07 2022 Alessandro Astone <ales.astone@gmail.com> - 1.2.0-7.20220307git1.2.0
- Recommend pyclip

* Sat Feb 26 2022 Alessandro Astone <ales.astone@gmail.com> - 1.2.0-5.20220226git1.2.0
- Add sepolicy for crash handler

* Fri Feb 25 2022 Alessandro Astone <ales.astone@gmail.com> - 1.2.0-4.20220225git1.2.0
- Respin package

* Wed Aug 12 2020 Qiyu Yan <yanqiyu@fedoraproject.org> - 0-0.1.20200811gitc87ea48
- initial package
