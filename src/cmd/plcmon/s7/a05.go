package s7

import (
	"github.com/robinson/gos7"
	"k8s.io/klog"
	"log"
	"time"
)

const (
	// A05 S7-1200
	spsAddr = "192.168.1.10"
	spsRack = 0
	spsSlot = 0
	dbNum   = 8
	dbByte  = 0
)

/*
	Merker in DB8.DBX0.0

	0.0	Status Dauerlicht
	0.1	Flurlicht-Timer zurücksetzen	  (push button)
	0.2	Flurlicht-Taster simulieren       (push button)
	0.3	Flurlicht-Haltemerker umschalten  (push button)
	0.4	Außenlichtkopplung aktiv
	0.5	UDP-Datentelegrammversand aktiv
*/

type Merker uint8

const (
	BitDauerlicht Merker = iota
	BitFlurlichtTimerReset
	BitFlurlichtTaster
	BitFlurlichtHold
	BitAussenlichtKopplung
	BitUDPEnabled
)

type A05PLC struct {
	handler *gos7.TCPClientHandler
}

func NewA05PLC() *A05PLC {
	return &A05PLC{
		handler: gos7.NewTCPClientHandler(spsAddr, spsRack, spsSlot),
	}
}

func (a *A05PLC) Connect() error {
	a.handler.Timeout = 5 * time.Second
	a.handler.IdleTimeout = 30 * time.Second
	a.handler.Logger = log.Default()
	return a.handler.Connect()
}

func (a *A05PLC) Disconnect() error {
	return a.handler.Close()
}

func (a *A05PLC) ReadDBBit(bitNum Merker) (bool, error) {
	client := gos7.NewClient(a.handler)
	var data [1]byte
	if err := client.AGReadDB(dbNum, dbByte, 1, data[:]); err != nil {
		return false, err
	}
	klog.Infof("ReadDBBit: %v", data)
	return data[0]&(1<<bitNum) != 0, nil
}

func (a *A05PLC) WriteDBBit(bitNum Merker, state bool) error {
	client := gos7.NewClient(a.handler)
	return client.AGWriteDBBit(dbNum, dbByte+int(bitNum), 1, boolToByte(state))
}

func boolToByte(b bool) []byte {
	if b {
		return []byte{0x01}
	}
	return []byte{0x00}
}
