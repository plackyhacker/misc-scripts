#!/usr/bin/python3
# ip-to-hex.py
# Script written to take an ip address and convert it to a 
# 32-bit hex value that can be pushed on to the stack
# 
# John Tear
# 

import sys

def error(err):
    print("[!] %s" % err)
    print("Usage:   %s [ip address]" % sys.argv[0])
    print("Example: %s 192.168.1.228" % sys.argv[0])
    sys.exit(-1)

if len(sys.argv) < 2:
    error("Not enough arguments!")

ip = sys.argv[1]

octets = ip.split('.')

if len(octets) != 4:
    error("Invalid IP Address!")

hexip = ""
for o in octets:
    try:
        hexip = hex(int(o, 10)).replace("0x", "").rjust(2, "0") + hexip
    except:
        error("Unable to parse IP address!")

print()
print ("push 0x%s;\t\t#   Push sin_addr (%s)" % (hexip, ip))
