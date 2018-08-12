SYS_FUNCTIONS = ['input', 'alloc']
REG_ALIASES = {'$_division': '$lo', '$_remainder': '$hi'}
class CompileException(Exception):
  def __init__(self, message, lineNumber=None, line=None):
    self.message = message
    self.lineNumber = lineNumber
    self.line = line

  def __str__(self):
    return 'Compile Error (line {}):\n\n  {}\n\n{}' \
      .format(self.lineNumber, self.line, self.message)

def addRegAlias(reg, alias):
  REG_ALIASES[reg] = alias

def getRegister(reg):
  return REG_ALIASES[reg] if reg in REG_ALIASES else reg

def isSysFunc(value):
  for func in SYS_FUNCTIONS:
    if value.startswith(func + '('): return True
  return False

def getVariable(varName, variables):
  if not varName in variables: raise CompileException("'{}' is not a variable".format(varName))
  return variables[varName]

def getTempRegister(registers, index):
  if index >= len(registers): raise CompileException('Not enough temporary registers available')
  return registers[index]

def propsWithTempRegOffset(props, index):
  return { **props, 'tempRegisters': props['tempRegisters'][index:] }

def propsWithTempRegExcl(props, exclRegs):
  return { **props, 'tempRegisters': [t for t in props['tempRegisters'] if not t in exclRegs] }

def isInt(value):
  try:
    int(value)
    return True
  except ValueError: return False
def isChar(value):
  return (value.startswith('\'') and value.endswith('\'')) or (value.startswith('"') and value.endswith('"'))

def isRegister(value):
  if value == '': return False
  if not (value.replace(' ', '')[1:]).isalnum(): return False
  return value.startswith('$')
def isTempRegister(value, tempRegisters=None):
  if isRegister(value) and value.startswith('$t'):
    if tempRegisters is None: return True
    return value in tempRegisters
  return False

def charToByte(c):
  try:
    return ord(c[1:-1].replace('\\n', '\n'))
  except Exception:
    raise CompileException('Invalid char: ' + c)

def isIntOrChar(value):
  return isInt(value) or isChar(value)

def getIntOrChar(value):
  return charToByte(value) if isChar(value) else int(value)

def getComment(line):
  firstPart = line.split('#')[0]
  return line[len(firstPart.rstrip()):]

def addIndentation(line, indentation, label):
  if isinstance(line, list):
    if label != '': return [label] + [addIndentation(l, indentation + '  ', '') for l in line]
    else: return [addIndentation(l, indentation, '') for l in line]
  return label + indentation + line

def formatComment(comment, props, commentLevel=1):
  if props['comment'] != None: return props['comment']
  elif comment is None: return ''
  elif commentLevel <= props['commentLevel']:
    return ' # {}'.format(comment)
  else: return ''

def parseAliasLine(line, props):
  splitLine = [s.strip() for s in line[len('@alias'):].split(',')]
  
  comment = ''
  for idx, expr in enumerate(splitLine):
    alias, reg = [s.strip() for s in expr.split('=')]
    REG_ALIASES[alias] = reg
    if idx == 0: comment += 'let '
    comment += '{} = {}'.format(alias, reg)
    if idx < len(splitLine)-1: comment += ', '

  comment = formatComment(comment, props).strip()
  return comment
  
def formatOutput(lines):
  def shouldSeparateLine(line):
    if isinstance(line, list): return True
    if line.strip().startswith('.'): return False
    return not (line.strip().startswith('#') or line.strip() == '')

  def formatLines(innerLines):
    result = []
    for i, line in enumerate(innerLines):
      if isinstance(line, list):
        if len(line) == 1:
          result.append(line[0])
        else:
          if i > 0 and not isinstance(lines[i-1], list) and shouldSeparateLine(lines[i-1]):
            if not lines[i-1].endswith(':'): result.append('')

          result += formatLines(line)
          if i < len(lines) - 1 and shouldSeparateLine(lines[i+1]):
            result.append('')
      else:
        result.append(line)
    return result
  return formatLines(lines)
