#!/bin/sh

# some parts are extracted from the divine install.sh and install-prereq.sh scripts

set -e
version=${version:-4.3.3}
prefix=${prefix:-/opt/divine}
make_params="CMAKE_GENERATE_VC=OFF PREFIX=$prefix"

if [ -d $prefix ]; then
    echo "DIVINE appears to be already installed in $prefix"
    echo -n "your installed divine says "
    $prefix/bin/divine version 2> /dev/null | grep ^version:
    echo "the current version is:             $version"
    echo "if you wish to upgrade, please remove your current installation and try again"
    exit 1
fi

sudo dnf install -y wget tar patch

wget -N --continue https://divine.fi.muni.cz/download/divine-$version.tar.gz
tar xzf divine-$version.tar.gz
cd divine-$version

# apply downstream patch(es)
patch -p1 < ../disable-VC-checks.patch
patch -p1 < ../make_install.patch

# without python2
sudo dnf install -y perl make cmake ninja-build gcc-c++ libedit-devel ncurses-devel zlib-devel gtest-devel
# gtest-devel is needed for install

chmod +x dios/libcxx/utils/cat_files.py
ln -sf `pwd`/_build.toolchain/lld/lib/Driver/DarwinLdOptions.inc lld/include/DarwinLdOptions.inc

sed -in 's/python$/python3/' dios/libcxx/utils/cat_files.py

make $make_params
sudo make install $make_params

echo "DIVINE's binaries are installed in $prefix/bin"

if [ -d /etc/profile.d ]; then
    echo "PATH=$prefix/bin:"'$PATH' | sudo dd of=/etc/profile.d/divine-path.sh status=none
    echo "I have created /etc/profile.d/divine-path.sh to update system PATH"
    echo "After you log out and back in, it should be available as 'divine'"
fi

