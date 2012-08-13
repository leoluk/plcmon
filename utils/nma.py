#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#
#   This copyright notice MUST APPEAR in all copies of the script!
#   In case of abuse or illegal redistribution please contact me:
#   mail@leoschabel.de
#

import logging
import requests

# http://notifymyandroid.com/api.jsp

URL_NOTIFY = 'http://www.notifymyandroid.com/publicapi/notify'
URL_VERIFY = 'http://www.notifymyandroid.com/publicapi/verify'

class NMAError(RuntimeError): pass
class UsageExceededError(NMAError): pass
class ServerError(NMAError): pass
class APIKeyError(NMAError): pass


class NMAProvider(object):
    def __init__(self, keys):
        self.keys = keys
        self.logger = logging.getLogger("nma")
        self.session = requests.session()

        valid_keys = []

        for key in keys:
            try:
                if not self._verify_key(key):
                    self.logger.error("Invalid API key: %s" % key)
                else:
                    valid_keys.append(key)
            except NMAError:
                self.logger.exception("NMA API error")

        if not len(valid_keys):
            raise APIKeyError("None of the keys provided are valid")

    def _verify_key(self, key):
        req = self.session.post(URL_VERIFY, data=dict(apikey=key))

        if req.status_code == 200:
            return True
        elif req.status_code == 500:
            raise ServerError("Internal server error")
        elif req.status_code == 402:
            raise UsageExceededError("API calls per hour exceeded")
        else:
            return False

    def notify(self, event, description, application="DK0FR", priority=0,
               html=False, url=None):

        params = {
            'apikey': ','.join(self.keys),
            'description': description,
            'event': event,
            'application': application,
            'priority': priority,
        }

        if html:
            params['content-type'] = 'text/html'

        if url:
            params['url'] = url

        req = self.session.post(URL_NOTIFY, data=params)

        if req.status_code == 200:
            return True
        elif req.status_code == 400:
            raise ValueError("The supplied data has an invalid format")
        elif req.status_code == 401:
            # should not happen, keys are checked beforehand!
            raise APIKeyError("None of the keys provided are valid")
        elif req.status_code == 500:
            raise ServerError("Internal server error")
        elif req.status_code == 402:
            raise UsageExceededError("API calls per hour exceeded")


def main():
    nma = NMAProvider(['13cd83b984c06e6a9bf43c2f3810ecf51b75cdb6655d3056'])
    nma.notify("PLCMON", "Test")


if __name__ == '__main__':
    main()