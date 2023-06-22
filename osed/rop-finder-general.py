#!/usr/bin/python3
# rop-finder-general.py
# Script to find 32-bit x86 rop gadgets in rp++ outputs
# Written for my OSED exam/studies
# 
# John Tear
# 

import sys, os, argparse, re
from rich.console import Console

global console
global options

options = ["Ref ESP/EBP Gadgets",
           "MOV/XCHG Gadgets",
           "PUSHAD Gadgets",
           "Pointer Deref Gadgets",
           "Save to Pointer Gadgets",
           "POP Gadgets",
           "PUSH-POP Gadgets",
           "Zeroing Gadgets",
           "INC Gadgets",
           "DEC Gadgets",
           "NEG Gadgets",
           "ADD Gadgets",
           "SUB Gadgets",
           "Custom RegEx",
           "Quit"
           ]

def loop():
    global console
    global options
    global lines

    os.system('clear')
    
    title = "[white bold]~-~-~[/][blue bold]([red bold]RoP fInDeR gEnErAl v1.0[/][blue bold])[/][white bold]~-~-~[/]\n"

    console.print(title)
    
    for i in range(len(options)):
        console.print("[white bold]  %s. %s[/]" % (hex(i).replace("0x", ""), options[i]))

    choice = console.input("\n[white bold] > [/]")
    
    os.system('clear')

    try:
        i_choice = int(choice, 16)
    except:
        loop()

    if i_choice >= len(options) - 1 or i_choice < 0:
        sys.exit(0)

    console.print(title)

    if i_choice == 0:
        find_ref_esp(lines)
    elif i_choice == 1:
        find_swap_registers(lines)
    elif i_choice == 2:
        find_pushad(lines)
    elif i_choice == 3:
        find_pointer_deref(lines)
    elif i_choice == 4:
        find_save_to_pointer(lines)
    elif i_choice == 5:
        find_pops(lines)
    elif i_choice == 6:
        find_push_pops(lines)
    elif i_choice == 7:
        find_xor_zeroing(lines)
    elif i_choice == 8:
        find_inc_gadgets(lines)
    elif i_choice == 9:
        find_dec_gadgets(lines)
    elif i_choice == 10:
        find_neg_gadgets(lines)
    elif i_choice == 11:
        find_add_gadgets(lines)
    elif i_choice == 12:
        find_sub_gadgets(lines)
    elif i_choice == 13:
        find_using_regex(lines)

    console.input("\n[white bold]Press enter to continue...[/]")
    loop()

def print_found(line):
    global found_items
    global base
    rtnstring = ""

    if "call" in line or "jmp" in line:
        return

    address = line.split(":")[0].replace("0x", "")
    orig_address = int(address, 16)
    base_addr = int(base, 16)
    offset_addr = orig_address - base_addr

    address = hex(orig_address).replace("0x", "")

    bytes = ["0x" + address[0:2], "0x" + address[2:4], "0x" + address[4:6], "0x" + address[6:8]]

    foundbad = False

    for b in bytes:
        if b in badchars:
            foundbad = True

    if foundbad:
        return
    else:
        comments = "# " + line.split(":")[1].split("(")[0].replace(" ;", ";").replace(" ;", ";")

        line = line.replace("fs:", "$$fs$$")
        rtnstring += "inputBuffer += pack(\"<L\", dllBase + " + hex(offset_addr) + "))".ljust(20) + "# " + line.split(":")[0] + " " + line.split(":")[1].split("(")[0].replace(" ;", ";").replace(" ;", ";")
        rtnstring = rtnstring.replace("$$fs$$", "fs:")

    if rtnstring != "":
        print(rtnstring)
    
    index = line.split(":")[1].split("found)")[0].split("(")[0].lstrip(" ")
    if index not in found_items:
        found_items.append(index)

def find_using_regex(lines):
    term = console.input("\n[white bold] RegEx > [/]")

    global found_items
    found_items = []

    print("\nCustom RegEx")
    print("-------------")
    apply_regex(lines, term, [""])
    print("")

def find_ref_esp(lines):
    global found_items
    found_items = []
    print("Ref ESP/EBP Gadgets")
    print("-------------------")
    term = "push e+.p ;"
    apply_regex(lines, term, ["push"])
    term = "lea e+.[xpi], dword \[e[bs]p+.0x"
    apply_regex(lines, term, ["lea"])
    term = "mov e+.[xi], e[bs]p"
    apply_regex(lines, term, ["mov"])
    print("")

def find_pushad(lines):
    global found_items
    found_items = []
    print("PUSHAD Gadgets")
    print("--------------")
    term = "pushad+.*"
    apply_regex(lines, term, ["pushad"])
    print("")

def find_swap_registers(lines):
    global found_items
    found_items = []
    print("MOV/XCHG Gadgets")
    print("----------------")
    term = "mov e.[xpi], e.[xpi] ;|xchg e.[xpi], e.[xpi] ;"
    apply_regex(lines, term, ["mov", "xchg"])
    print("")

