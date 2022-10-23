#!/usr/bin/env bash
set -eo pipefail

go build -o plcmon github.com/leoluk/plcmon/src/cmd/plcmon
rsync plcmon dk0fr@192.168.1.125:/opt/plcmon/plcmon
ssh dk0fr@192.168.1.125 sudo systemctl restart plcmon
ssh dk0fr@192.168.1.125 sudo systemctl status plcmon
