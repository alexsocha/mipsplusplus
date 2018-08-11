import sys
import os
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FILE_DIR)
RUN_DIR = FILE_DIR + '/_run'
sys.path.append(BASE_DIR)
import mipsplusplus

class TColors:
  GREEN = '\033[92m'
  RED = '\033[91m'
  END = '\033[0m'

def runOutputFile(expectedOutput):
  pass # Not yet implemented

def compileOutputFile(sourceFile):
  try:
    expectedOutput = None
    openFileIn = open(sourceFile, 'r')
    compiled = mipsplusplus.compile(openFileIn.readlines())
    openFileIn.close()

    openFileOut = open(RUN_DIR + '/output.asm', 'w')
    openFileOut.write(os.linesep.join(compiled))
    openFileOut.close()

    print('{}Compiled Successfully: {}{}'.format(TColors.GREEN, os.path.basename(sourceFile), TColors.END))
    return expectedOutput

  except Exception as e:
    print('{}Failed to Compile: {}{}'.format(TColors.RED, os.path.basename(sourceFile), TColors.END))
    if isinstance(e, mipsplusplus.utils.CompileException):
      sys.exit(e)
    else: raise e

def initTests():
  if not os.path.exists(RUN_DIR):
    os.makedirs(RUN_DIR)

def testAllInDirectory(directory):
  fullDir = '{}/{}'.format(BASE_DIR, directory)
  for file in os.listdir(fullDir):
      if file.endswith('.mpp'):
          expectedOutput = compileOutputFile(os.path.join(fullDir, file))
          if expectedOutput is not None: runOutputFile(expectedOutput) 
     
initTests() 
testAllInDirectory('examples')
