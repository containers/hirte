#!/bin/bash -xe
# SPDX-License-Identifier: GPL-2.0-or-later

source $(dirname "$(readlink -f "$0")")/build-srpm.sh

# Install build dependencies
if [ "${SKIP_BUILDDEP}" != "yes" ]; then
    dnf builddep -y rpmbuild/SRPMS/*src.rpm
fi

# Build binary package
rpmbuild \
    --define "_topmdir rpmbuild" \
    --define "_rpmdir rpmbuild" \
    --rebuild rpmbuild/SRPMS/*src.rpm

# Move RPMs to exported artifacts
ARTIFACTS_DIR="${ARTIFACTS_DIR:=$(pwd)/artifacts/rpms/$(date +'%m-%d-%Y')}"
[[ -d $ARTIFACTS_DIR ]] || mkdir -p $ARTIFACTS_DIR
find rpmbuild -iname \*rpm | xargs mv -t $ARTIFACTS_DIR
