#!/bin/bash

set -e

SPEC=${SPEC:-../divine.spec}

rm -rf srpm
mkdir srpm
cd srpm

# clone git repo
git clone --depth 1 https://gitlab.fi.muni.cz/paradise/mirror/divine.git

# make package
pushd divine > /dev/null
TAG=$(git describe | sed -e "s/-/_/g")
PREFIX="divine-$TAG/"

echo "Making divine-$TAG.tar.gz..."
git archive --prefix="$PREFIX" -o "../divine-$TAG.tar.gz" HEAD
popd > /dev/null

# update version
echo "Updating $SPEC..."
VERSION="Version:        $TAG"

if ! grep -q "$VERSION" "$SPEC"; then
  echo "New release found: $TAG"
  sed -i "s/^Version:.*/$VERSION/" "$SPEC"
  sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC"
fi

# copy patches
cp ../*.patch .

# copy tools
cp ../divine2csgrep.py ../csexec-divine.sh .

# build SRPM
echo Building SRPMs...
rpmbuild -bs "$SPEC" --define "_sourcedir $PWD" --define "_srcrpmdir $PWD"
