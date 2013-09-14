#!/bin/bash

gen_alarm_live() {
	echo -ne "\x01" | nc -4u -w1 127.0.0.1 7002
}

gen_alarm_disabled() {
	echo -ne "\x0F" | nc -4u -w1 127.0.0.1 7002
}

gen_alarm_triggered() {
	echo -ne "\xF1" | nc -4u -w1 127.0.0.1 7002
}

gen_alarm_reset() {
	echo -ne "\xEF" | nc -4u -w1 127.0.0.1 7002
}
