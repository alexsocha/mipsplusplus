from mipsplusplus import utils
from mipsplusplus import functions
from mipsplusplus import definitions
from mipsplusplus import general
from mipsplusplus import operations
from mipsplusplus import addresses
from mipsplusplus import parser

def parseRHS(expression, props, outputReg='any', inferredType='any'):
  # Convert the expression to postfix (RPN) notation
  splitExp = parser.infixToPostfix(parser.splitExpression(expression))

  allTempRegs = props['tempRegisters']
  resultLines = []
  resultAddr = None

  # Parse the expression as a stack of operations
  equationStack = []
  typeStack = []
  asAddressStack = []
  availableTempRegIdx = 0
  for i, item in enumerate(splitExp):
    val1, val2 = item, None
    val1Type, val2Type = inferredType, inferredType
    val1AsAddress, val2AsAddress = False, False
    val1Addr, val2Addr = None, None # Havn't optimized address addition yet
    reg1, reg2 = None, None
    limitedProps = utils.propsWithTempRegOffset(props, availableTempRegIdx)
    
    finalIteration = i == len(splitExp) - 1 or (i == len(splitExp) - 3 and (splitExp[-1] == 'as' or splitExp[-1] == 'addressof'))
    targetReg = utils.getTempRegister(limitedProps['tempRegisters'], 0)
    if finalIteration:
      if utils.isSysFunc(item) and outputReg == 'any': targetReg = '$v0'
      elif outputReg == 'any': targetReg = utils.getTempRegister(allTempRegs, 0)
      else: targetReg = outputReg

    prevTempReg = None if availableTempRegIdx < 1 else utils.getTempRegister(allTempRegs, availableTempRegIdx - 1)
    prevPrevTempReg = None if availableTempRegIdx < 2 else utils.getTempRegister(allTempRegs, availableTempRegIdx - 2)
    
    if item in operations.BIN_OPERATORS or item == 'as':
      val1, val2 = equationStack[-2], equationStack[-1]
      val1Type, val2Type = typeStack[-2], typeStack[-1]
      val1AsAddress, val2AsAddress = asAddressStack[-2], asAddressStack[-1]
    elif item in operations.UN_OPERATORS or item == 'addressof':
      val1, val1Type, val1AsAddress = equationStack[-1], typeStack[-1], asAddressStack[-1]
    
    # Special operators
    if item == 'as':
      equationStack.pop()
      asAddressStack.pop()
      typeStack.pop(); typeStack.pop()
      typeStack.append(val2)
      val1, val1Type, val1AsAddress = equationStack[-1], typeStack[-1], asAddressStack[-1]
    elif item == 'addressof':
      asAddressStack.pop()
      asAddressStack.append(True)
      val1, val1Type, val1AsAddress = equationStack[-1], typeStack[-1], asAddressStack[-1]
    else:
      # Get first register
      if item in operations.BIN_OPERATORS or item in operations.UN_OPERATORS:
        if utils.isIntOrChar(val1): reg1 = val1
        else:
          if utils.isRegister(val1): reg1 = val1
          else: reg1 = targetReg
          parsed = parseSingleRHS(val1, limitedProps, reg1, val1Type, val1AsAddress)
          resultLines += parsed['lines']
          val1Type, val1Addr = parsed['type'], parsed['address']
          if not utils.isRegister(val1): limitedProps = utils.propsWithTempRegOffset(limitedProps, 1)

      # Get Second register
      if item in operations.BIN_OPERATORS:
        if utils.isIntOrChar(val2): reg2 = val2
        else:
          if utils.isRegister(val2): reg2 = val2
          elif reg1 == targetReg: reg2 = utils.getTempRegister(limitedProps['tempRegisters'], 0)
          else: reg2 = targetReg
          parsed = parseSingleRHS(val2, limitedProps, reg2, val2Type, val2AsAddress)
          resultLines += parsed['lines']
          val2Type, val2Addr = parsed['type'], parsed['address']
          if not utils.isRegister(val2): limitedProps = utils.propsWithTempRegOffset(limitedProps, 1)

    # Do binary operation
    if item in operations.BIN_OPERATORS:
      # Try to re-use/free-up temporary registers where possible
      equationReg = targetReg
      if utils.isTempRegister(equationReg, allTempRegs):
        if val1 == prevPrevTempReg: equationReg = val1
        elif val2 == prevTempReg: equationReg = val2
        else: availableTempRegIdx += 1
        if val1 == prevPrevTempReg and val2 == prevTempReg:
          # Suggested Optimization: Even though it frees up a register, it doesn't
          # keep track of the value inside it. This could potentially prevent
          # the same value from being re-loaded.
          availableTempRegIdx -= 1
      
      # Parse the operation
      parsedOperation = operations.binaryOperation(item, reg1, reg2, equationReg, limitedProps)
      resultLines += parsedOperation['lines']
      equationStack.pop(); equationStack.pop(); typeStack.pop(); typeStack.pop(); asAddressStack.pop(); asAddressStack.pop()
      equationStack.append(parsedOperation['reg'])
      typeStack.append(definitions.mergeType(val1Type, val2Type))
      asAddressStack.append(False)

    # Do unary operation
    elif item in operations.UN_OPERATORS:
      # Try to re-use/free-up temporary registers where possible
      equationReg = targetReg
      if utils.isTempRegister(equationReg, allTempRegs):
        if val1 == prevTempReg: equationReg = val1
        else: availableTempRegIdx += 1
      
      # Parse the operation
      parsedOperation = operations.unaryOperation(item, reg1, equationReg, limitedProps)
      resultLines += parsedOperation['lines']
      equationStack.pop(); typeStack.pop(); asAddressStack.pop()
      equationStack.append(parsedOperation['reg'])
      typeStack.append(val1Type)
      asAddressStack.append(False)
    
    # Handle expressions without operators
    elif i == len(splitExp) - 1:
      if outputReg == 'any':
        if val1 == '0': val1 = '$0'
        if utils.isRegister(val1): targetReg = utils.getRegister(val1)
      parsed = parseSingleRHS(val1, limitedProps, targetReg, val1Type, val1AsAddress)
      resultLines += parsed['lines']
      val1Type, val1Addr = parsed['type'], parsed['address']
      resultAddr = val1Addr
      equationStack.append(targetReg)
      typeStack.append(val1Type)
      asAddressStack.append(False)

    # Add to stack
    elif item != 'as' and item != 'of':
      equationStack.append(item)
      if utils.isInt(item): typeStack.append('number')
      elif utils.isChar(item): typeStack.append('char')
      else: typeStack.append('any')
      asAddressStack.append(False)

  return { 'lines': resultLines, 'type': typeStack[-1], 'reg': equationStack[-1], 'address': resultAddr }

