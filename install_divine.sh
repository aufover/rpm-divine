#! /bin/sh

# some parts are extracted from the divine install.sh and install-prereq.sh scripts

set -e
version=4.3.3
prefix=/opt/divine

if test -d $prefix; then
    echo "DIVINE appears to be already installed in $prefix"
    echo -n "your installed divine says "
    $prefix/bin/divine version 2> /dev/null | grep ^version:
    echo "the current version is:             $version"
    echo "if you wish to upgrade, please remove your current installation and try again"
    exit 1
fi

dnf install -y wget tar

wget -N --continue https://divine.fi.muni.cz/download/divine-$version.tar.gz
tar xzf divine-$version.tar.gz
cd divine-$version

# without python2
dnf install -y perl make cmake ninja-build gcc-c++ libedit-devel ncurses-devel zlib-devel gtest-devel
# gtest-devel is needed for install

chmod +x dios/libcxx/utils/cat_files.py
ln -sf ${PWD}/_build.toolchain/lld/lib/Driver/DarwinLdOptions.inc lld/include/DarwinLdOptions.inc

sed -in 's/python$/python3/g' dios/libcxx/utils/cat_files.py
sed -in 's/\${PROJECT_SOURCE_DIR}\/include/\${PROJECT_SOURCE_DIR}\/stp\/include/g' stp/lib/Interface/CMakeLists.txt
sed -in 's/^install( TARGETS divine-ui divine-vm divine-cc divine-ltl DESTINATION lib )/install( TARGETS divine-ui divine-vm divine-cc divine-ltl divine-sim divine-mc divine-dbg divine-smt DESTINATION lib )/g' divine/CMakeLists.txt 
/bin/cp ../new-install-rpath.cmake releng/install-rpath.cmake

make
make install

echo "DIVINE's binaries are installed in $prefix/bin"

if test -d /etc/profile.d; then
    echo "PATH=$prefix/bin:"'$PATH' > /etc/profile.d/divine-path.sh
    echo "I have created /etc/profile.d/divine-path.sh to update system PATH"
    echo "After you log out and back in, it should be available as 'divine'"
fi

