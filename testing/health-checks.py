#!/usr/bin/env python
from __future__ import print_function
import sys
import json
import base64
import urllib2


# should we have a global exit status, or just exit early for any errors?
EXIT_STATUS = 0


def get_credentials():
    yaml_key = "chronos_http_credentials:"
    with open('security.yml') as f:
        for line in f:
            if yaml_key in line:
                # credentials are the whole string after the key
                credentials = line[len(yaml_key):].strip()
                # only grab what we need
                return credentials


def node_health_check(node_address):
    global EXIT_STATUS
    url = "https://" + node_address + "/consul/v1/health/state/any"
    auth = b'Basic ' + base64.b64encode(get_credentials())
    request = urllib2.Request(url)
    request.add_header("Authorization", auth)
    try:
        f = urllib2.urlopen(request)
        health_checks = json.loads(f.read().decode('utf8'))

        for check in health_checks:
            if check['Status'] != "passing":
                print(check['Name'] + ": not passing.")
                EXIT_STATUS = 1
            else:
                print(check['Name'] + ": passing.")
    except Exception, e:
        print("Skipping IP ", node_address, " due to this error\n", e)


def cluster_health_check(ip_addresses):
    for node_address in ip_addresses:
        print("Testing node at IP: " + node_address)
        node_health_check(node_address)
        print("Done testing " + node_address)


if __name__ == "__main__":

    address_list = sys.argv[1:]
    print("Health check starting now")
    cluster_health_check(address_list)
    print("Health check finished. Exiting now")
    sys.exit(EXIT_STATUS)
