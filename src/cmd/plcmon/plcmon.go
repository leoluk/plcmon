package main

import (
	"flag"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"k8s.io/klog"
	"net/http"
	_ "net/http/pprof"
	"sync"
)

var (
	statusAddr = flag.String("statusAddr", "0.0.0.0:7001", "Listen address for PLCMON status")
	notifyAddr = flag.String("notifyAddr", "0.0.0.0:7002", "Listen address for PLCMON notify")
	debugAddr  = flag.String("debugAddr", "0.0.0.0:6060", "Listen address for debug server")
)

func main() {
	klog.InitFlags(nil)
	flag.Parse()
	validatePushFlags()
	validateTelegramArgs()

	klog.CopyStandardLogTo("INFO")

	http.Handle("/metrics", promhttp.Handler())

	go func() {
		klog.Info("debug server listening on ", *debugAddr)
		klog.Error(http.ListenAndServe(*debugAddr, nil))
	}()

	wg := sync.WaitGroup{}
	wg.Add(2)

	go func() {
		statusServer(*statusAddr)
		wg.Done()
	}()
	go func() {
		notifyServer(*notifyAddr)
		wg.Done()
	}()

	wg.Wait()

	klog.Info("exiting")
	klog.Flush()
}
