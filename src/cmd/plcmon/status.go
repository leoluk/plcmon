package main

import (
	"encoding/binary"
	"github.com/golang/glog"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"net"
	"reflect"
)

var (
	statusMessagesProcessed = promauto.NewCounter(prometheus.CounterOpts{
		Name: "plcmon_status_messages_total",
		Help: "The total number of processed status messages",
	})
	sensorStatus = promauto.NewGaugeVec(prometheus.GaugeOpts{
		Name: "plcmon_status_value",
		Help: "Current state of PLCMON status bits",
	}, []string{"name"})
)

// See messages.org. Using the German descriptions appeared to the most
// sensible course of action, given all of the existing German docs.
type StatusMessage struct {
	RelaisWerkstatt    bool
	RelaisUKW          bool
	RelaisKW           bool
	RelaisZentralstrom bool
	RelaisFlurlicht    bool
	StatusDauerlicht   bool
	KopplungAktiv      bool
	Kopplung           bool
	FlurlichtManuell   bool
	RelaisAussenlicht  bool
	AlarmUnscharf      bool
	AlarmAusgeloest    bool
}

func processStatusPacket(buffer []byte) StatusMessage {
	message := binary.BigEndian.Uint16(buffer)

	return StatusMessage{
		RelaisWerkstatt:    message&(1<<0) > 0,
		RelaisUKW:          message&(1<<1) > 0,
		RelaisKW:           message&(1<<2) > 0,
		RelaisZentralstrom: message&(1<<3) > 0,
		RelaisFlurlicht:    message&(1<<4) > 0,
		StatusDauerlicht:   message&(1<<5) > 0,
		KopplungAktiv:      message&(1<<6) > 0,
		Kopplung:           message&(1<<7) > 0,
		FlurlichtManuell:   message&(1<<8) > 0,
		RelaisAussenlicht:  message&(1<<9) > 0,
		AlarmUnscharf:      message&(1<<10) > 0,
		AlarmAusgeloest:    message&(1<<11) > 0,
	}
}

func boolToFloat(b bool) float64 {
	if b {
		return 1
	}

	return 0
}

func statusServer(addr string) {
	s, err := net.ListenPacket("udp", addr)
	if err != nil {
		glog.Fatal(err)
	}

	glog.Infof("status server listening on %s", addr)

	defer s.Close()

	buffer := make([]byte, 2)

	for {
		n, addr, err := s.ReadFrom(buffer)
		if err != nil {
			glog.Errorf("failed to receive packet: %v", err)
		}

		glog.V(2).Infof("recv: bytes=%d from=%s, buf=%x\n",
			n, addr.String(), string(buffer[:n]))

		if n != 2 {
			glog.Warning("ignoring invalid packet")
			continue
		}

		data := processStatusPacket(buffer[:n])

		glog.V(2).Infof("data: %+v", data)

		// Set metrics
		statusMessagesProcessed.Inc()

		{
			v := reflect.ValueOf(data)
			for i := 0; i < v.NumField(); i++ {
				 sensorStatus.WithLabelValues(
				 	v.Type().Field(i).Name).Set(boolToFloat(v.Field(i).Bool()))
			}
		}

		glog.Flush()
	}
}
