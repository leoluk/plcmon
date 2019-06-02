#!/usr/bin/env bash
set -eo pipefail
# Ghetto pfSense redeployment.

. ./env.sh

HOST=dk0fr-pf

ARGS="$PLCMON_ARGS $@ -vmodule notify=2 -vmodule push=1 -log_file /tmp/plcmon.log -logtostderr false"

# Cross-compile binary
GOOS=freebsd GO386=387 GOARCH=386 go build -ldflags="-s -w" github.com/leoluk/plcmon/src/cmd/plcmon

# Kill old instances of the daemon
! ssh ${HOST} kill '`cat ~/plcmon.pid`'

# Poor man's rsync (since we do not have rsync on the box)
if [[ "$(ssh ${HOST} cksum plcmon)" != "$(cksum plcmon)" ]]; then
    echo "Copying binary...."
    scp plcmon ${HOST}:
fi

# Run the daemon
scp src/daemon.sh ${HOST}:
ssh ${HOST} '~/daemon.sh' $ARGS
