#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#
#   The author clearly points out that it is not possible to create absolutely
#   errorless or on all systems compatible software. Therefore you use or buy this
#   product "AS IS". This product was developed with the utmost care; however, a
#   described function MIGHT FAIL. The author takes NO RESPONSIBILITY for this.
#   The author takes no responsibility for correctness of the product,
#   especially not for the case that the product does not meet the requirements
#   and purposes of the user or does not work together with other programs. The
#   author takes absolutely no responsibility for DAMAGES of any kind resulting
#   from the use, misuse or other not mentioned damage possibilities.
#

"""This module provides a high-level interface for communication with a
Siemens S7-1200 CPU. Unless similar approaches (like wrapping libnodave),
this module fully supports symbolic names and database access. This is
accomplished by interfacing the S7 web server (which is obviously required
for using this module).

The following interfaces have been implemented (more to come):

  - switch SPS to RUN/STOP mode
  - read and write arbitrary symbolic and absolute variables
  - gather basic information about the CPU (model, resources, S/N)

Example usage:

>>> from s7com import S7WebComm
>>> plc = S7WebComm()
>>> plc.login("secret")
>>> plc.read_value('Q0.0', 'BOOL'):
True

Notes:

  - The S7 web server is insecure, just like the entire S7 communication is -
    you should NEVER EVER expose it on a public network; the password protects
    the SPS only from unauthorized writes (attackers can still crash it)

  - If you need real time communication, you might want to use a commercial
    library or libnodave - this module takes about 60 msecs for a request over
    plain HTTP and 1200 msecs for a request over HTTPS

  - Sometimes, the S7 rejects any login and the web interface can't be used
    as 'admin' users. When this error occurs, you have to power-cycle the CPU
    or do a factory reset if you have no physical access.

  - WARNING: NEVER use this library (or libnodave) in production, or at least
    not without EXTENSIVE testing: the S7 web server is VERY buggy and it's
    easy to crash the entire CPU - in the worst case, the S7 enters the DEFECT
    state and requires a physical reboot

"""

import sys, os
import re

import requests

try:
    import lxml.html
    LXML_AVAILABLE = True
except ImportError:
    import warnings
    LXML_AVAILABLE = False
    warnings.warn("lxml not available! using regular expressions")

# TODO: nicer regex workaround integration

LXML_AVAILABLE = False

from decorator import decorator
from unescape import unescape

def autopath(base, *args):
    return os.path.join(os.path.dirname(base), *args)

# Monkey-patching the monkey-patch: Requests respects the RFC, the S7-1200 doesn't,
# so the cookie values may not be wrapped in quotes and we have to stop
# Requests from adding them (forcing it to ignore the RFC just like Siemens does).

requests.packages.oreos.monkeys.SimpleCookie.value_encode = \
    requests.packages.oreos.monkeys.BaseCookie.value_encode

URL_LOGIN = "/FormLogin"
URL_BASE = "/Portal/Portal.mwsl"  # dangerous! no parms=crash CPU
URL_MAIN = "/Portal/Portal.mwsl?PriNav=Start"
URL_IDENT = "/Portal/Portal.mwsl?PriNav=Ident"
URL_VARSET = "/VarStateRedirect.mwsl"
URL_CMD = "/CPUCommands"

COOKIE_NAME = "siemens_ad_session"
COOKIE_FILE = autopath(__file__, 'session.dcx')

RE_VAR = re.compile(r'<div id="dynamic_contentt\d+" class="updatable">.+&nbsp;(.+)?</div>')
RE_FMT = re.compile('<option value="([A-Z_]+)" selected>')
RE_STATE = re.compile(r'<td class="output_field_long">.*?([A-Z]+?)\s*</td>', re.DOTALL)
RE_INFOS = re.compile(r'<td class="output_field_long">(.+?)</td>')
RE_NAME = re.compile(r'>SIMATIC&nbsp;1200-Station_1/(.+?)\b</td>')

class S7CommFailure(requests.ConnectionError): pass
class LoginFailure(S7CommFailure): pass
class LoginRequiredError(S7CommFailure): pass

DATA_MAPPING = {
    'BOOL': lambda x: bool([u'false', u'true'].index(x)),
    'DEC': int,
    'DEC_UNSIGNED': int,
    'BIN': str,
}  # TODO: complete list and conversion routines
   # TODO: use DefaultDict

