# Miscellanious Scripts

## OSED

### Bad Character Check

[Bad Character Check](https://github.com/plackyhacker/misc-scripts/blob/main/osed/bad-char-check.py)

Checks for bad characters in custom x86 shellcode. This is really useful when you have bad characters present and need to change the shellcode without using decoding (e.g., when using `WriteProcessMemory` in a ROP chain):

```
python3 ./bad-char-check.py                                                            
usage: bad-char-check.py [-h] [--asm ASM] --badchars BADCHARS [--raw RAW] [--scroll SCROLL] 
bad-char-check.py: error: the following arguments are required: --badchars/-b

python3 ./bad-char-check.py -a ./test.asm -b "0x00 0x0a 0x11 0xff" -s 20
0x1000  pushal                                         ; 60 
0x1001  push   ebp                                     ; 55 
0x1002  mov    ebp, esp                                ; 89 e5 
0x1004  push   eax                                     ; 50 
0x1005  push   esp                                     ; 54
...
```

The script can also be used to analyse an `msfvenom` raw file:

```
python3 ./bad-char-check.py -r ./met.raw -b "0x00 0x0a 0x11 0xff" -s 20
```

### IP to Hex

[IP to Hex](https://github.com/plackyhacker/misc-scripts/blob/main/osed/ip-to-hex.py)

Simple script to convert an IP address to a 32-bit x86 `push` instruction:

```
python3 ./ip-to-hex.py 192.168.1.166  

push 0xa601a8c0;                #   Push sin_addr (192.168.1.166)
```

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
