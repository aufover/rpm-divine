#!/bin/bash

SPEC=${SPEC:-../divine.spec}

rm -rf srpm
mkdir srpm
cd srpm || exit $?

# clone git repo
git clone https://gitlab.fi.muni.cz/paradise/mirror/divine.git

# make package
pushd divine
VER=`sed "s/-/_/g" <(git describe)`
PREFIX="divine-$VER/"

echo Making divine-$VER.tar.gz ...
git archive --prefix=$PREFIX -o ../divine-$VER.tar.gz HEAD
popd

# update version
echo Updating $SPEC ...
sed -i "s/^Version:.*/Version:        $VER/" $SPEC

if [ -v CHECK ]; then
  sed '/make unit/a make functional' $SPEC > divine_check.spec
  SPEC=divine_check.spec
fi

# copy patches
cp ../*.patch .

# build SRPM
echo Building SRPM ...
rpmbuild -bs $SPEC --define "_sourcedir $PWD" --define "_srcrpmdir $PWD"
