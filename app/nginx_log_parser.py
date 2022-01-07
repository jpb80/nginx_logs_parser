#!/usr/bin/env python
# coding=utf-8

import ipaddress
import json
import logging
import os
import sys

from pygrok import Grok

log = logging.getLogger(__name__)
NGINX_LOG_FILEPATH = os.environ['NGINX_LOG_FILEPATH']
SUBNETS = os.environ["SUBNETS"].split(',')
LOGLEVEL = os.environ['LOGLEVEL']


def setup_logging():
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=LOGLEVEL, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def load_nginx_logs_to_dict(filepath):
    """
    Load each line from the nginx log file. Parse that line with Grok pattern 
    matching into a dict object. Group together the nginx objects by remote
    ipaddress. 
    {
        '123.123.123.4': [{'remote_addr':'123...', 'verb':'GET'}]
    }
    Return: dictionary
    """
    log.info("Loading nginx logs into dictionary.")
    results = {}
    try:
        with open(filepath, 'r') as _file:
            while (line := _file.readline().rstrip()):
                log.debug("log line: %s", line)
                parsed_log = parse_nginx_logs(line)
                log.debug("parsed log: %s", parsed_log)
                if results.get(parsed_log['remote_addr']):
                    log.debug("ip address exists, append to the list: %s", 
                              parsed_log['remote_addr'])
                    results[parsed_log['remote_addr']].append(parsed_log)
                else:
                    log.debug("ip address does not exist, create a new list: %s", 
                              parsed_log['remote_addr'])
                    results[parsed_log['remote_addr']] = [parsed_log]
    except IOError as io:
        log.exception("Error reading file has occurred: %s", io)
    except Exception as ex:
        log.exception("Failed to load and parse logs.")
    return results


def parse_nginx_logs(log_line):
    """
    Use Grok pattern matching to match column fields to keys in a dictionary.
    Return: dictionary
    """
    log.debug("Log line: %s", log_line)
    pattern = "%{IPORHOST:remote_addr} - - \[%{HTTPDATE:time_local}\] \"(?:%{WORD:verb} %{NOTSPACE:request}(?: HTTP/%{NUMBER:version})?|-)\" %{NUMBER:status} (-|%{INT:body_bytes_sent}) \"-\" \"%{GREEDYDATA:referrer}\""
    try:
        grok = Grok(pattern)
        parsed_log = grok.match(log_line)
        log.debug("Parse nginx log line: %s", parsed_log)
    except Exception as exc:
        log.exception("Parsing nginx logs: %s", exc)
    return parsed_log


def get_ipaddress_occurrences(ipaddresses_details_dict):
    """
    Use the dictionary keys of unique ipaddresses to determine number of
    occurrences. 
    """
    log.info("Get count of unqiue ipaddresses.")
    log.debug("ipaddresses_details_dict %s", ipaddresses_details_dict)
    results = {}
    try:
        for ipaddr, addr_array in ipaddresses_details_dict.items():
            log.debug("check ipaddress for occurrences: %s", ipaddr)
            results[ipaddr] = len(addr_array)
            log.debug("occurrences: %s", len(addr_array))
    except Exception as ex:
        log.exception("An error has occurred: %s", ex)
    return results


def get_distinct_ipaddress_by_subnets(ipaddress_occurrences_dict, subnets):
    """
    Use the unique ipaddresses to determine if they belong to the set of
    subnets.
    Return: dictionary of subnet to number of ip addresses that belonged to it.
    """
    log.info("Get distinct ipaddress that belong to subnets: %s", subnets)
    results = {}
    try:
        for subnet in subnets:
            log.debug("Subnet: %s", subnet)
            for ip in ipaddress_occurrences_dict.keys():
                log.debug("IP address: %s", ip)
                if ipaddress.ip_address(ip) in ipaddress.ip_network(subnet):
                    if results.get(subnet):
                        results[subnet] += 1
                        log.debug("%s ipaddresses  in subnet %s",
                                  results[subnet], subnet)
                    else:
                        results[subnet] = 1
                        log.debug("%s ipaddresses in subnet %s",
                                  results[subnet], subnet)
    except Exception as ex:
        log.exception("An error has occurred: %s", ex)
    return results


def output_results(ipaddress_occurrences_dict,
                   distinct_ipaddresses_by_subnet_dict):
    """
    Output readable results to stdout and as a dictionary object.
    """
    results = {'buckets': {},
               'remote_address_occurrences': {}}
    for addr, occurrence in ipaddress_occurrences_dict.items():
        results['remote_address_occurrences'][addr] = occurrence
        print(f'Address {addr} was encountered {occurrence} time(s)')
    
    for subnet, addresses in distinct_ipaddresses_by_subnet_dict.items():
        results['buckets'][subnet] = addresses
        print(f'The bucket {subnet} contains {addresses} addresses')
    return results
    

def main():
    setup_logging()
    log.info("Begin processing nginx logs...")
    ipaddresses_details_dict = load_nginx_logs_to_dict(filepath=NGINX_LOG_FILEPATH)
    ipaddress_occurrences_dict = get_ipaddress_occurrences(ipaddresses_details_dict)
    distinct_ipaddresses_by_subnet_dict = get_distinct_ipaddress_by_subnets(ipaddress_occurrences_dict, 
                                                                           subnets=SUBNETS)
    results = output_results(ipaddress_occurrences_dict, 
                             distinct_ipaddresses_by_subnet_dict)
    return results


if __name__ == '__main__':
    main()
