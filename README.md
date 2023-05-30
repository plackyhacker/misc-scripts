# Miscellanious Scripts

## OSED

### Bad Character Check

[Bad Character Check](https://github.com/plackyhacker/misc-scripts/blob/main/osed/bad-char-check.py)

Checks for bad characters in custom x86 shellcode. This is really useful when you have bad characters present and need to change the shellcode without using decoding (e.g., when using `WriteProcessMemory` in a ROP chain):

```
usage: bad-char-check.py [-h] [--asm ASM] --badchars BADCHARS [--scroll SCROLL] [--raw RAW] [--txt TXT] [--platform PLATFORM]

options:
  -h, --help            show this help message and exit
  --asm ASM, -a ASM     The asm instruction file to check.
  --badchars BADCHARS, -b BADCHARS
                        The bad chars to highlight.
  --scroll SCROLL, -s SCROLL
                        Set to scroll after number of lines output.
  --raw RAW, -r RAW     Raw file as an input, e.g., msfvenom output.
  --txt TXT, -t TXT     Space delimited text file as an input.
  --platform PLATFORM, -p PLATFORM
                        Platform x86/x64.
```

<img width="1453" alt="Screenshot 2023-05-30 at 14 11 40" src="https://github.com/plackyhacker/misc-scripts/assets/42491100/dcfdae6b-c197-48bb-b1cb-e076ac4bec05">

The script can also be used to analyse an `msfvenom` raw file and a space delimited text file.

### IP to Hex

[IP to Hex](https://github.com/plackyhacker/misc-scripts/blob/main/osed/ip-to-hex.py)

Simple script to convert an IP address to a 32-bit x86 `push` instruction:

```
python3 ./ip-to-hex.py 192.168.1.166  

push 0xa601a8c0;                #   Push sin_addr (192.168.1.166)
```

### Find Win32 APIs

[Find Win32 APIs](https://github.com/plackyhacker/misc-scripts/blob/main/osed/find-win32-apis.py)

Searches a loaded module for IAT references to APIs.

### ROP Finder General

[ROP Finder General](https://github.com/plackyhacker/misc-scripts/blob/main/osed/rop-finder-general.py)

Searches an `rp++` output for common ROP gadgets:

```
./rop-finder-general.py -f ../gadgets.txt -b "0x00 0x0a 0x80 0x81"

~-~-~(RoP fInDeR gEnErAl v1.0)~-~-~

  0. Ref ESP/EBP Gadgets
  1. MOV/XCHG Gadgets
  2. PUSHAD Gadgets
  3. Pointer Deref Gadgets
  4. Save to Pointer Gadgets
  5. POP Gadgets
  6. PUSH-POP Gadgets
  7. Zeroing Gadgets
  8. INC Gadgets
  9. DEC Gadgets
  a. NEG Gadgets
  b. ADD Gadgets
  c. SUB Gadgets
  d. Custom RegEx
  e. Quit
```
