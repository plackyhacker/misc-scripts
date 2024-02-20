PUBLIC SendRPCRequest

.DATA

.CODE

SendRPCRequest PROC

    ; prep the stack
    push rbx
    push rsi
    push rdi
    push rbp
    mov rbp, rsp
    ;sub rsp, 32                 ; Shadow Space
    ;and spl, -16                ; Align stack at 16
    


    ; store variables
    mov r12, rcx                 ; address of input buffer
    mov r13, rdx                 ; size of input buffer
    mov r14, r8                  ; address of output buffer

    ; open the RPC channel
    mov eax, 0564D5868h					; Magic number 'VMXh'
    mov ecx, 0001eh 						; MESSAGE_TYPE_OPEN
    mov edx, 05658h							; Low bandwidth
    mov ebx, 0C9435052h					; Magic number 'RPCI'
    in eax, dx									; Make the request

    ; save the RPC channel no.
    mov r15, rdx                 ; rdx contains the channel
                                 ; number in edx (hi)

    ; send the size of the cmd
    mov eax, 0564D5868h				   ; Magic number 'VMXh'
    mov ecx, 01001eh 					   ; MESSAGE_TYPE_SENDSIZE
    mov dx, 05658h						   ; Low bandwidth
                                 ; edx(hi) contains the channel
                                 ; number
    mov rbx, r13			 			     ; The size of the request
    in eax, dx								   ; Make the request
                                 ; esi and edi contain the 	
                                 ; cookies

    ; send the cmd
    mov eax, 0564D5868h				   ; Magic number 'VMXh'
    mov rcx, r13    				     ; The size of the request
    mov dx, 05659h						   ; Switch to high bandwidth
													       ; edx(hi) contains the channel
													       ; number
    mov ebx, 010000h				 	   ; Magic number
    mov ebp, esi							   ; Move cookie in to ebp
                                 ; edi and ebp now contain the
                                 ; cookies
    mov rsi, r12        	       ; Pointer to the command 	
                                 ; buffer
                                                            
    cld												   ; Clear the direction flag
    rep outsb                    ; Repeat string operation is used
                                                        
    ; receive the reply length
    mov eax, 0564D5868h				   ; Magic number 'VMXh'
    mov ecx, 03001eh 					   ; MESSAGE_TYPE_RECVSIZE
    mov dx, 05658h						   ; Low bandwidth
    mov esi, ebp							   ; Move cookie back in to esi
                                 ; edi and esi now contain the
                                 ; cookies
    in eax, dx									 ; make the request
                                 ; ebx should contain the reply length

    mov eax, 0564D5868h				   ; Magic number 'VMXh'
    mov ecx, ebx       				   ; The size of the reply data
    mov rdx, r15                 ; Restore the RPC channel
    mov dx, 05659h						   ; Switch to high bandwidth
													       ; edx(hi) contains the channel
													       ; number
    mov ebx, 010000h				 	   ; Magic number
    mov ebp, edi							   ; Move cookie in to ebp
                                 ; esi and ebp now contain the
                                 ; cookies
    mov rdi, r14                 ; Pointer to overwrite the 
                                 ; reply buffer with the reply
        
    cld												   ; Make the request
    rep insb                     ; Repeat string operation is used

    ; finish receiving reply
    mov eax, 0564D5868h					 ; Magic number 'VMXh'
    mov ecx, 05001eh 						 ; MESSAGE_TYPE_RECVSTATUS
    mov dx, 05658h							 ; low bandwidth
    mov edi, ebp							   ; Move cookie back in to edi
                                 ; edi and esi now contain the
                                 ; cookies
    mov ebx, edx                 ; copy replyid into ebx
    mov bx, 00000h               ; zero out lower bytes

    in eax, dx									 ; make the request

    ; close the RPC channel
    mov eax, 0564D5868h					 ; Magic number 'VMXh'
    mov ecx, 06001eh 						 ; MESSAGE_TYPE_CLOSE
    mov dx, 05658h							 ; low bandwidth
    in eax, dx									 ; make the request

    mov eax, 01h

    ; restore the stack
    pop rbp
    pop rdi
    pop rsi
    pop rbx
    ret

SendRPCRequest ENDP
END
