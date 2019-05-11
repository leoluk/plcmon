package main

import (
	"fmt"
	"github.com/golang/glog"
	"net"
)


const (
	messageArmed     = "Alarmanlage scharf"
	messageDisarmed  = "Alarmanlage unscharf"
	messageTriggered = "Alarm ausgelöst"
	messageReset     = "Alarm zurückgesetzt und unscharf"
	messageInvalid   = "Ungültiger Zustand der State Machine: %x"
)

func formatPushMessage(message uint8) (pushMessage string, urgent bool) {
	switch {
	case message == 0x01: // armed
		glog.Info("notify: alarm armed")
		pushMessage = messageArmed
	case message == 0x0f: // disarmed
		glog.Info("notify: alarm disarmed")
		pushMessage = messageDisarmed
	case message == 0xf1: // alarm || armed
		glog.Info("notify: alarm triggered")
		pushMessage = messageTriggered
		urgent = true
	case message == 0xef: // reset || disarmed
		glog.Info("notify: alarm reset")
		pushMessage = messageReset
	default:
		glog.Errorf("notify: invalid state machine: %x", message)
		pushMessage = fmt.Sprintf(messageInvalid, message)
	}

	return
}

func processNotify(buffer []byte) {
	b := uint8(buffer[0])

	sendPushMessage(formatPushMessage(b))
}

func notifyServer(addr string) {
	s, err := net.ListenPacket("udp", addr)
	if err != nil {
		glog.Fatal(err)
	}

	glog.Infof("notify server listening on %s", addr)

	defer s.Close()

	buffer := make([]byte, 1)

	for {
		n, addr, err := s.ReadFrom(buffer)
		if err != nil {
			glog.Errorf("failed to receive packet: %v", err)
		}

		glog.V(2).Infof("recv: bytes=%d from=%s, buf=%x\n",
			n, addr.String(), string(buffer[:n]))

		if n != 1 {
			glog.Warning("ignoring invalid packet")
			continue
		}

		processNotify(buffer[:n])

		glog.Flush()
	}
}
