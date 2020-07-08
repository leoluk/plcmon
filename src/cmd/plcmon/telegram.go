package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"k8s.io/klog"
	"net/http"
	"time"
)

var (
	telegramKey   = flag.String("telegramKey", "", "Telegram bot key")
	telegramGroup = flag.String("telegramGroup", "", "Telegram destination group ID")

	httpClient = http.Client{
		Timeout: 10 * time.Second,
	}
)

func validateTelegramArgs() {
	if *telegramKey != "" && *telegramGroup == "" {
		klog.Fatal("Please specify -telegramGroup with -telegramKey")
	}
}

func sendTelegramMessage(body string) {
	go func() {
		message := map[string]string{
			"text":    body,
			"chat_id": *telegramGroup,
		}
		payload, err := json.Marshal(message)
		if err != nil {
			panic(err)
		}

		url := fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", *telegramKey)

		req, err := http.NewRequest("POST", url, bytes.NewBuffer(payload))
		if err != nil {
			panic(err)
		}

		req.Header.Set("Content-Type", "application/json")

		resp, err := httpClient.Do(req)
		if err != nil {
			klog.Errorf("error sending Telegram message: %v", resp)
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode != 200 {
			klog.Errorf("sendMessage returned status code %d", resp.StatusCode)
		}
	}()
}
