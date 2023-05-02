#!/usr/bin/python3
# bad-char-check.py
# Script written to take code and output bad characters for OSED
# It's a bit 'hacky' and probably not the way to do it, but it serves my needs
# 
# John Tear
# 

import sys, argparse
import ctypes, struct
from keystone import *
from capstone import *
from rich.console import Console

def main():
    # the instructions array is used to hold all of the instructions in one place
    global instructions
    instructions = []

    # used by rich
    console = Console()

    # get the arguments
    parser = argparse.ArgumentParser()
    parse_args(parser)
    args = parser.parse_args()

    file = ""

    if args.asm != "":
        file = args.asm
        f = open(file, "r")
    if args.raw != "":
        file = args.raw
        f = open(file, "rb")

    # open the asm file
    asm = f.read()
    bad = []
    f.close()

    # reformat the bad characters
    chars = args.badchars.split(' ')
    for c in chars:
        bad.append(int(c, 16))

    # encode the asm
    if args.asm != "":
        encodeAll(asm)
    else:
        instructions = asm

    # now decode so we have the instructions and the shellcode
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    counter = 0
    counter_scroll = int(args.scroll)

    for i in md.disasm(bytes(instructions), 0x1000):
        shellcode = ""
        for b in i.bytes:
            shellcode = shellcode + hex(b).replace("0x", "").rjust(2, "0") + " "
            
            address = hex(i.address)
            address = "[white bold]" + address.ljust(8, " ") + "[/]"

            if(i.mnemonic.startswith("call")):
                mnemonic = i.mnemonic.ljust(7, " ")
                op_str = i.op_str
                op_str = op_str.ljust(40, " ")
                mnemonic = "[green bold]%s[/]" % mnemonic
                op_str = op_str.replace("[", "\[")
                op_str = "[green bold]%s[/]" % op_str
            else:
                mnemonic = i.mnemonic.ljust(7, " ")
                op_str = i.op_str
                op_str = op_str.ljust(40, " ")
                mnemonic = "[blue bold]%s[/]" % mnemonic
                op_str = op_str.replace("[", "\[")
                op_str = "[blue bold]%s[/]" % op_str


        console.print(address + mnemonic + op_str + "; " + formatCode(shellcode, bad))
        counter = counter + 1
        if counter == counter_scroll:
            console.print("[white bold]\nHit enter for next, [C]ancel, or [A]ll[/]")
            answer = input("")
            if answer.upper() == "C":
                return
            if answer.upper() == "A":
                counter_scroll = 10000
            counter = 0


def formatCode(code, bad):
    if code == "":
        return ""
    
    nums = code.split(' ')
    retVal = ""

    for n in nums:
        if n == '':
            break
        if int(n, 16) in bad:
            retVal = retVal + "[red bold]" + n + '[/] '
        else:
            retVal = retVal + "[white bold]" + n + '[/] '

    return retVal

def encodeAll(code):
    ks = Ks(KS_ARCH_X86, KS_MODE_32)
    encoding, count = ks.asm(code)
    for b in encoding:
        instructions.append(int(hex(b).replace("0x", "").rjust(2, "0"), 16))

def parse_args(parser):
    parser.add_argument('--asm','-a', type=str, action='store', required=False, default = "",
                    help='The asm instruction file to check.')
    parser.add_argument('--badchars','-b', type=str, action='store', required=True, default ="0x00",
                    help='The bad chars to highlight.')
    parser.add_argument('--scroll','-s', type=str, action='store', required=False, default ="10000",
                    help='Set to scroll after number of lines output.')
    parser.add_argument('--raw','-r', type=str, action='store', required=False, default = "",
                    help='Raw file as an input, e.g., msfvenom output.')

if __name__ == "__main__":
    main()
