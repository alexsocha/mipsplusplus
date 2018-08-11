import argparse
import time
import os
import mipsplusplus

parser = argparse.ArgumentParser(description='MIPS++ compiler')
parser.add_argument('input', metavar='filename', help='file containing your source code')
parser.add_argument('-o', '--output', metavar='filename', nargs='?', const='./output.asm',
  help='file to write MIPS assembly code to')
parser.add_argument('-c', '--comments', metavar='level', nargs='?', type=int, const=1,
  help='0=none, 1=minimal, 2=all (default: 1)')
parser.add_argument('-r', '--registers', metavar='register', nargs='+',
  help='available temporary registers (in order). avoid using these in your code \
  as they may get overridden (default: \'$t0\' \'$t1\' \'$t2\')')

args = parser.parse_args()

COMPILE_HEADER = """# This file was generated using the MIPS++ programming language
# and compiler: https://github.com/alexsocha/mipsplusplus

"""

try:
  openFileIn = open(args.input, 'r')
  fileLines = openFileIn.readlines()
  openFileIn.close()

  compileArgs = {}
  if args.comments is not None: compileArgs['comments'] = args.comments
  if args.registers is not None: compileArgs['registers'] = args.registers

  compiled = mipsplusplus.compile(fileLines, **compileArgs)

  fileOut = args.output if args.output is not None \
    else os.path.splitext(args.input)[0] + '.asm'
  openFileOut = open(fileOut, 'w')
  openFileOut.write(COMPILE_HEADER + os.linesep.join(compiled))
  openFileOut.close()

except mipsplusplus.utils.CompileException as e:
  print(e)
except Exception as e:
  print('COMPILATION FAILED')
  raise e