def find_pointer_deref(lines):
    global found_items
    found_items = []
    print("Pointer Deref Gadgets")
    print("---------------------")
    term = "mov e.[xpi], dword \["
    apply_regex(lines, term, ["mov"])
    print("")

def find_save_to_pointer(lines):
    global found_items
    found_items = []
    print("Save to Pointer Gadgets")
    print("-----------------------")
    term = "mov dword \[e.[xpi]\], e.[xpi]"
    apply_regex(lines, term, ["mov"], limit=10)
    term = "mov dword \[e.[xpi].+\], e.[xpi]"
    apply_regex(lines, term, ["mov dword"], limit=10)
    print("")

def find_pops(lines):
    global found_items
    found_items = []
    print("POP Gadgets")
    print("-----------")
    term = "pop e.[xpi]"
    apply_regex(lines, term, ["pop"], limit = 20)
    print("")

def find_push_pops(lines):
    global found_items
    found_items = []
    print("PUSH-POP Gadgets")
    print("----------------")
    term = "push e.[xpi]+.*pop"
    apply_regex(lines, term, ["push"], limit = 10)
    print("")

def find_xor_zeroing(lines):
    global found_items
    found_items = []
    print("Zeroing Gadgets")
    print("---------------")
    term = "\\bxor eax+.*"
    apply_regex(lines, term, ["xor"], limit = 5)
    term = "\\bxor ebx, ebx"
    apply_regex(lines, term, ["xor"], limit = 5)
    term = "\\bxor ecx, ecx+.*"
    apply_regex(lines, term, ["xor"], limit = 5)
    term = "\\bxor edx, edx"
    apply_regex(lines, term, ["xor"], limit = 5)
    term = "\\bxor esi, esi"
    apply_regex(lines, term, ["xor"], limit = 5)
    term = "\\bxor edi, edi"
    apply_regex(lines, term, ["xor"], limit = 5)

    term = "\\bmov eax, 0x00000000"
    apply_regex(lines, term, ["mov"], limit = 5)
    term = "\\bmov ebx, 0x00000000"
    apply_regex(lines, term, ["mov"], limit = 5)
    term = "\\bmov ecx, 0x00000000"
    apply_regex(lines, term, ["mov"], limit = 5)
    term = "\\bmov edx, 0x00000000"
    apply_regex(lines, term, ["mov"], limit = 5)
    term = "\\bmov esi, 0x00000000"
    apply_regex(lines, term, ["mov"], limit = 5)
    term = "\\bmov edi, 0x00000000"
    apply_regex(lines, term, ["mov"], limit = 5)

    print("")


def find_inc_gadgets(lines):
    global found_items
    found_items = []
    print("INC Gadgets")
    print("-----------")
    term = "inc e.[xpi]"
    apply_regex(lines, term, ["inc"], limit = 10)
    print("")

def find_dec_gadgets(lines):
    global found_items
    found_items = []
    print("DEC Gadgets")
    print("-----------")
    term = "dec e.[xpi]"
    apply_regex(lines, term, ["dec"], limit = 10)
    print("")

def find_neg_gadgets(lines):
    global found_items
    found_items = []
    print("NEG Gadgets")
    print("-----------")
    term = "neg e.[xpi]"
    apply_regex(lines, term, ["neg"], limit = 10)
    print("")

def find_sub_gadgets(lines):
    global found_items
    found_items = []
    print("SUB Gadgets")
    print("-----------")
    term = "sub e.[xpi]"
    apply_regex(lines, term, ["sub"])
    print("")

def find_add_gadgets(lines):
    global found_items
    found_items = []
    print("ADD Gadgets")
    print("-----------")
    term = "add e.[xpi]"
    apply_regex(lines, term, ["add"])
    print("")

def starts_with(line, terms):
    for term in terms:
        if line.startswith(term):
            return True
    return False

def apply_regex(lines, term, must_start_with, limit = 16):
    global found_items
    count = 0

    for line in lines:
        found = re.findall(term, line)
        for f in found:
            if count == limit:
                return
            else:
                index = line.split(":")[1].split("found)")[0].split("(")[0].lstrip(" ")
                if starts_with(index, must_start_with):
                    if index not in found_items:
                        count = count + 1
                        print_found(line)

def main():
    global badchars
    global base
    global found_items
    global lines
    global console
    
    console = Console()

    found_items = []

    parser = argparse.ArgumentParser()
    parse_args(parser)
    args = parser.parse_args()

    badchars = args.badchars
    base = args.base
    baseaddr = int(base, 16)
    base = hex(baseaddr)

    f = open(args.file)
    lines = f.readlines()
    f.close()

    lines.sort(key=len, reverse=False)

    loop()


def parse_args(parser):
    parser.add_argument('--file','-f', type=str, action='store', required=False, default="./rop.txt",
                    help='The file to search.')
    parser.add_argument('--badchars','-b', type=str, action='store', required=False, default ="0x00",
                    help='The bad chars to ignore')
    parser.add_argument('--base', type=str, default = "10000000", required = False,
                    help='Module preferred base address')

if __name__ == "__main__":
    main()
