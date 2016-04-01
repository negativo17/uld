%global         debug_package %{nil}

Name:           uld
Version:        1.00.37
Release:        1%{?dist}
Summary:        Samsung Printing & Scan Driver
License:        End-user license agreement for Samsung Electronics software product
URL:            http://www.samsung.com/us/support/owners/product/SL-C460W/XAA
ExclusiveArch:  %{ix86} x86_64

Source0:        http://downloadcenter.samsung.com/content/DR/201512/20151210091120064/uld_v1.00.37_00.99.tar.gz
Source1:        %{name}.xml
Source2:        usbresetter.txt

BuildRequires:  chrpath
# Required for defining _udevrulesdir
BuildRequires:  systemd
Requires:       cups-filesystem 
Requires:       firewalld
Requires:       gettext
Requires:       sane-backends%{?_isa}

%description
Samsung Printing & Scan Driver.

%prep
%setup -qn %{name}
cp %{SOURCE2} .

%install
mkdir -p %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_datadir}/cups/model/uld/
mkdir -p %{buildroot}%{_libdir}/sane/
mkdir -p %{buildroot}%{_prefix}/lib/firewalld/services/
mkdir -p %{buildroot}%{_prefix}/lib/cups/backend/
mkdir -p %{buildroot}%{_prefix}/lib/cups/filter/
mkdir -p %{buildroot}%{_sysconfdir}/sane.d/dll.d/
mkdir -p %{buildroot}%{_udevrulesdir}/

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

# Remove RPATH for libscmssc.so
chrpath -d %{buildroot}%{_prefix}/lib/cups/filter/rastertospl

ln -sf libsane-smfp.so.1.0.1 %{buildroot}%{_libdir}/sane/libsane-smfp.so.1
ln -sf libsane-smfp.so.1.0.1 %{buildroot}%{_libdir}/sane/libsane-smfp.so

install -p -m 644 noarch/etc/smfp.conf %{buildroot}%{_sysconfdir}/sane.d/
echo "smfp" > %{buildroot}%{_sysconfdir}/sane.d/dll.d/smfp

# CUPS PPDs
install -p -m 644 noarch/share/ppd/*.ppd %{buildroot}%{_datadir}/cups/model/uld/
gzip -9 %{buildroot}%{_datadir}/cups/model/uld/*

# Firewalld rules
install -D -m 644 -p %{SOURCE1} \
    %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

# UDev rules - look for function fill_full_template() in scanner-script.pkg
source noarch/oem.conf
while read line; do
    eval echo \"$line\" >> %{buildroot}%{_udevrulesdir}/64-smfp.rules
done < noarch/etc/smfp.rules.in

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%{!?_licensedir:%global license %%doc}
%license noarch/license/eula.txt
%doc noarch/oem.conf usbresetter.txt
%config %{_sysconfdir}/sane.d/smfp.conf
%config %{_sysconfdir}/sane.d/dll.d/smfp
# usbresetter takes two arguments: USB vendor id (VID) and USB product id (PID)
%{_bindir}/usbresetter
%{_datadir}/cups/model/uld
%{_libdir}/libscmssc.so
%{_libdir}/sane/libsane-smfp.so*
%{_prefix}/lib/cups/backend/*
%{_prefix}/lib/cups/filter/*
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_udevrulesdir}/64-smfp.rules

%changelog
* Fri Apr 01 2016 Simone Caronni <negativo17@gmail.com> - 1.00.37-1
- Update to 1.00.37.

* Mon Nov 02 2015 Simone Caronni <negativo17@gmail.com> - 1.00.36-1
- Update to 1.00.36_00.91.

* Wed Oct  7 2015 Simone Caronni <negativo17@gmail.com> - 1.00.35-1
- First build.
