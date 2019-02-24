# Binary package, no debuginfo should be generated
%global debug_package %{nil}

# If firewalld macro is not defined, define it here:
%{!?firewalld_reload:%global firewalld_reload test -f /usr/bin/firewall-cmd && firewall-cmd --reload --quiet || :}

Name:           uld
Version:        1.00.39
Release:        1%{?dist}
Summary:        Samsung Printing & Scan Driver
License:        End-user license agreement for Samsung Electronics software product
URL:            https://support.hp.com/gb-en/products/printers/samsung-printers
ExclusiveArch:  %{ix86} x86_64

Source0:        https://ftp.hp.com/pub/softlib/software13/printers/SS/SL-M4580FX/uld_V1.00.39_01.17.tar.gz
Source1:        %{name}.xml
Source2:        usbresetter.txt

BuildRequires:  chrpath
# Required for defining _udevrulesdir
BuildRequires:  systemd
Requires:       cups-filesystem 
Requires:       firewalld
Requires:       gettext
Requires:       sane-backends%{?_isa}

# Required for the firewall rules
# http://fedoraproject.org/wiki/PackagingDrafts/ScriptletSnippets/Firewalld
%if 0%{?rhel}
Requires:       firewalld
Requires(post): firewalld
%else
Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
%endif

%description
Samsung Linux Print and Scan Driver.

%prep
%setup -qn %{name}
cp %{SOURCE2} .

%install
mkdir -p %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_datadir}/cups/model/uld/cms/
mkdir -p %{buildroot}%{_datadir}/locale/
mkdir -p %{buildroot}%{_libdir}/sane/
mkdir -p %{buildroot}%{_prefix}/lib/firewalld/services/
mkdir -p %{buildroot}%{_prefix}/lib/cups/backend/
mkdir -p %{buildroot}%{_prefix}/lib/cups/filter/
mkdir -p %{buildroot}%{_sysconfdir}/sane.d/dll.d/
mkdir -p %{buildroot}%{_udevrulesdir}/

# Unfortunately this is hardcoded:
# $ strings x86_64/libsane-smfp.so.1.0.1 | grep oem.conf
# /opt/%s/scanner/share/oem.conf
install -p -m 644 -D noarch/oem.conf %{buildroot}/opt/samsung/scanner/share/oem.conf

# Native components (SANE driver, CUPS driver)
%ifarch x86_64
install -p -m 755 x86_64/usbresetter %{buildroot}%{_bindir}/
install -p -m 755 x86_64/libsane-smfp.so.1.0.1 %{buildroot}%{_libdir}/sane/
install -p -m 755 x86_64/smfpnetdiscovery %{buildroot}%{_prefix}/lib/cups/backend/
install -p -m 755 x86_64/pstosecps %{buildroot}%{_prefix}/lib/cups/filter/
install -p -m 755 x86_64/rastertospl %{buildroot}%{_prefix}/lib/cups/filter/
install -p -m 755 x86_64/libscmssc.so %{buildroot}%{_libdir}/
%endif

%ifarch %{ix86}
install -p -m 755 i386/usbresetter %{buildroot}%{_bindir}/
install -p -m 755 i386/libsane-smfp.so.1.0.1 %{buildroot}%{_libdir}/sane/
install -p -m 755 i386/smfpnetdiscovery %{buildroot}%{_prefix}/lib/cups/backend/
install -p -m 755 i386/pstosecps %{buildroot}%{_prefix}/lib/cups/filter/
install -p -m 755 i386/rastertospl %{buildroot}%{_prefix}/lib/cups/filter/
install -p -m 755 i386/libscmssc.so %{buildroot}%{_libdir}/
%endif

ldconfig -vn %{buildroot}%{_libdir}/sane/

# Remove RPATH for libscmssc.so
chrpath -d %{buildroot}%{_prefix}/lib/cups/filter/rastertospl

# Configuration
install -p -m 644 noarch/etc/smfp.conf %{buildroot}%{_sysconfdir}/sane.d/
echo "smfp" > %{buildroot}%{_sysconfdir}/sane.d/dll.d/smfp

# CUPS PPDs
install -p -m 644 noarch/share/ppd/*.ppd %{buildroot}%{_datadir}/cups/model/uld/
install -p -m 644 noarch/share/ppd/cms/*.cts %{buildroot}%{_datadir}/cups/model/uld/cms/
gzip -9 %{buildroot}%{_datadir}/cups/model/uld/*.ppd

# Firewalld rules
install -D -m 644 -p %{SOURCE1} \
    %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

# UDev rules - look for function fill_full_template() in scanner-script.pkg
source noarch/oem.conf
while read line; do
    eval echo \"$line\" >> %{buildroot}%{_udevrulesdir}/64-smfp.rules
done < noarch/etc/smfp.rules.in

# Locales
cp -frv noarch/share/locale/* %{buildroot}%{_datadir}/locale/
find %{buildroot}%{_datadir}/locale -name install.mo -delete

%find_lang sane-smfp

%post
%?ldconfig
%firewalld_reload

%ldconfig_postun

%files -f sane-smfp.lang
%license noarch/license/eula.txt
%doc usbresetter.txt
%config %{_sysconfdir}/sane.d/smfp.conf
%config %{_sysconfdir}/sane.d/dll.d/smfp
%{_bindir}/usbresetter
%{_datadir}/cups/model/uld
%{_libdir}/libscmssc.so
%{_libdir}/sane/libsane-smfp.so*
%{_prefix}/lib/cups/backend/*
%{_prefix}/lib/cups/filter/*
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_udevrulesdir}/64-smfp.rules
/opt/samsung/scanner/share/oem.conf

%changelog
* Sun Feb 24 2019 Simone Caronni <negativo17@gmail.com> - 1.00.39-1
- Update to V1.00.39_01.17.
- Update SPEC file for Samsung/HP switch.
- Update for packaging guidelines.

* Fri Jan 19 2018 Simone Caronni <negativo17@gmail.com> - 1.00.37-3
- Unfortunately libsane-smfp hardcodes the path of a configuration file in
  /opt/samsung/scanner/share (thanks Piotr Szyszkowski).

* Fri Apr 14 2017 Simone Caronni <negativo17@gmail.com> - 1.00.37-2
- Enable firewalld macros.
- Install localization.
- Use ldconfig for installing libraries.
- Install missing cts files.

* Fri Apr 01 2016 Simone Caronni <negativo17@gmail.com> - 1.00.37-1
- Update to 1.00.37.

* Mon Nov 02 2015 Simone Caronni <negativo17@gmail.com> - 1.00.36-1
- Update to 1.00.36_00.91.

* Wed Oct  7 2015 Simone Caronni <negativo17@gmail.com> - 1.00.35-1
- First build.
