# inetsim spec file for Fedora 31
%global debug_package %{nil}

Summary: Internet Services Simulation Suite
Name: inetsim
Version: 1.3.1 
Release: 1%{dist}
License: GPLv2
Group: Applications/Internet
URL: https://www.inetsim.org/
Source0: https://www.inetsim.org/downloads/%{name}-%{version}.tar.gz
Requires: perl-Net-Server perl-Net-DNS perl-Net-DNS-Nameserver perl-IPC-Shareable perl-Digest-SHA perl-IO-Socket-SSL
BuildRequires: perl-interpreter systemd-rpm-macros
Packager: Nobuyuki Ito <info@2ito.com>
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

##############################################################################
# description
##############################################################################
%description
Internet Services Simulation Suite

##############################################################################
# prep
##############################################################################
%prep
%setup -q

##############################################################################
# build
##############################################################################
%build

##############################################################################
# install
##############################################################################
%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

DEST_SYSCONF_DIR=$RPM_BUILD_ROOT%{_sysconfdir}
[[ -d $DEST_SYSCONF_DIR ]] || %{__mkdir_p} $DEST_SYSCONF_DIR
%{__cp} -p ./conf/*.conf $DEST_SYSCONF_DIR/ 

DEST_DATA_DIR=$RPM_BUILD_ROOT%{_datadir}/%{name}-%{version}
[[ -d $DEST_DATA_DIR ]] || %{__mkdir_p} $DEST_DATA_DIR
%{__cp} -pr ./contrib $DEST_DATA_DIR/

DEST_SHARED_STATE_DIR=$RPM_BUILD_ROOT%{_sharedstatedir}/%{name}
[[ -d $DEST_SHARED_STATE_DIR ]] || %{__mkdir_p} $DEST_SHARED_STATE_DIR
%{__cp} -pr ./data $DEST_SHARED_STATE_DIR/

DEST_SBIN_DIR=$RPM_BUILD_ROOT%{_sbindir}
[[ -d $DEST_SBIN_DIR ]] || %{__mkdir_p} $DEST_SBIN_DIR
PERL_VENDORLIB=%{perl_vendorlib}
%{__sed} -r -e '/^use lib/ c use lib "'${PERL_VENDORLIB//\//\\\/}'";' inetsim > $DEST_SBIN_DIR/inetsim

DEST_PERL_VENDORLIB=$RPM_BUILD_ROOT$PERL_VENDORLIB
[[ -d $DEST_PERL_VENDORLIB ]] || %{__mkdir_p} $DEST_PERL_VENDORLIB
%{__cp} -pr ./lib/* $DEST_PERL_VENDORLIB/
%{__cp} -p ./doc/*.pod $DEST_PERL_VENDORLIB/INetSim/

DEST_MAN_DIR=$RPM_BUILD_ROOT%{_mandir}
[[ -d $DEST_MAN_DIR ]] || %{__mkdir_p} $DEST_MAN_DIR
%{__cp} -pr ./man/* $DEST_MAN_DIR/

DEST_LOG_DIR=$RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
[[ -d $DEST_LOG_DIR ]] || %{__mkdir_p} $DEST_LOG_DIR
DEST_REPORT_DIR=$DEST_LOG_DIR/report
[[ -d $DEST_REPORT_DIR ]] || %{__mkdir_p} $DEST_REPORT_DIR

DEST_SYSTEMD_UNIT_DIR=$RPM_BUILD_ROOT%{_unitdir}
[[ -d $DEST_SYSTEMD_UNIT_DIR ]] || %{__mkdir_p} $DEST_SYSTEMD_UNIT_DIR
%{__cat} <<EOF > $DEST_SYSTEMD_UNIT_DIR/%{name}.service
[Unit]
Description=Internet Services Simulation Suite
Documentation=man:inetsim(1) man:inetsim(5)
Wants=network-online.target

[Service]
Type=forking
PIDFile=/run/inetsim.pid
EnvironmentFile=-/etc/sysconfig/inetsim
ExecStart=/usr/sbin/inetsim \$OPTIONS
PrivateTmp=yes
ProtectHome=yes
ProtectSystem=full

[Install]
WantedBy=multi-user.target
EOF

DEST_SYSTEM_CONF_DIR=$RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
[[ -d $DEST_SYSTEM_CONF_DIR ]] || %{__mkdir_p} $DEST_SYSTEM_CONF_DIR/
%{__cat} <<EOF > $DEST_SYSTEM_CONF_DIR/%{name}
# Command-line options for %{name}
OPTIONS="--config=%{_sysconfdir}/%{name}.conf --log-dir=%{_localstatedir}/log/%{name} --data-dir=%{_sharedstatedir}/%{name}/data --report-dir=%{_localstatedir}/log/%{name}/report --pidfile=%{_rundir}/%{name}.pid"
EOF

##############################################################################
# clean
##############################################################################
%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

##############################################################################
# post/postun
##############################################################################
%pre
%{__grep} '^%{name}:' /etc/group >/dev/null
[[ $? -eq 0 ]] || %{_sbindir}/groupadd -r %{name}
%{__grep} '^%{name}:' /etc/passwd >/dev/null
[[ $? -eq 0 ]] || %{_sbindir}/useradd -r -M -g %{name} -s %{_sbindir}/nologin -d %{_sharedstatedir}/%{name} %{name}

%postun
%{__grep} '^%{name}:' /etc/group >/dev/null
[[ $? -eq 0 ]] && %{_sbindir}/userdel %{name}
%{__grep} '^%{name}:' /etc/passwd >/dev/null
[[ $? -eq 0 ]] && %{_sbindir}/groupdel %{name}

##############################################################################
# files
##############################################################################
%files
%defattr(-,root,root)
%doc CHANGES
%license COPYING
%doc DISCLAIMER
%doc LIESMICH
%doc README
%attr(0644, root, inetsim) %config %{_sysconfdir}/*.conf
%attr(0644, root, root) %%config %{_sysconfdir}/sysconfig/%{name}
%{_datadir}/%{name}-%{version}/contrib
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/certs
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/finger
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/ftp/ftproot
%attr(0775, root, inetsim) %{_sharedstatedir}/%{name}/data/ftp/upload
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/http/mime.types
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/http/fakefiles
%attr(0775, root, inetsim) %{_sharedstatedir}/%{name}/data/http/postdata
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/http/wwwroot
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/pop3
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/quotd
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/smtp
%attr(-, root, inetsim) %{_sharedstatedir}/%{name}/data/tftp/tftproot
%attr(0775, root, inetsim) %{_sharedstatedir}/%{name}/data/tftp/upload
%attr(0744, root, root) %{_sbindir}/inetsim
%{perl_vendorlib}/INetSim.pm
%{perl_vendorlib}/INetSim
%{perl_vendorlib}/INetSim/%{name}.*.pod
%{_mandir}
%attr(0770, root, inetsim) %dir %{_localstatedir}/log/%{name}
%attr(0770, root, inetsim) %dir %{_localstatedir}/log/%{name}/report
%attr(0644, root, root) %{_unitdir}/%{name}.service

%changelog
* Mon Nov 4 2019 Nobuyuki Ito <info@2ito.com> - 1.3.1
- Initial version for Fedora 31
