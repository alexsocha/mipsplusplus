from mipsplusplus import utils
from mipsplusplus import general
from mipsplusplus import definitions
from mipsplusplus import expressions
from mipsplusplus import addresses
from mipsplusplus import operations
from mipsplusplus import parser

def parseAssignment(line, props):
  resultLines = []
  lhs, rhs = [s.strip() for s in line.split('=')]

  if utils.isRegister(lhs):
    reg = lhs.split(' as ')[0].strip() if ' as ' in lhs else lhs
    parsedRHS = expressions.parseRHS(rhs, props, reg)
    resultLines += parsedRHS['lines']
  else:
    inferredType = expressions.parseLHS(lhs, props)['type']
    parsedRHS = expressions.parseRHS(rhs, props, 'any', inferredType)
    resultLines += parsedRHS['lines']
    resultType = parsedRHS['type']
    limitedProps = utils.propsWithTempRegExcl(props, [parsedRHS['reg']])

    parsedLHS = expressions.parseLHS(lhs, limitedProps)
    resultLines += parsedLHS['lines']

    resultType = definitions.updateType(resultType, parsedLHS['elemtype'])
    resultLines.append(general.storeToAddress(parsedLHS['address'], resultType, parsedRHS['reg'], props))
  
  lastLine = resultLines[-1]
  if '#' in lastLine:
    lastLine = lastLine[:lastLine.index('#')].strip()
  resultLines[-1] = lastLine + utils.formatComment(line, props)
  return resultLines

def parsePrint(line, props):
  parsedExpr = expressions.parseRHS(line[line.index(' '):].strip(), props, '$a0')
  printOperations = { 'number': 1, 'address': 4, 'char': 11 }
  resultType = 'char' if parsedExpr['type'] == 'char' else definitions.getSupertype(parsedExpr['type'])
  if resultType == 'any': resultType = 'number'
  printOperation = printOperations[resultType if resultType in printOperations else 'number']

  return parsedExpr['lines'] + [
    general.setMode(printOperation, props),
    'syscall{}'.format(utils.formatComment(line, props))
  ]

def parseSysFunc(expr, props, isInExpression=False):
  comment = utils.formatComment(None if isInExpression else expr, props)
  if expr.startswith(utils.SYS_FUNCTIONS[0]):
    return [
    general.setMode(5, props),
    'syscall{}'.format(comment)
  ]
  elif expr.startswith(utils.SYS_FUNCTIONS[1]):
    params = expr[expr.index('(')+1:-1].strip()
    parsedSize = expressions.parseRHS(params, props, '$a0')
    return parsedSize['lines'] + [
    general.setMode(9, props),
    'syscall{}'.format(comment)
  ]

def parseInputStr(line, props):
  resultLines = []
  argumentStr = line[len(line.split()[0]):]
  arguments = [s.strip() for s in argumentStr.split(',')]
  parsedAddr = expressions.parseRHS(arguments[0], props, '$a0', 'address')
  resultLines += parsedAddr['lines']
  
  masSize = '20'
  if len(arguments) > 1: masSize = arguments[1]
  parsedSize = expressions.parseRHS(masSize, props, '$a1', 'number')
  resultLines += parsedSize['lines']

  return resultLines + [
    general.setMode(8, props),
    'syscall{}'.format(utils.formatComment(line, props))
  ]

def parseExit(line, props):
  return [
    general.setMode(10, props),
    'syscall{}'.format(utils.formatComment('exit', props))
  ]

def parseGoto(line, props, link=False):
  location = line[len('goto'):].strip()
  parsedExpr = expressions.parseRHS(location, props, 'any', 'address')
  locationReg = parsedExpr['reg']
  newComment = utils.formatComment(line, props)

  gotoInstructions = ['jal', 'jalr'] if link else ['j', 'jr'] 
  if parsedExpr['address'] != None: return '{} {}{}'.format(gotoInstructions[0], parsedExpr['address'], newComment)
  else: return parsedExpr['lines'] + ['{} {}{}'.format(gotoInstructions[1], locationReg, newComment)]

def parseGotoConditional(line, props):
  resultLines = []
  gotoFunc = line.split()[0]

  branchOperators = ['==', '!=', '<', '<=', '>', '>=']
  branchFuncs = {'==': 'beq', '!=': 'bne', '<': 'blt', '<=': 'ble', '>': 'bgt', '>=': 'bge'}
  branchFuncsWith0 = {'<': 'bltz', '<=': 'blez', '>': 'bgtz', '>=': 'bgez'}
  branchFuncsWith0Link = {'<': 'bltzal', '>=': 'bgezal'}

  condition = line.split(' if ')[1].strip()
  location = line.split(' if ')[0][len(gotoFunc):].strip()

  address = expressions.parseRHS(location, props, 'any', 'address')['address']
  if address == None: raise utils.CompileException('Direct label is required')
  
  conditionLeft, conditionRight, conditionOperator = '', '', None
  
  splitCondition = parser.splitExpression(condition)
  rpnCondition = parser.infixToPostfix(splitCondition)
  if rpnCondition[-1] not in branchOperators:
    conditionLeft = '({})'.format(condition)
    conditionRight = '0'
    conditionOperator = '>'
  else:
    splitIdxCondition = [(item, idx) for idx, item in enumerate(splitCondition)]
    rpnIdxCondition = parser.infixToPostfix(splitIdxCondition, lambda item: item[0])
    conditionOperator = rpnIdxCondition[-1][0]
    operatorIdx = rpnIdxCondition[-1][1]
    conditionLeft = ' '.join(splitCondition[:operatorIdx])
    conditionRight = ' '.join(splitCondition[operatorIdx+1:])

  branchFunc = branchFuncs[conditionOperator]
  singleParam = False
  
  reg1, reg2 = 'any', 'any'
  if utils.isRegister(conditionLeft):
    reg1 = utils.getRegister(conditionLeft)
  else:
    parsed = expressions.parseRHS(conditionLeft, props, 'any', 'number')
    resultLines += parsed['lines']
    reg1 = parsed['reg']

  limitedProps = utils.propsWithTempRegExcl(props, [reg1])

  if gotoFunc == 'gotolink':
    if conditionRight == '0' and conditionOperator in branchFuncsWith0Link:
      branchFunc = branchFuncsWith0Link[conditionOperator]
      singleParam = True
    else:
      raise utils.CompileException('Conditional gotolink only supports < 0 and >= 0 conditions')
  elif conditionRight == '0' and conditionOperator in branchFuncsWith0:
    branchFunc = branchFuncsWith0[conditionOperator]
    singleParam = True
  elif utils.isRegister(conditionRight):
    reg2 = utils.getRegister(conditionRight)
  else:
    parsed = expressions.parseRHS(conditionRight, limitedProps, 'any', 'number')
    resultLines += parsed['lines']
    reg2 = parsed['reg']
  
  comment = utils.formatComment(line, props)
  if singleParam: resultLines.append('{} {}, {}{}'.format(branchFunc, reg1, address, comment))
  else: resultLines.append('{} {}, {}, {}{}'.format(branchFunc, reg1, reg2, address, comment))
  return resultLines
