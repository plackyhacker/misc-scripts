import argparse

def main():
  args = parse_args()
  str = '[byte[]] $buf = '

  with open(args.file, 'rb') as f:
    while 1:
      byte_s = f.read(1)
      if not byte_s:
        break
      byte = byte_s[0]
      if byte != 255:
        byte += 1
      str += hex(byte) + ','

  str = str.rstrip(',')
  print(str)

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-f", "--file", help="The file to convert.", type=str, required=True)

  args = parser.parse_args()
  return args

if __name__ == '__main__':
  main()