DATA_MAPPING_REV = {
    'BOOL': lambda x: str(x).lower(),
    'DEC': str,
    'DEC_UNSIGNED': str,
    'BIN': str,
}

@decorator
def login_required(f, *args, **kwargs):
    """Decorator which raises a LoginRequiredError if the user has not logged
    in for the current WebComm session. (such as RUN/STOP/Write)"""

    # TODO: min timeout for re-check - session expires!

    if not args[0]._logged_in:
        raise LoginRequiredError("This method requires login")

    f(*args, **kwargs)


class S7WebComm(requests.Session):
    def __init__(self, sps_ip, secure=False):
        """
        Initializes an SPS communication session.

        `sps_ip`: IP or DNS name of the S7-1200
        `secure`: establish communication over HTTP (VERY slow!)

        """

        requests.Session.__init__(self, verify=False)
        self.ip = sps_ip
        self.secure = secure
        self._logged_in = False

        if self._load_cookie():
            self.ireq = self.get(self._build_url(URL_MAIN))
            self._logged_in = self._check_login(self.ireq)

    def _check_login(self, req):
        """Analyzes a Portal.mswl request for a successful login.
        Only necessary for checking if a given cookie is still valid."""

        return not ("Login_Button" in req.content)

    @property
    def logged_in(self):
        """Verifies whether the current session is still valid."""
        self._logged_in = self._check_login(self.get(self._build_url(URL_MAIN)))
        return self._logged_in

    def _build_url(self, location):
        return '%s://%s%s' % (['http', 'https'][self.secure], self.ip, location)

    def _load_cookie(self):
        try:
            self.cookies[COOKIE_NAME] = open(COOKIE_FILE).read()
            return True
        except IOError:
            pass

    def _save_cookie(self):
        try:
            open(COOKIE_FILE, 'w').write(self.cookies[COOKIE_NAME])
        except KeyError:
            pass

    def login(self, password, username='admin'):
        req = self.post(self._build_url(URL_LOGIN),
                 data={'Login': username, 'Password': password,}, prefetch=True)

        if COOKIE_NAME in req.cookies:
            self._logged_in = True
            self.ireq = self.get(self._build_url(URL_MAIN))
            self._save_cookie()
            return True
        else:
            raise LoginFailure("Invalid password")

    def logout(self, soft=False):
        if not soft:
            #self.post(self._build_url(URL_LOGIN+'?LOGOUT'),
            raise NotImplementedError

        self.cookies['siemens_ad_session'] = None

    def sps_information(self):
        req = self.get(self._build_url(URL_IDENT))
        if LXML_AVAILABLE:
            tree = lxml.html.parse(req.raw)
            listing = tree.xpath(r"//td[@class='output_field_long']/text()")
            name = tree.xpath(r"//td[@class='Header_Title_Description']/text()")\
                [0].split('/')[1]
        else:
            listing = RE_INFOS.findall(req.content)
            name = RE_NAME.findall(req.content)[0]

        properties = dict(zip(['serial', 'hwmodel', 'swmodel',
                  'hwversion', 'version'], listing))

        properties['name'] = unescape(name)

        return properties

    def sps_status(self):
        # TODO: use iReq as well
        req = self.get(self._build_url(URL_MAIN))

        if LXML_AVAILABLE:
            tree = lxml.html.parse(req.raw)
            infos = tree.xpath("//div[@id='dynamic_content_table2']//"
                               "td[@class='output_field_long']/text()")
            result = (infos[0], infos[2].strip())
        else:
            infos = RE_STATE.findall(req.content)
            result = infos

        return result

    @staticmethod
    def _check_fmt(fmt):
        if not fmt in DATA_MAPPING:
            raise ValueError("Format '%s' not supported" % fmt)

    @login_required
    def set_value(self, identifier, value, fmt="BOOL", check=False):
        return self.set_values([(identifier, value)], fmt, check=check)

    def read_value(self, identifier, fmt="BOOL"):
        # TODO: faster implementation
        return self.read_values([identifier], fmt=fmt)[identifier]

    @login_required
    def set_values(self, assignments, fmt="BOOL", check=False):
        """
        Writes one or more values to the PLC.

        `assignments`: key-value pairs to write, symbolic or absolute
            or a tuple (key, value, fmt) if you want to specify one
        `fmt`: format used for communication with the PLC
            (default bool)
        `check`: Verify whether write succeeded

        """

        self._check_fmt(fmt)
        data = {'PriNav': 'Varstate',}

        for n, dtup in enumerate(assignments):
            p_point, p_val = dtup[:2]

            try:
                p_fmt = dtup[2]
            except IndexError:
                p_fmt = fmt

            data['v%d' % (n+1)] = p_point
            data['t%d' % (n+1)] = p_fmt
            data['modifyvalue_t%d' % (n+1)] = DATA_MAPPING_REV.get(p_fmt, str)(p_val)
            data['gobutton_t%d' % (n+1)] = 'Go'

            req = self.get(self._build_url(URL_VARSET),
                           params=data, prefetch=True, allow_redirects=False)

        if check:
            raise NotImplementedError

    def read_values(self, identifiers, fmt="BOOL"):
        """
        Reads one or more values from the PLC.

        `identifiers`: list of values to read, symbolic or absolute
            or a tuple (identifier, fmt) if you want to specify one
        `fmt`: format used for communication with the PLC
            (default bool)

        """

        self._check_fmt(fmt)
        full_identifiers = []

        data = {'PriNav': 'Varstate',}

        for n, point in enumerate(identifiers):
            if isinstance(point, basestring):
                p_fmt = fmt
                p_point = point
            else:
                p_point, p_fmt = point

            self._check_fmt(p_fmt)

            data['v%d' % (n+1)] = p_point
            data['t%d' % (n+1)] = p_fmt

            full_identifiers.append((p_point, p_fmt))

        req = self.get(self._build_url(URL_BASE), params=data)

        if LXML_AVAILABLE:
            tree = lxml.html.parse(req.raw)
            raw_values = [x.strip() for x in tree.xpath("//div[starts-with"
                                    "(@id,'dynamic_contentt')]/text()")[:-1]]
            raw_fmts = tree.xpath("//select[@class='Variable_Type_Selection_Box']"
                                  "/option[@selected]/text()")
        else:
            # Parsing HTML with regexes is evil, but fast :)
            # (and this is a limited subset of HTML)

            raw_values = RE_VAR.findall(req.content)
            raw_fmts = RE_FMT.findall(req.content)

        results = {}

        for n, value, fmt in zip(range(len(raw_values)), raw_values, raw_fmts):
            if full_identifiers[n][1] != fmt:
                raise ValueError("Format for %s not accepted" %
                                 full_identifiers[n][0])

            if not len(value):
                results[full_identifiers[n][0]] = None
                continue

            results[full_identifiers[n][0]] = DATA_MAPPING.get(fmt, str)(value)

        return results

    @login_required
    def sps_run(self):
        self.post(self._build_url(URL_CMD), data={'Run': ' ',})

    @login_required
    def sps_stop(self):
        self.post(self._build_url(URL_CMD), data={'Stop': ' ',})

    @login_required
    def sps_flash_led(self):
        self.post(self._build_url(URL_CMD), data={'FlashLed': ' ',})

    def sps_time(self):
        raise NotImplementedError


def main():
    plc = S7WebComm('sps.dk0fr')

    #if 'WINGDB_ACTIVE' in os.environ:
        #plc.proxies = dict(http="127.0.0.1:8887")

    print "CPU status:", plc.sps_status()
    print "CPU identification:", plc.sps_information()
    print "Logged in:", plc.logged_in

    ### SENSITIVE DEBUG CODE ###

    if not plc._logged_in:
        print "Logging in, Status:", plc.login("[...]")

    ###    DEBUG CODE END    ###

    print "Bypass status:", plc.read_values([
        ('RemoteControl.SBy UKW', 'BOOL'),
        ('RemoteControl.DoesNotExist', 'BOOL'),
        ('RemoteControl.SBy KW', 'BOOL'),
    ])

    print "S/R SBy KW..."
    print plc.set_value("RemoteControl.SBy KW", True)
    print plc.set_value("RemoteControl.SBy KW", False)
    print "SBy KW:", plc.read_value("RemoteControl.SBy KW")


if __name__ == '__main__':
    main()
