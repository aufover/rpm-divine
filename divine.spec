Name:           divine
Version:        4.4.0
Release:        11%{?dist}
Summary:        Explicit-state model checker

License:        TODO
URL:            https://%{name}.fi.muni.cz

Source0:        https://%{name}.fi.muni.cz/download/%{name}-%{version}.tar.gz
Source1:        divine2csgrep.py

Patch0:         make_install.patch
Patch1:         rpmbuild.patch

# Patches to add missing headers and source files + change paths in divine
Patch2:         headers.patch
Patch3:         prefix_path.patch

# Patch to rise the testsuite timeout values for Copr builds
Patch4:         timeout.patch

# Downstream hotfixes or patches from the next branch
Patch5:         hotfix.patch

BuildRequires:  python3 perl make cmake ninja-build gcc-c++ libedit-devel
BuildRequires:  ncurses-devel zlib-devel gtest-devel

# optional dependencies
BuildRequires:  z3 z3-devel

# if some test fails, gdb is used to gather additional info
BuildRequires:  gdb

# 'static-dynamic.sh' test requires a static version of glibc
BuildRequires:  glibc-static

# required by 'divine2csgrep'
Requires: python3-pyyaml

# optional dependencies
Requires: python3-pygments z3

%description
TODO

%prep
%autosetup -p1

# use Python 3 explicitly
sed -in 's/python$/python3/' clang/tools/clang-format/clang-format-diff.py
sed -in 's/python$/python3/' clang/tools/clang-format/git-clang-format
sed -in 's/python$/python3/' clang/utils/hmaptool/hmaptool
sed -in 's/python$/python3/' clang/tools/scan-view/bin/scan-view

# use Python 3 instead of 2.7
sed -in 's/env python2.7$/python3/' llvm/tools/opt-viewer/opt-viewer.py
sed -in 's/env python2.7$/python3/' llvm/tools/opt-viewer/opt-stats.py
sed -in 's/env python2.7$/python3/' llvm/tools/opt-viewer/opt-diff.py
sed -in 's/env python2.7$/python3/' llvm/tools/opt-viewer/optrecord.py
sed -in 's/env python2.7$/python3/' llvm/utils/update_llc_test_checks.py
sed -in 's/env python2.7$/python3/' llvm/utils/lit/lit/Test.py
sed -in 's/env python2.7$/python3/' llvm/utils/update_analyze_test_checks.py
sed -in 's/env python2.7$/python3/' llvm/utils/update_test_checks.py
sed -in 's/env python2.7$/python3/' llvm/utils/update_mca_test_checks.py
sed -in 's/env python2.7$/python3/' clang/utils/check_cfc/test_check_cfc.py
sed -in 's/env python2.7$/python3/' clang/utils/check_cfc/check_cfc.py
sed -in 's/env python2.7$/python3/' clang/utils/check_cfc/obj_diff.py

%build
make

%install

# skip rpath check for now
export QA_RPATHS=$[ 0x0001 | 0x0010 | 0x0002 ]

%make_install

# create divc++ and diosc++ symlinks (if divcc is invoked as divc++, it should
# automatically link C++ run-time libraries)
ln -sf divcc  %{buildroot}/opt/divine/bin/divc++
ln -sf dioscc %{buildroot}/opt/divine/bin/diosc++

# make divine tools available in default $PATH
mkdir -p %{buildroot}%{_bindir}
ln -sf /opt/divine/bin/{diosc{c,++},divc{c,++},divine,lart} \
  %{buildroot}%{_bindir}

# install divine to csgrep convertor as an executable in path
install -p -D -m 755 %{SOURCE1} %{buildroot}%{_bindir}/divine2csgrep

%check
make unit
#make functional

%files
/opt/divine/
%{_bindir}/*
