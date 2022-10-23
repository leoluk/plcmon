package main

import (
	"flag"
	"fmt"
	mqtt "github.com/eclipse/paho.mqtt.golang"
	"k8s.io/klog"
	"log"
)

var (
	flagMqttAddr   = flag.String("mqttAddr", "", "MQTT server address")
	flagMqttUser   = flag.String("mqttUser", "", "MQTT username")
	flagMqttPass   = flag.String("mqttPass", "", "MQTT password")
	flagMqttRetain = flag.Bool("mqttRetain", false, "MQTT retain messages")
)

type mqttStatus struct {
	Armed     bool
	Triggered bool
}

func init() {
	if *flagMqttAddr != "" && (*flagMqttUser == "" || *flagMqttPass == "") {
		klog.Exit("mqttUser and mqttPass must both be set")
	}
}

func mqttService(evC chan mqttStatus) error {
	klog.CopyStandardLogTo("INFO")
	mqtt.ERROR = log.Default()

	opts := mqtt.NewClientOptions().AddBroker("tcp://" + *flagMqttAddr).SetClientID("plcmon")
	opts.SetUsername(*flagMqttUser)
	opts.SetPassword(*flagMqttPass)

	c := mqtt.NewClient(opts)
	if token := c.Connect(); token.Wait() && token.Error() != nil {
		return fmt.Errorf("mqtt connect: %w", token.Error())
	}

	klog.Infof("mqtt connected to %s", *flagMqttAddr)

	if token := c.Publish(
		"homeassistant/binary_sensor/plcmon/plcmon_armed/config", 0, *flagMqttRetain,
		`{
  "name": "Alarm Armed",
  "unique_id": "plcmon_armed",
  "device_class": "lock",
  "state_topic": "homeassistant/binary_sensor/plcmon/plcmon_armed/state",
  "payload_on": "false",
  "payload_off": "true",
  "device": {
    "identifiers": "PLCMON",
    "name": "PLCMON",
    "model": "PLCMON",
    "manufacturer": "PLCMON"
  }
}`); token.Wait() && token.Error() != nil {
		return fmt.Errorf("mqtt publish: %w", token.Error())
	}

	if token := c.Publish(
		"homeassistant/binary_sensor/plcmon/plcmon_triggered/config", 0, *flagMqttRetain,
		`{
  "name": "Alarm Triggered",
  "unique_id": "plcmon_triggered",
  "device_class": "safety",
  "state_topic": "homeassistant/binary_sensor/plcmon/plcmon_triggered/state",
  "payload_on": "true",
  "payload_off": "false",
  "device": {
    "identifiers": "PLCMON",
    "name": "PLCMON",
    "model": "PLCMON",
    "manufacturer": "PLCMON"
  }
}`); token.Wait() && token.Error() != nil {
		return fmt.Errorf("mqtt publish: %w", token.Error())
	}

	for {
		select {
		case e := <-evC:
			klog.V(1).Infof("mqtt event: %v", e)
			if token := c.Publish("homeassistant/binary_sensor/plcmon/plcmon_armed/state", 0, *flagMqttRetain, fmt.Sprintf("%v", e.Armed)); token.Wait() && token.Error() != nil {
				return fmt.Errorf("mqtt publish: %w", token.Error())
			}
			if token := c.Publish("homeassistant/binary_sensor/plcmon/plcmon_triggered/state", 0, *flagMqttRetain, fmt.Sprintf("%v", e.Triggered)); token.Wait() && token.Error() != nil {
				return fmt.Errorf("mqtt publish: %w", token.Error())
			}
		}
	}
}
