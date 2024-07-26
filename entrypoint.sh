#!/usr/bin/with-contenv bashio

/usr/local/bin/plcmon \
  -pushoverKey "$(bashio::config 'pushoverKey')" \
  -pushoverAddr "$(bashio::config 'pushoverAddr')" \
  -telegramKey "$(bashio::config 'telegramKey')" \
  -telegramGroup "$(bashio::config 'telegramGroup')"
