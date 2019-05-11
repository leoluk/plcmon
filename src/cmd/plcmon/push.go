package main

import (
	"flag"
	"github.com/golang/glog"
	"github.com/gregdel/pushover"
)

var (
	pushoverKey  = flag.String("pushoverKey", "", "Pushover application key")
	pushoverAddr = flag.String("pushoverAddr", "", "Pushover recipient address")
)

func validatePushFlags() {
	if *pushoverKey == "" {
		glog.Fatal("no Pushover key specified")
	} else if *pushoverAddr == "" {
		glog.Fatal("Pushover key specified, but no address")
	}
}

func sendPushMessage(body string, urgent bool) {
	pApp := pushover.New(*pushoverKey)
	pRecipient := pushover.NewRecipient(*pushoverAddr)

	// Pushover
	go func(){
		m := pushover.NewMessage(body)

		if urgent {
			m.Priority = 1
			m.Sound = "alien"
		}

		r, err := pApp.SendMessage(m, pRecipient)
		if err != nil {
			glog.Error("failed to send Pushover message:", err)
		}

		glog.V(1).Infof("Pushover response %s", r)
	}()
}
