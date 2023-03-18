package main

import (
	"github.com/leoluk/plcmon/src/cmd/plcmon/s7"
	"k8s.io/klog"
)

func init() {
	klog.InitFlags(nil)
}

func main() {
	sps := s7.NewA05PLC()
	if err := sps.Connect(); err != nil {
		klog.Exitf("failed to connect to SPS: %v", err)
	}
	defer sps.Disconnect()

	klog.Info("connected to SPS")

	bit := s7.BitAussenlichtKopplung

	st, err := sps.ReadDBBit(bit)
	if err != nil {
		klog.Exitf("failed to read DB bit: %v", err)
	}
	klog.Infof("%d is %v", bit, st)

	if err := sps.WriteDBBit(bit, false); err != nil {
		klog.Exitf("failed to write DB bit: %v", err)
	}
	klog.Info("wrote DB bit")

	st, err = sps.ReadDBBit(bit)
	if err != nil {
		klog.Exitf("failed to read DB bit: %v", err)
	}
	klog.Infof("%d is %v", bit, st)

}
