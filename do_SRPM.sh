#!/bin/bash

set -e

SPEC=${SPEC:-../divine.spec}
SPEC_TESTED=${SPEC/%.spec/-tested.spec}

rm -rf srpm
mkdir srpm
cd srpm

# clone git repo
echo "Cloning Divine..."
git clone --quiet https://gitlab.fi.muni.cz/paradise/mirror/divine.git

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

cp "$SPEC" "$SPEC_TESTED"
sed -i "s/\(Name:.*\)divine/\1divine-tested/" "$SPEC_TESTED"
sed -i "s/#make/make/" "$SPEC_TESTED"

# copy patches
cp ../*.patch .
cp ../divine2csgrep.py .

# build SRPM
echo Building SRPMs...
rpmbuild -bs {"$SPEC","$SPEC_TESTED"} --define "_sourcedir $PWD" \
    --define "_srcrpmdir $PWD"
