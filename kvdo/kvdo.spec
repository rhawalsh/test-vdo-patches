%define spec_release 3

%global commit 72f94c2d858e4baabeba72bc3551287a2dd45d87
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%define kmod_name		kvdo
%define kmod_driver_version	6.2.7.17
%define kmod_rpm_release	%{spec_release}
%define kmod_kernel_version	3.10.0-693.el7

# Disable the scanning for a debug package
%global debug_package %{nil}

Name:		kmod-kvdo
Version:	%{kmod_driver_version}
Release:	%{kmod_rpm_release}%{?dist}
Summary:	Kernel Modules for Virtual Data Optimizer
License:	GPLv2+

# pointed at the fork
URL:		https://github.com/dm-vdo/kvdo

Source0:        %{url}/archive/%{commit}/%{kmod_name}-%{shortcommit}.tar.gz

Patch0001: 0001-Removed-unneeded-import-of-stddef.h.patch
Patch0002: 0002-Removed-fixed-stdarg.h-imports.patch
Patch0003: 0003-Update-time-types-for-newer-kernels.patch
Patch0004: 0004-Fixed-GCC-implicit-fallthrough-errors-when-building-.patch
Patch0005: 0005-Removed-unneeded-casts-to-KvdoWorkFunction.patch
Patch0006: 0006-Added-IMA-statustype-for-5.15-kernels-emitting-the-n.patch
Patch0007: 0007-Removed-usage-of-removed-elevator-constants.patch
Patch0008: 0008-Update-procfs-args-for-kernel-5.6-and-above.patch
Patch0009: 0009-Adapt-PDE_DATA-to-kernel-5.17.patch
Patch0010: 0010-Update-__vmalloc-signature-for-5.8-kernels.patch
Patch0011: 0011-Adapt-complete-and-exit-signature-for-5.17-kernel.patch
Patch0012: 0012-Eliminated-obsolete-function-smp_read_barrier_depend.patch
Patch0013: 0013-Removed-export-of-currentTime.patch
Patch0014: 0014-Adapted-new-bio_reset-signature.patch
Patch0015: 0015-Adapted-to-new-bio_alloc_bioset-signature.patch
Patch0016: 0016-More-kobj-conversions.patch
Patch0017: 0017-More-kobj-conversions.patch
Patch0018: 0018-Adapted-to-dm-bufio-API-change.patch
Patch0019: 0019-Replace-prandom_bytes-with-get_random_bytes.patch
Patch0020: 0020-Switched-from-bdevname-to-the-magic-pg-prink-format.patch

BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Requires:       dkms
Requires:	kernel-devel >= %{kmod_kernel_version}
Requires:       make
%if 0%{?fedora}
# Fedora requires elfutils-libelf-devel, while rhel does not.
BuildRequires:  elfutils-libelf-devel
%endif
BuildRequires:	glibc
%if 0%{?rhel}
# Fedora doesn't have abi whitelists.
BuildRequires:	kernel-abi-whitelists
%endif
BuildRequires:  libuuid-devel
BuildRequires:  redhat-rpm-config
ExclusiveArch:	x86_64
ExcludeArch:    s390
ExcludeArch:    s390x
ExcludeArch:    ppc
ExcludeArch:    ppc64
ExcludeArch:    ppc64le
ExcludeArch:    aarch64
ExcludeArch:    i686

%description
Virtual Data Optimizer (VDO) is a device mapper target that delivers
block-level deduplication, compression, and thin provisioning.

This package provides the kernel modules for VDO.

%post
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %{kmod_name} -v %{version}
/usr/sbin/dkms --rpm_safe_upgrade build -m %{kmod_name} -v %{version}
/usr/sbin/dkms --rpm_safe_upgrade install -m %{kmod_name} -v %{version}

%preun
# Check whether kvdo or uds is loaded, and if so attempt to remove it.  A
# failure here means there is still something using the module, which should be
# cleared up before attempting to remove again.
for module in kvdo uds; do
  if grep -q "^${module}" /proc/modules; then
    modprobe -r ${module}
  fi
done
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{kmod_name} -v %{version} --all || :

%prep
%setup -n %{kmod_name}-%{commit}
%patch0001 -p1
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1
%patch0005 -p1
%patch0006 -p1
%patch0007 -p1
%patch0008 -p1
%patch0009 -p1
%patch0010 -p1
%patch0011 -p1
%patch0012 -p1
%patch0013 -p1
%patch0014 -p1
%patch0015 -p1
%patch0016 -p1
%patch0017 -p1
%patch0018 -p1
%patch0019 -p1
%patch0020 -p1

%build
# Nothing doing here, as we're going to build on whatever kernel we end up
# running inside.

%install
mkdir -p $RPM_BUILD_ROOT/%{_usr}/src/%{kmod_name}-%{version}
cp -r * $RPM_BUILD_ROOT/%{_usr}/src/%{kmod_name}-%{version}/
cat > $RPM_BUILD_ROOT/%{_usr}/src/%{kmod_name}-%{version}/dkms.conf <<EOF
PACKAGE_NAME="kvdo"
PACKAGE_VERSION="%{version}"
AUTOINSTALL="yes"

BUILT_MODULE_NAME[0]="uds"
BUILT_MODULE_LOCATION[0]="uds"
DEST_MODULE_LOCATION[0]="/kernel/drivers/block/"
STRIP[0]="no"

BUILT_MODULE_NAME[1]="kvdo"
BUILT_MODULE_LOCATION[1]="vdo"
DEST_MODULE_LOCATION[1]="/kernel/drivers/block/"
STRIP[1]="no"
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_usr}/src/%{kmod_name}-%{version}

%changelog
* Tue Nov 01 2022 - Andy Walsh <awalsh@redhat.com> - 6.2.7.17-3
- Applied patches to enable builds up to 6.1 kernel.

* Tue Jun 21 2022 - Andy Walsh <awalsh@redhat.com> - 6.2.7.9-3
- Re-pointed source to upstream repo
- Applied patches to enable builds up to 5.17 kernel

* Wed Jun 15 2022 - Andy Walsh <awalsh@redhat.com> - 6.2.7.9-2
- Adjusted sources to point at the fork

* Wed May 04 2022 - Red Hat VDO Team <vdo-devel@redhat.com> - 6.2.7.9-1
- Fixed bug which could result in empty flushes being issued to the storage
  below vdo while suspended.
- Fixed syntax mismatch which prevented lvm from being able to configure a
  512MB UDS index.
