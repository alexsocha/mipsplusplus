import os
from mipsplusplus import utils

NUM_TYPES = ['int', 'short', 'byte', 'char', 'number']
ADDRESS_TYPES = ['int[]', 'short[]', 'byte[]', 'char[]', 'string']
ADDRESS_ELEMENT_TYPE_MAP = {'int[]': 'int', 'short[]': 'short', 'byte[]': 'byte', 'char[]': 'char', 'string': 'char', 'address': 'any'}
NUM_SIZES = {'int': 4, 'short': 2, 'byte': 1, 'char': 1}

def isDefinition(line):
  for v in NUM_TYPES + ADDRESS_TYPES:
    if line.startswith(v + ' ') or line.replace(' ', '').startswith(v + '['): return True
  return False

def getSupertype(t):
  return 'number' if t in NUM_TYPES else 'address' if t in ADDRESS_TYPES else t

def parseDefinition(line, props):
  newLine = ''
  newVariable = {}
  

  varDefinition, varValue = '', None
  if '=' in line: varDefinition, varValue = [s.strip() for s in line.split('=')]
  else: varDefinition = line.strip()
  varType, varName = varDefinition.split()
  
  comment = utils.formatComment(varDefinition, props)

  # Numberic
  numTypeMap = { 'int': 'word', 'short': 'half', 'byte': 'byte', 'char': 'byte' }
  for numType in NUM_TYPES:
    if varValue == None: varValue = '0'
    if varType == numType:
      parsedValue = utils.getIntOrChar(varValue)
      newLine = '{}: .{} {}{}'.format(varName, numTypeMap[numType], parsedValue, comment)
      newVariable = { 'name': varName, 'type': varType, 'supertype': getSupertype(varType), 'init': varValue }

  # Array or string or address
  if varType in ADDRESS_TYPES or '[' in varType:
    initSize = 0
    if '[' in varType:
      initSizeStr = varType[varType.index('[')+1:varType.index(']')]
      initSize = utils.getIntOrChar(initSizeStr) if utils.isInt(initSizeStr) else 0
      varType = varType[:varType.index('[')].strip() + '[]'
    elemType = ADDRESS_ELEMENT_TYPE_MAP[varType]

    if varValue[0] == '\'' and varValue[-1] == '\'': varValue = '"' + varValue[1:-1] + '"'
    if varValue.startswith('"'):
      newLine = '{}: .asciiz {}{}'.format(varName, varValue, comment)
    elif varValue.startswith('['):
      newLine = '{}: .{} {}{}'.format(varName, numTypeMap[elemType], varValue[1:-1].strip(), comment)
    else:
      numBytes = NUM_SIZES[elemType]
      newLine = '{}: .space {}{}'.format(varName, initSize, comment)
      if numBytes != 1: newLine = '.align {}{}{}'.format(numBytes-1, os.linesep, newLine)

    newVariable = { 'name': varName, 'type': varType, 'supertype': 'address', 'elemtype': ADDRESS_ELEMENT_TYPE_MAP[varType], 'init': varValue, 'initsize': initSize }

  if props['comment'] is not None: newLine += props['comment']
  return (newLine, newVariable)

def mergeType(type1, type2):
  if type1 == type2: return type1
  if type1 == 'any' and type2 != 'any': return type2
  if type2 == 'any' and type1 != 'any': return type1

  if type1 == 'number' and type2 in NUM_TYPES: return type2
  if type2 == 'number' and type1 in NUM_TYPES: return type1

  if type1 == 'address' and type2 in ADDRESS_TYPES: return type2
  if type2 == 'address' and type1 in ADDRESS_TYPES: return type1

  if getSupertype(type1) == 'address' and getSupertype(type2) == 'number': return type1
  if getSupertype(type2) == 'address' and getSupertype(type1) == 'number': return type2

  if type1 in ADDRESS_TYPES and type2 in ADDRESS_TYPES: return 'address'
  if type1 in NUM_TYPES and type2 in NUM_TYPES: return type1 if NUM_SIZES[type1] >= NUM_SIZES[type2] else type2 
  return type1

def updateType(old, new):
  if new == 'any' and old != 'any': return old
  if new == getSupertype(old): return old
  return new
