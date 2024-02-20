// example backdoor request and response, using backdoor.asm
// John Tear, 2024

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <windows.h>
#include <winddi.h>

#define MAX_OUT_BUFFER 64

extern "C"
{
    int SendRPCRequest(const char* in, size_t size, char* out);
}

int main()
{
    // we can use this address to debug our assembly code
    printf("[+] Address of SendRPCRequest: 0x%p\n", SendRPCRequest);

    // allocate a buffer for the RPC response
    char* reply = (char*)malloc(sizeof(char*) * MAX_OUT_BUFFER);
    memset(reply, 0x0, sizeof(char*) * MAX_OUT_BUFFER);
    const char* buffer = "info-get guestinfo.ip";

    // output some debug info
    printf("[+] Input: %s\n", buffer);
    printf("[+] Address of In Buffer: 0x%p\n", buffer);
    size_t length = strlen("info-get guestinfo.ip");
    printf("[+] Size of In Buffer: %d\n", length);
    printf("[+] Address of Out Buffer: 0x%p\n", reply);

    // this gives us an opportunity to attach windbg
    printf("[!] Press a key to continue...");
    getchar();
    printf("[+] Sending RPC request...\n");

    // send the rpc request
    SendRPCRequest(buffer, length, reply);

    // print the output
    printf("[+] Output: %s\n", reply);
    printf("[+] Done!\n");

    // free the allocated buffer
    free(reply);

    return 0;
}
