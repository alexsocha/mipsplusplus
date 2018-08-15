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
      comment = None
      indentation = line[0:len(line) - len(line.lstrip())]
      newLine = None
      rawLine = None

      if utils.hasLabel(line):
        label = line[:line.index(':')+1].lstrip()
        line = line[line.index(':')+1:]
        newLine = line
      else: newLine = line.strip()
      
      if '#' in line:
        comment = utils.getComment(line)
        rawLine = line[:line.index('#')].strip()
      else: rawLine = line.strip()

      props = {'variables': variables, 'comment': comment, 'commentLevel': comments, 'tempRegisters': registers}

      if definitions.isDefinition(rawLine):
        newLine, newVar = definitions.parseDefinition(rawLine, props)
        variables[newVar['name']] = newVar
      elif rawLine.startswith('@alias'): newLine = utils.parseAliasLine(rawLine, props)
      elif rawLine.startswith('print '): newLine = functions.parsePrint(rawLine, props)
      elif rawLine.startswith('inputstr '): newLine = functions.parseInputStr(rawLine, props)

      elif (rawLine.startswith('goto ') or rawLine.startswith('gotolink ')) and ' if ' in rawLine:
        newLine = functions.parseGotoConditional(rawLine, props)
      elif rawLine.startswith('goto '): newLine = functions.parseGoto(rawLine, props)
      elif rawLine.startswith('gotolink '): newLine = functions.parseGoto(rawLine, props, True)
      elif rawLine.startswith('exit'): newLine = functions.parseExit(rawLine, props)
      elif '=' in rawLine: newLine = functions.parseAssignment(rawLine, props)

      newLines.append(utils.addIndentation(newLine, indentation, label))
    
    except utils.CompileException as e:
      raise utils.CompileException(e.message, idx+1, originalLine)
    except Exception as e:
      raise utils.CompileException('Unknown error', idx+1, originalLine)

  return utils.formatOutput(newLines)
