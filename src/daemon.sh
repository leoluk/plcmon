#!/bin/sh

kill -0 `cat ~/plcmon.pid` || daemon -P ~/plcmon.pid -r ~/plcmon $@
echo "@reboot ~/daemon.sh $@" | crontab -
