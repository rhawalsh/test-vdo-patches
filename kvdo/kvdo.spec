%define unstable_date           20220527
%define spec_release            unstable.%{unstable_date}02
%define kmod_name		kvdo
%define kmod_driver_version	8.2.0.0
%define kmod_rpm_release	%{spec_release}
%define kmod_kernel_version	3.10.0-693.el7

# Disable the scanning for a debug package
%global debug_package %{nil}


Name:		kmod-kvdo
Version:	%{kmod_driver_version}
Release:	%{kmod_rpm_release}%{?dist}
Summary:	Kernel Modules for Virtual Data Optimizer
License:	GPLv2+
URL:		https://github.com/dm-vdo/kvdo

Source0:        %{url}/archive/refs/heads/unstable.tar.gz
Patch1:         0001-Use-correct-bi_bdev-to-do-cloning-with-in-5.18.patch

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
/usr/sbin/dkms --rpm_safe_upgrade add -m %{kmod_name} -v %{version}.%{unstable_date}
/usr/sbin/dkms --rpm_safe_upgrade build -m %{kmod_name} -v %{version}.%{unstable_date}
/usr/sbin/dkms --rpm_safe_upgrade install -m %{kmod_name} -v %{version}.%{unstable_date}

%preun
# Check whether kvdo is loaded, and if so attempt to remove it.  A
# failure here means there is still something using the module, which
# should be cleared up before attempting to remove again.
for module in kvdo uds; do
  if grep -q "^${module}" /proc/modules; then
    modprobe -r ${module}
  fi
done
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{kmod_name} -v %{version} --all || :

%prep
%setup -n kvdo-unstable
%patch1 -p1

%build
# Nothing doing here, as we're going to build on whatever kernel we end up
# running inside.

%install
mkdir -p $RPM_BUILD_ROOT/%{_usr}/src/%{kmod_name}-%{version}.%{unstable_date}
cp -r * $RPM_BUILD_ROOT/%{_usr}/src/%{kmod_name}-%{version}.%{unstable_date}/
cat > $RPM_BUILD_ROOT/%{_usr}/src/%{kmod_name}-%{version}.%{unstable_date}/dkms.conf <<EOF
PACKAGE_NAME="kvdo"
PACKAGE_VERSION="%{version}.%{unstable_date}"
AUTOINSTALL="yes"

BUILT_MODULE_NAME[0]="kvdo"
BUILT_MODULE_LOCATION[0]="vdo"
DEST_MODULE_LOCATION[0]="/kernel/drivers/block/"
BUILD_DEPENDS[0]=LZ4_COMPRESS
BUILD_DEPENDS[0]=LZ4_DECOMPRESS
STRIP[0]="no"
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_usr}/src/%{kmod_name}-%{version}.%{unstable_date}

%changelog
%define spec_release unstable.2022052702
* Thu Jun 23 2022 - Andy Walsh - awalsh@redhat.com - 8.2.0.0-unstable.2022052702
- Use correct bi_bdev to do cloning with in 5.18.

* Fri Jun 17 2022 - Andy Walsh - awalsh@redhat.com - 8.2.0.0-unstable.2022052701
- Added packaging information

* Fri May 27 2022 - Red Hat VDO Team <vdo-devel@redhat.com> - 8.2.0.0-1
- See https://github.com/dm-vdo/kvdo.git
