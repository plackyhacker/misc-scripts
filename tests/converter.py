import argparse
import base64
import pyperclip
import sys

from rich.console import Console

def main():
  console = Console()
  title = "\n[white bold]~-~-~[/][blue bold]([yellow bold]Simple Shellcode Convertor v1.0[/][blue bold])[/][white bold]~-~-~[/]\n"
  console.print(title)
  
  args = parse_args()
  format = args.format
  clip = args.clipboard
  offset = args.offset

  str = get_header(format)

  try:
    f = open(args.raw, 'rb')
  except:
    console.print("[red bold][!] [white]Unable to process/open raw file: " + args.raw + "[/]")
    sys.exit(1)

  if format == "b64":
    enc = base64.b64encode(f.read())
    str = enc.decode("utf8")
  else:
    with f:
      while 1:
        byte_s = f.read(1)
        if not byte_s:
          break
        byte = byte_s[0]
        if offset != False:
          if byte != 255:
            byte += 1
        str += get_byte(format, byte)
    
    str = str.rstrip(',')
    str = str + get_footer(format)

  console.print("[yellow bold][*] [white]Shellcode:")
  console.print("[white]" + str + "[/]")

  if clip == True:
    console.print("\n[yellow bold][*] [white]Shellcode copied to clipboard!")
    pyperclip.copy(str)

  f.close()

def get_header(format):
  if format == 'c':
    return 'unsigned char buf[] = "'
  elif format == 'cs':
    return 'byte[] buf = {'
  elif format == 'ps':
    return '[byte[]] $buf = '
  elif format == 'py':
    return 'buf = b\''
  elif format == 'b64':
    pass

def get_footer(format):
  if format == 'c':
    return '";'
  elif format == 'cs':
    return '};'
  elif format == 'ps':
    return ''
  elif format == 'py':
    return '\''
  elif format == 'b64':
    pass

def get_byte(format, byte):
  if format == 'c':
    return "\\x" + hex(byte).replace("0x", "").rjust(2, "0")
  elif format == 'cs':
    return hex(byte) + ','
  elif format == 'ps':
    return hex(byte) + ','
  elif format == 'py':
    return "\\x" + hex(byte).replace("0x", "").rjust(2, "0")
  elif format == 'b64':
    pass

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-r", "--raw", help="The raw binary file to convert.", type=str, required=True)
  parser.add_argument("-f", "--format", help="The output format: c, cs, ps, py, b64", type=str, required=True)
  parser.add_argument("-c", "--clipboard", help="Copy output to the clipboard.", action='store_true')
  parser.add_argument("-o", "--offset", help="Offset the value of each byte by 1 for obfuscation.", action='store_true')

  args = parser.parse_args()
  return args

if __name__ == '__main__':
  main()

