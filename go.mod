module github.com/leoluk/plcmon

go 1.19

require (
	github.com/eclipse/paho.mqtt.golang v1.4.3
	github.com/gregdel/pushover v1.3.1
	github.com/prometheus/client_golang v1.19.1
	github.com/robinson/gos7 v0.0.0-20240315073918-1f14519e4846
	k8s.io/klog/v2 v2.130.1
)

require (
	github.com/beorn7/perks v1.0.1 // indirect
	github.com/cespare/xxhash/v2 v2.3.0 // indirect
	github.com/go-logr/logr v1.4.1 // indirect
	github.com/gorilla/websocket v1.5.3 // indirect
	github.com/munnerz/goautoneg v0.0.0-20191010083416-a7dc8b61c822 // indirect
	github.com/prometheus/client_model v0.6.1 // indirect
	github.com/prometheus/common v0.55.0 // indirect
	github.com/prometheus/procfs v0.15.1 // indirect
	github.com/tarm/serial v0.0.0-20180830185346-98f6abe2eb07 // indirect
	golang.org/x/net v0.27.0 // indirect
	golang.org/x/sync v0.7.0 // indirect
	golang.org/x/sys v0.22.0 // indirect
	google.golang.org/protobuf v1.34.2 // indirect
)

replace github.com/robinson/gos7 => github.com/leoluk/gos7 v0.0.0-20230318194414-5a5c7c1b5435
