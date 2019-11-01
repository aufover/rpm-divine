#!/bin/bash

SPEC=${SPEC:-../divine.spec}

rm -rf srpm
mkdir srpm
cd srpm || exit $?

# clone git repo
git clone https://gitlab.fi.muni.cz/paradise/mirror/divine.git

# make package
pushd divine
TAG=`sed "s/-/_/g" <(git describe)`
PREFIX="divine-$TAG/"

echo Making divine-$TAG.tar.gz ...
git archive --prefix=$PREFIX -o ../divine-$TAG.tar.gz HEAD
popd

# update version
echo Updating $SPEC ...
VERSION="Version:        $TAG"

if ! grep -q "$VERSION" $SPEC; then
  echo New release found: $TAG 
  sed -i "s/^Version:.*/$VERSION/" $SPEC
  sed -i "s/^Release:.*/Release:        1%{?dist}/" $SPEC
fi

if [ -v CHECK ]; then
  sed '/make unit/a make functional' $SPEC > divine_check.spec
  SPEC=divine_check.spec
fi

# copy patches
cp ../*.patch .

# build SRPM
echo Building SRPM ...
rpmbuild -bs $SPEC --define "_sourcedir $PWD" --define "_srcrpmdir $PWD"
