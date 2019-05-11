#!/usr/bin/env bash
set -eo pipefail
# Ghetto pfSense redeployment.

. ./env.sh

HOST=dk0fr-pf

ARGS="$PLCMON_ARGS $@ -vmodule notify=2 -alsologtostderr"

GOOS=freebsd GO386=387 GOARCH=386 go build -ldflags="-s -w" github.com/leoluk/plcmon/src/cmd/plcmon
! ssh ${HOST} kill '`cat ~/plcmon.pid`'
scp plcmon ${HOST}:
scp src/daemon.sh ${HOST}:
(echo '~/daemon.sh' $ARGS; cat)| ssh -t ${HOST}
