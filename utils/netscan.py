#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

"""Provides features for network enumeration"""

import sys, os
import re

import envoy
import bs4

# TODO: use lxml XPath instead


PROPERTY_MAP = {
    'vendor': 'vendor',
    'ipv4': 'addr',
    'mac': 'addr',
    'hostname': 'name',
}


def ping_sweep(iprange="192.168.1-2.*", stored_log=None):
    """Runs an nMap ping sweep for a specified network range
    and returns the online hosts in a dictionary.

    If no `stored_log` is provided, the scan will be executed directly.

    """

    if not stored_log:
        nmap_log = envoy.run("nmap -sP {range} -oX -".format(range=iprange)).std_out
    else:
        nmap_log = open(stored_log).read()

    soup = bs4.BeautifulSoup(nmap_log)
    hosts = [status.find_parent() for status in soup.find_all("status", state="up")]

    hostlist = [{
        'ipv4': host.find('address', addrtype='ipv4'),
        'mac': host.find('address', addrtype='mac'),
        'vendor': host.find('address', addrtype='mac'),
        'hostname': host.hostname
    }
        for host in hosts
    ]

    for host in hostlist:
        for prop, val in host.viewitems():
            if val:
                host[prop] = host[prop].get(PROPERTY_MAP[prop], None)

    return hostlist


def main():
    import pprint
    import platform

    hostlist = (ping_sweep(stored_log="../nmaplog.xml") if
                platform.system() == "Windows" else ping_sweep())

    pprint.pprint(hostlist)


if __name__ == '__main__':
    main()