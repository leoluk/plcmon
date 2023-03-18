module github.com/leoluk/plcmon

go 1.19

require (
	github.com/eclipse/paho.mqtt.golang v1.4.1
	github.com/gregdel/pushover v0.0.0-20190217183207-15d3fef40636
	github.com/prometheus/client_golang v1.11.1
	github.com/robinson/gos7 v0.0.0-20230126084723-c85e13033f3e
	k8s.io/klog v0.3.2
)

require (
	github.com/beorn7/perks v1.0.1 // indirect
	github.com/cespare/xxhash/v2 v2.1.1 // indirect
	github.com/golang/protobuf v1.4.3 // indirect
	github.com/gorilla/websocket v1.4.2 // indirect
	github.com/matttproud/golang_protobuf_extensions v1.0.1 // indirect
	github.com/prometheus/client_model v0.2.0 // indirect
	github.com/prometheus/common v0.26.0 // indirect
	github.com/prometheus/procfs v0.6.0 // indirect
	github.com/tarm/serial v0.0.0-20180830185346-98f6abe2eb07 // indirect
	golang.org/x/net v0.0.0-20200625001655-4c5254603344 // indirect
	golang.org/x/sync v0.0.0-20210220032951-036812b2e83c // indirect
	golang.org/x/sys v0.0.0-20210603081109-ebe580a85c40 // indirect
	google.golang.org/protobuf v1.26.0-rc.1 // indirect
)

replace github.com/robinson/gos7 => github.com/leoluk/gos7 v0.0.0-20230318194414-5a5c7c1b5435
