#!/usr/bin/python3
# find-win32apis.py
# Script written for to enumarate references to Win32 APIS for use in ROP chains 
# Note: Win32 API addresses change because of ASLR, we can use non-ASLR modules to try and find references
# 
# John Tear
# 

from pykd import *
import utility, sys

def find_base_and_size_of_iat(modname):
    # search headers of the module/image with the !dh command
    output = dbgCommand("!dh " + modname + " -f", True)

    #  parse the ouput to return the base address and table size
    lines = output.split("\n")
    for line in lines:
        if "Import Address Table Directory" in line:
            base_address = line.replace(" ", "").split("[")[0]
            iat_size = line.split("[")[1].split("]")[0].replace(" ", "")
            return base_address, iat_size

def find_apis_in_iat(modname, apis, base, size):
    # display the iat using the dps command
    entries = str(int(size, 16) / 4).split(".")[0]
    output = dbgCommand("dps " + modname + "+0x" + base + " L" + hex(int(entries)), True)

    #  parse the ouput looking for iat entries
    lines = output.split("\n")
    for line in lines:
        for api in apis:
            if api in line:
                print("[+] " + line)

def find_first_api_in_iat(modname, base, size):
    # display the iat using the dps command
    entries = str(int(size, 16) / 4).split(".")[0]
    output = dbgCommand("dps " + modname + "+0x" + base + " L" + hex(int(entries)), True)

    #  parse the ouput looking for iat entries
    lines = output.split("\n")
    for line in lines:
        if "KERNEL32" in line.upper():
                return line.split(" ")[0], line.split("!")[1]

def find_api_offset(refapi, api, base, size):
    # display the offset
    output = dbgCommand("? kernel32!" + refapi + " - " + "kernel32!" + api, True)

    #  return the offset
    return output.split(" ")[4].replace("\n", "")


def main():
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " [module_name]")
        sys.exit()

    # get the base address and size of iat in the module
    base, size = find_base_and_size_of_iat(sys.argv[1])

    # apis to find
    apis = ["VirtualProtect", "VirtualAlloc", "WriteProcessMemory"]
    # find the apis
    print ("---\n[!] Dereference the IAT address to get the target API.")
    find_apis_in_iat(sys.argv[1], apis, base, size)

    # find the apis by offset
    address, refapi = find_first_api_in_iat(sys.argv[1], base, size)
    base, size = find_base_and_size_of_iat("kernel32")
    print ("---\n[!] Dereference the IAT address, minus the offset to get the target API address.")
    for api in apis:
        offset = find_api_offset(refapi, api, base, size)
        print("[+] IAT of " + refapi + " is at dword[" + address + "], Offset is " + offset + " for " + api)

    print("---\n[+] Finished.")

# call main
main()
