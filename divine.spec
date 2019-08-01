Name:           divine
Version:        4.3.3 
Release:        1%{?dist}
Summary:        Explicit-state model checker

License:        TODO
URL:            https://%{name}.fi.muni.cz
Source0:        https://%{name}.fi.muni.cz/download/%{name}-%{version}.tar.gz

Patch0:         make_install.patch
Patch1:         disable-VC-checks.patch

BuildRequires:  wget tar patch perl make cmake ninja-build gcc-c++ libedit-devel ncurses-devel zlib-devel gtest-devel

%description
TODO

%prep
%autosetup -p1

chmod +x dios/libcxx/utils/cat_files.py
ln -sf `pwd`/_build.toolchain/lld/lib/Driver/DarwinLdOptions.inc lld/include/DarwinLdOptions.inc

# TODO: use build-id for divine build
# may fail, untested, add '-Wl,--build-id' to DEFINE_DEFINES otherwise
sed -in 's/ENABLE_LINKER_BUILD_ID OFF/ENABLE_LINKER_BUILD_ID ON/' clang/CMakeLists.txt

# use Python 3 explicitly
sed -in 's/python$/python3/' clang/tools/clang-format/clang-format-diff.py
sed -in 's/python$/python3/' clang/tools/clang-format/git-clang-format
sed -in 's/python$/python3/' dios/libcxx/utils/cat_files.py
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

# skip rpath check for now
export QA_RPATHS=$[ 0x0001 | 0x0010 | 0x0002 ]

%build
make CMAKE_GENERATE_VC=OFF

%install
rm -rf $RPM_BUILD_ROOT
%make_install

%files
#TODO
/opt/divine/
