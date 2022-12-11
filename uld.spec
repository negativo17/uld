# Binary package, no debuginfo should be generated
%global debug_package %{nil}

# If firewalld macro is not defined, define it here:
%{!?firewalld_reload:%global firewalld_reload test -f /usr/bin/firewall-cmd && firewall-cmd --reload --quiet || :}

Name:           uld
Version:        1.00.39.12
Release:        1%{?dist}
Summary:        Samsung/HP Printing & Scan Driver
License:        Proprietary
URL:            https://support.hp.com/us-en/drivers
ExclusiveArch:  aarch64 %{ix86} x86_64

Source0:        https://ftp.hp.com/pub/softlib/software13/printers/MFP170/uld-hp_V1.00.39.12_00.15.tar.gz
Source1:        https://ftp.hp.com/pub/softlib/software13/printers/SS/SL-M4580FX/uld_V1.00.39_01.17.tar.gz
Source2:        %{name}.xml
Source3:        usbresetter.txt
Source4:        tech-menu.txt

BuildRequires:  chrpath
# Required for defining _udevrulesdir
BuildRequires:  systemd
Requires:       cups-filesystem 
Requires:       firewalld
Requires:       gettext
Requires:       sane-backends%{?_isa}

%description
HP and Samsung Unified Linux Driver (ULD) for printers and multifunction
printers (printer and scanner combined).

%prep
%setup -qn %{name}

# Additional Samsung printer drivers from old archive
tar -xzf %{SOURCE1} \
    --strip-components=1 uld/noarch/share uld/noarch/oem.conf \
    --transform s/oem.conf/oem.conf.samsung/

# Additional documents
cp %{SOURCE3} %{SOURCE4} .

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
install -p -m 755 %{_arch}/usbresetter %{buildroot}%{_bindir}/
install -p -m 755 %{_arch}/libsane-smfp.so.1.0.1 %{buildroot}%{_libdir}/sane/
install -p -m 755 %{_arch}/smfpnetdiscovery %{buildroot}%{_prefix}/lib/cups/backend/
install -p -m 755 %{_arch}/pstosecps %{buildroot}%{_prefix}/lib/cups/filter/
install -p -m 755 %{_arch}/rastertospl %{buildroot}%{_prefix}/lib/cups/filter/
install -p -m 755 %{_arch}/libscmssc.so %{buildroot}%{_libdir}/

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
install -D -m 644 -p %{SOURCE2} \
    %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

# UDev rules - look for function fill_full_template() in scanner-script.pkg
source noarch/oem.conf
while read line; do
    eval echo \"$line\" >> %{buildroot}%{_udevrulesdir}/64-smfp-hp.rules
done < noarch/etc/smfp.rules.in

source noarch/oem.conf.samsung
while read line; do
    eval echo \"$line\" >> %{buildroot}%{_udevrulesdir}/64-smfp-samsung.rules
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
%doc usbresetter.txt tech-menu.txt
%config %{_sysconfdir}/sane.d/smfp.conf
%config %{_sysconfdir}/sane.d/dll.d/smfp
%{_bindir}/usbresetter
%{_datadir}/cups/model/uld
%{_libdir}/libscmssc.so
%{_libdir}/sane/libsane-smfp.so.1
%{_libdir}/sane/libsane-smfp.so.1.0.1
%{_prefix}/lib/cups/backend/smfpnetdiscovery
%{_prefix}/lib/cups/filter/pstosecps
%{_prefix}/lib/cups/filter/rastertospl
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_udevrulesdir}/64-smfp-hp.rules
%{_udevrulesdir}/64-smfp-samsung.rules
/opt/samsung/scanner/share/oem.conf

%changelog
* Sat Dec 10 2022 Simone Caronni <negativo17@gmail.com> - 1.00.39.12-1
- Update to 1.00.39.12, using HP driver package and combining in Samsung
  drivers (#1).
- Build also for aarch64.
- Add tech menu document for real (#2).
- Avoid wildcards in file list.
- Update SPEC file for new HP information.

* Fri Sep 24 2021 Simone Caronni <negativo17@gmail.com> - 1.00.39-2
- Simplify SPEC file.
- Add document to access the tech menu.

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
