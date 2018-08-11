import os
from mipsplusplus import utils
from mipsplusplus import definitions
from mipsplusplus import functions
from mipsplusplus import general
from mipsplusplus import expressions
from mipsplusplus import parser

def compile(lines, comments=1, registers=['$t0', '$t1', '$t2']):
  if not isinstance(lines, list): lines = lines.split(os.linesep)
  lines = [l.rstrip() for l in lines]
  newLines = []
  variables = {}
  for idx, line in enumerate(lines):
    originalLine = line
    try:
      label = ''
      if ':' in line and line.split(':')[0].isalnum():
        splitLine = line.split(':')
        label = splitLine[0] + ':' + splitLine[1][0:len(splitLine[1]) - len(splitLine[1].lstrip())]
        line = splitLine[1]
      else: indentation = line[0:len(line) - len(line.lstrip())]
      line = newLine = line.strip()
      comment = None
      if '#' in line:
        comment = utils.getComment(line)
        line = line[:line.index('#')].rstrip()
      
      props = {'variables': variables, 'comment': comment, 'commentLevel': comments, 'tempRegisters': registers}

      if definitions.isDefinition(line):
        newLine, newVar = definitions.parseDefinition(line, props)
        variables[newVar['name']] = newVar
      elif line.startswith('@alias'): newLine = utils.parseAliasLine(line, props)
      elif line.startswith('print '): newLine = functions.parsePrint(line, props)
      elif line.startswith('inputstr '): newLine = functions.parseInputStr(line, props)

      elif (line.startswith('goto ') or line.startswith('gotolink ')) and ' if ' in line:
        newLine = functions.parseGotoConditional(line, props)
      elif line.startswith('goto '): newLine = functions.parseGoto(line, props)
      elif line.startswith('gotolink '): newLine = functions.parseGoto(line, props, True)
      elif line.startswith('exit'): newLine = functions.parseExit(line, props)
      elif '=' in line: newLine = functions.parseAssignment(line, props)

      newLines.append(utils.addIndentation(newLine, indentation, label))

    except utils.CompileException as e:
      raise utils.CompileException(e.message, idx+1, originalLine)
  
  return utils.formatOutput(newLines)
