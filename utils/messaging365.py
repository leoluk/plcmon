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

# This is a very basic wrapper which only supports a limited subset of
# possible parameters and errors.

URL_SEND = "http://messaging365.com:8080/MsgReceiver/sendmsg"

class M365Error(RuntimeError): pass
class AuthError(M365Error): pass
class ServerError(M365Error): pass
class BalanceError(M365Error): pass

ERRORS = {
    401: AuthError("Username or Password not correct"),
    402: BalanceError("Insufficient account balance"),
    400: ServerError("Invalid request"),
    500: ServerError("Internal server error"),
}


class M365Provider(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.logger = logging.getLogger("m365")
        self.session = requests.session()

    def send_message(self, msisdn, sender, message, msg_type="flash"):
        req = self.session.post(URL_SEND, data=dict(
            user=self.username,
            password=self.password,
            msgType=msg_type,
            destNumber=msisdn,
            origNumber=sender,
            msgText=message
        ), stream=False)

        if req.status_code == 200:
            return True
        else:
            raise ERRORS.get(req.status_code,
                              M365Error("Unknown error: %s" % req.content))


def main():
    import getpass
    number = raw_input("Phone number: ")
    username = raw_input("Messaging365 username: ")
    password = getpass.getpass("Password: ")

    prov = M365Provider(username, password)
    prov.send_message(number, "PLCMON", "Hallo")


if __name__ == '__main__':
    main()
