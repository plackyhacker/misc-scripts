import sys, argparse, socket, ipaddress
from threading import Thread
from queue import Queue
import requests
from rich.console import Console
import subprocess

def do_work():
    global q
    global ports
    global dns
    global timeout
    global verbose

    console = Console()

    # scan the host in a seperate thread
    while True:
        host = str(q.get())

        openports = []

        for port in ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((host, port))
                    s.settimeout(timeout)
                    openports.append(str(port))
                except Exception as e:
                    if "is unreachable" in str(e):
                        break
                    if "No route to host" in str(e):
                        break
                    pass

                try:
                    s.close()
                except:
                    pass

        # report back to the user
        openstring = ""
        for open in openports:
            openstring = openstring + open + " "

        if openstring != "":
            console.print("[green bold][+] [/][white bold]" + host + ": [/][green bold]" + openstring + "[/]")
        else:
            if verbose:
                console.print("[red bold][!] [/][white bold]" + host + ": [/][red bold]None[/]")

        q.task_done()

def main():
    global q
    global ports
    global dns
    global timeout
    global verbose

    # used by rich
    console = Console()
    console.print("\n[white bold]SYN/ACK Port Scanner by Plackyhacker\n------------------------------------[/]")

    args=parse_args()

    # verbosity
    verbose = args.verbose
    if verbose:
        console.print("[green bold][+] [/][white bold]Verbose output enabled...[/]\n")


    # the TCP timeout
    timeout = float(args.timeout)

    # the ports to scan
    if(args.ports == None):
        ports = [21, 22, 23, 25, 53, 80, 88, 110, 135, 139, 143, 389, 443, 465, 993, 995, 445, 1443, 3306, 3389, 5985, 5986, 8080, 8443]
    else:
        ports = []
        if args.ports == "all":
            for prt in range(1, 65536):
                ports.append(int(prt))
        else:
            p = args.ports.split(",")
            for prt in p:
                ports.append(int(prt))

    # The number of concurrent threads.
    concurrent = int(args.concurrent)
    
    # The hosts to scan - using CIDR
    hosts = ipaddress.IPv4Network(args.rhosts)

    q = Queue(concurrent * 2)
    for i in range(concurrent):
        t = Thread(target=do_work)
        t.daemon = True
        t.start()

    try:
        for ip in hosts:
            q.put(ip)
        q.join()
    except KeyboardInterrupt:
        sys.exit(1)
    
    console.print("\n[+] Done!")
    console.print("[white bold]----------------------------[/]\n")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--concurrent", help="Number of concurrent threads, default=100.", type=str, default="100")
    parser.add_argument("-r", "--rhosts", help="The hosts to scan, use CIDR.", type=str, required=True)
    parser.add_argument("-p", "--ports", help="The ports to scan (comma [,] delimited), use 'all' to scan for all ports.", type=str)
    parser.add_argument("-t", "--timeout", help="The TCP timeout value, default = 1.5.", type=str, default="1.5")
    parser.add_argument("-v", "--verbose", help="Run the script verbosely.", action='store_true')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()