def parseSingleRHS(expression, props, outputReg, inferredType='any', loadAsAddress=False):
  resultLines = []
  resultAddr = None
  resultType = inferredType

  if loadAsAddress and (utils.isRegister(expression) or utils.isSysFunc(expression)):
    raise utils.CompileException('Can\'t get address of register')

  # System functions
  if utils.isSysFunc(expression):
    resultLines += functions.parseSysFunc(expression, props, True)
    resultType = definitions.updateType(resultType, 'number')
    if outputReg != '$v0': resultLines.append(general.loadRegister('$v0', outputReg, props))

  # Array
  elif addresses.isArray(expression):
    parsedAddr = addresses.parseArray(expression, props, outputReg)
    outerInner = (parsedAddr['outer'], parsedAddr['inner'])
    resultLines += parsedAddr['lines']

    if loadAsAddress:
      resultType = definitions.updateType('address', resultType)
      if parsedAddr['reg'] != outputReg:
        resultLines.append(general.loadAsAddress(parsedAddr['address'], outputReg, props, outerInner))
      if parsedAddr['reg'] == None: resultAddr = parsedAddr['address']
    else:
      loadType = definitions.updateType(resultType, parsedAddr['elemtype'])
      resultLines.append(general.loadFromAddress(parsedAddr['address'], loadType, outputReg, props, outerInner))
      resultType = definitions.updateType(loadType, resultType)

  # Register
  elif utils.isRegister(expression):
    if general.isRegHiLo(expression):
      resultLines.append(general.loadRegHiLo(expression, outputReg, props))
    elif expression != outputReg:
      resultLines.append(general.loadRegister(expression, outputReg, props))

  # Variable
  elif expression in props['variables']:
    varName, varType = props['variables'][expression]['name'], props['variables'][expression]['type']
    if definitions.getSupertype(varType) == 'address' or loadAsAddress:
      resultLines.append(general.loadAsAddress(varName, outputReg, props))
      resultType = definitions.updateType(varType, resultType)
      resultAddr = varName
    else:
      resultLines.append(general.loadFromAddress(varName, varType, outputReg, props))
      resultType = definitions.updateType(varType, resultType)

  # Integer or char literal
  elif utils.isIntOrChar(expression):
    resultType = definitions.updateType(resultType, 'char' if utils.isChar(expression) else 'number')
    resultLines.append(general.loadIntOrChar(expression, outputReg, props))

  # Address
  elif addresses.isAddress(expression, props):
    resultType = definitions.updateType('address', resultType)
    if definitions.getSupertype(resultType) == 'address':
      resultLines.append(general.loadAsAddress(expression, outputReg, props))
    else: resultLines.append(general.loadFromAddress(expression, resultType, outputReg, props))
    resultAddr = expression

  return { 'lines': resultLines, 'type': resultType, 'reg': outputReg, 'address': resultAddr }

def parseLHS(expression, props, addressReg='any'):
  resultType = 'address'
  elemType = 'any'
  if ' as ' in expression: expression, elemType = [s.strip() for s in expression.split(' as ')]

  if addresses.isArray(expression):
    parsedAddr = addresses.parseArray(expression, props, addressReg)
    return {**parsedAddr, 'elemtype': definitions.updateType(elemType, parsedAddr['elemtype'])}
  
  elif expression in props['variables']:
    if props['variables'][expression]['supertype'] == 'address':
      resultType = props['variables'][expression]['type']
      elemType = props['variables'][expression]['elemtype']
    else:
      elemType = props['variables'][expression]['type']

  return { 'lines': [], 'type': resultType, 'elemtype': elemType, 'reg': None, 'address': expression }
