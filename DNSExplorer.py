#!python3

import argparse
import dns, dns.query, dns.resolver, dns.zone
import socket
from pathlib import Path
from termcolor import colored
from time import sleep

def find_ns(domain: str) -> dict:

    try:
        resolv = dns.resolver.resolve(domain, "NS")
        names = [ str(r) for r in resolv ]
        
        return names
        
    except (dns.resolver.NXDOMAIN):
        return None


def transfer_zone(domain: str) -> str:
    
    tz = False
    servers = find_ns(domain)
    if servers != None:

        ns = {}
        for name in servers:
            for ip in dns.resolver.resolve(name, "A"):
                ns[name] = str(ip)

        print("")
        print(colored(f"[*] ", "blue", attrs=['bold']), end="")
        print(colored(f"Find ", "blue"), end="")
        print(colored(f"{len(ns)} ", "blue", attrs=['bold']), end="")
        print(colored("Nameservers for the domain ", "blue"), end="")
        print(colored(f"{domain}", "blue", attrs=['bold']))
        print("")
        print("".join(f"{key} ({value})\n" for key, value in ns.items()))
        sleep(2)
        
        for server in servers:
            try: 
                transfer = dns.zone.from_xfr(dns.query.xfr(ns[server], domain))
                print(colored("\n[+] Success transfer zone to ", 'green'), end="")
                print(colored(server, 'green', attrs=['bold']))
                for i in transfer:
                    print(f"{i}.{domain}")
                
                print("")
                
                tz = True

            except (dns.xfr.TransferError, ConnectionRefusedError, dns.exception.FormError):
                print(colored("[-] Fail transfer zone to ", 'red'), end="")
                print(colored(server, 'red', attrs=['bold']))

            sleep(2)

        if tz:
            return True
        else:
            print("\nTransfer zone is not possible for this domain!")
            print("Trying via bruteforce!!")
            return False                
    
    else:
        print(f"No nameservers were found for the domain {domain}")
        print("Trying via bruteforce!!")
        return False


def reverse_dns(ip: str) -> list:

    try:
        result = socket.gethostbyaddr(ip)
        return [result[0]]+result[1]
    except socket.herror:
        return None


def dns_request(subdomain: str) -> list:

    ips = []
    try:
        result = dns.resolver.resolve(subdomain)
        if result:
            print("")
            print(colored(subdomain, 'blue', attrs=['bold']))
            for answer in result:                
                print(answer)
                print(f"Domain Names: {reverse_dns(answer.to_text())}")
    except (dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.resolver.NoAnswer):
        return []

    return ips


def subdomains_bruteforce(domain: str, wordlist: list, nums: int) -> None:

    for word in wordlist:
        subdomain = f"{word}.{domain}"
        dns_request(subdomain)
        if nums > 0:
            for i in range(0,nums):
                s = f"{word}{str(i)}.{domain}"
                dns_request(s)


def prepare_wordlist(wordl: str) -> list:

    while not Path(wordl).is_file():
        print("")
        print(colored(f"[!] The file {wordl} do not exists!!", "yellow", attrs=['bold']))
        wordl = input('''
        Please insert the path of the valid wordlist:
        >>> ''')


    with open(wordl,"r") as f:
        wordlist = f.read().splitlines()

    return wordlist


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Tool to DNS transfer zones and subdomains bruteforce")
    parser.add_argument('-d', help='Domain to be ennumerate.', required=True)
    parser.add_argument('-w', help='Wordlist to subdomains bruteforce.', required=True)
    parser.add_argument('-n', help='Number of interactions in the same subdomain (Ex: mx..mx1..mx2..).', required=True)
    parsed = parser.parse_args()

    if not transfer_zone(parsed.d):
        subdomains_bruteforce(parsed.d, prepare_wordlist(parsed.w), int(parsed.n))