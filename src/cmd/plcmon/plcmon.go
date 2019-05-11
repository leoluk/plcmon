package main

import (
	"flag"
	"github.com/golang/glog"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"net/http"
	"sync"
	_ "net/http/pprof"
)

var (
	statusAddr = flag.String("statusAddr", "0.0.0.0:7001", "Listen address for PLCMON status")
	notifyAddr = flag.String("notifyAddr", "0.0.0.0:7002", "Listen address for PLCMON notify")
	debugAddr = flag.String("debugAddr", "0.0.0.0:6060", "Listen address for debug server")
)

func main() {
	flag.Parse()
	validatePushFlags()
	glog.CopyStandardLogTo("INFO")

	http.Handle("/metrics", promhttp.Handler())

	go func() {
		glog.Info("debug server listening on ", *debugAddr)
		glog.Error(http.ListenAndServe(*debugAddr, nil))
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

	glog.Info("exiting")
	glog.Flush()
}
