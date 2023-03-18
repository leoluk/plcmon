module github.com/leoluk/plcmon

go 1.19

require (
	github.com/eclipse/paho.mqtt.golang v1.4.1
	github.com/gregdel/pushover v0.0.0-20190217183207-15d3fef40636
	github.com/prometheus/client_golang v0.9.2
	github.com/robinson/gos7 v0.0.0-20230126084723-c85e13033f3e
	k8s.io/klog v0.3.2
)

require (
	github.com/beorn7/perks v0.0.0-20180321164747-3a771d992973 // indirect
	github.com/golang/protobuf v1.2.0 // indirect
	github.com/gorilla/websocket v1.4.2 // indirect
	github.com/matttproud/golang_protobuf_extensions v1.0.1 // indirect
	github.com/prometheus/client_model v0.0.0-20180712105110-5c3871d89910 // indirect
	github.com/prometheus/common v0.0.0-20181126121408-4724e9255275 // indirect
	github.com/prometheus/procfs v0.0.0-20181204211112-1dc9a6cbc91a // indirect
	github.com/tarm/serial v0.0.0-20180830185346-98f6abe2eb07 // indirect
	golang.org/x/net v0.0.0-20200425230154-ff2c4b7c35a0 // indirect
	golang.org/x/sync v0.0.0-20210220032951-036812b2e83c // indirect
	golang.org/x/sys v0.1.0 // indirect
)

replace github.com/robinson/gos7 => github.com/leoluk/gos7 v0.0.0-20230318194414-5a5c7c1b5435
