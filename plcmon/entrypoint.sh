#!/usr/bin/with-contenv bashio

CONFIG_PATH=/data/options.json

/plcmon \
  -pushoverKey "$(bashio::config 'pushoverKey')" \
  -pushoverAddr "$(bashio::config 'pushoverAddr')" \
  -telegramKey "$(bashio::config 'telegramKey')" \
  -telegramGroup "$(bashio::config 'telegramGroup')" \
  -mqttAddr "$(bashio::config 'mqttAddr')" \
  -mqttUser "$(bashio::config 'mqttUser')" \
  -mqttPass "$(bashio::config 'mqttPass')"
