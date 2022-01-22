#!python3

import argparse
import dns
import dns.resolver
import socket

def reverse_dns(ip: str) -> list:
    
    try:
        result = socket.gethostbyaddr(ip)
        return [result[0]]+result[1]
    except socket.herror:
        return None

def dns_request(domain: str) -> list:

    ips = []
    try:
        result = dns.resolver.resolve(domain)
        if result:
            print(domain)
            for answer in result:
                print(answer)
                print(f"Domain Names: {reverse_dns(answer.to_text())}")
    except (dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.resolver.NoAnswer):
        return []

    return ips

def search_subdomain(domain: str, wordlist: list, nums: bool) -> None:

    for word in wordlist:
        subdomain = f"{word}.{domain}"
        dns_request(subdomain)
        if nums:
            for i in range(0,10):
                s = f"{word}{str(i)}.{domain}"
                dns_request(s)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Tool to ennumerate DNS and subdomains")
    parser.add_argument('-d', help='Domain to be ennumerate.', required=True)
    parser.add_argument('-w', help='Wordlist to subdomains bruteforce.', required=True)
    parsed = parser.parse_args()

    wordlist = []
    with open(parsed.w,"r") as f:
        wordlist = f.read().splitlines()

    search_subdomain(parsed.d, wordlist, True)