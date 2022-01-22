#!python3

import argparse
import dns, dns.query, dns.resolver, dns.zone
import socket
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
        lista = {}
        for name in servers:
                for ip in dns.resolver.resolve(name, "A"):
                    lista[name] = str(ip)
        
        for server in servers:
            try: 
                transfer = dns.zone.from_xfr(dns.query.xfr(lista[server], domain))
                print(colored("\n\n[+] Success transfer zone to ", 'green'), end="")
                print(colored(server, 'green', attrs=['bold']))
                for i in transfer:
                    print(f"{i}.{domain}")
                
                tz = True

            except (dns.xfr.TransferError, ConnectionRefusedError, dns.exception.FormError):
                print(colored("\n\n[-] Fail transfer zone to ", 'red'), end="")
                print(colored(server, 'red', attrs=['bold']))

            sleep(2)

        if tz:
            return True
        else:
            print("\nTransfer not is not possible for this domain!")
            return False                
    
    else:
        print(f"Não foram encontrados servidores de nomes para o domínio {domain}")
        print("Tentando via Força Bruta!!")

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
            print(colored(subdomain, 'blue', attrs=['bold']))
            for answer in result:                
                print(answer)
                print(f"Domain Names: {reverse_dns(answer.to_text())}")
    except (dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.resolver.NoAnswer):
        return []

    return ips

def search_subdomain(domain: str, wordlist: list, nums: bool) -> None:

    for word in wordlist:
        print("")
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
    
    if not transfer_zone(parsed.d):
        search_subdomain(parsed.d, wordlist, True)