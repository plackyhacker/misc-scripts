# Miscellanious Scripts
Miscellaneous Scripts

## OSED

[bad-char-check.py](https://github.com/plackyhacker/misc-scripts/blob/main/osed/bad-char-check.py)

```
python3 ./bad-char-check.py                                                            
usage: bad-char-check.py [-h] --asm ASM --badchars BADCHARS [--scroll SCROLL]
bad-char-check.py: error: the following arguments are required: --asm/-a, --badchars/-b

python3 ./bad-char-check.py -a ./test.asm -b "0x00 0x0a 0x11 0xff" -s 20
0x1000  pushal                                         ; 60 
0x1001  push   ebp                                     ; 55 
0x1002  mov    ebp, esp                                ; 89 e5 
0x1004  push   eax                                     ; 50 
0x1005  push   esp                                     ; 54
...
```
