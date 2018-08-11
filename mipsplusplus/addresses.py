from mipsplusplus import utils
from mipsplusplus import general
from mipsplusplus import expressions
from mipsplusplus import operations
from mipsplusplus import definitions

def isAddress(expression, props):
  if expression in props['variables']:
    return props['variables'][expression]['supertype'] == 'address'
  return expression.isalnum() # Detect labels as addresses

def isArray(expression):
  return expression.endswith(']')

def parseArray(expression, props, addressReg='any'):
  resultLines = []
  resultReg = None
  resultType = 'address'
  elemType = 'any'
  resultAddress = 'none'
  outer, inner = None, None

  outerAddr = expression[:expression.index('[')]
  innerExpr = expression[expression.index('[')+1:-1].strip()

  if outerAddr in props['variables'] and 'elemtype' in props['variables'][outerAddr]:
    resultType = definitions.updateType(props['variables'][outerAddr]['type'], 'address')
    if 'elemtype' in props['variables'][outerAddr]:
      elemType = props['variables'][outerAddr]['elemtype']

  # Optimize offset literals
  if utils.isIntOrChar(innerExpr):
    value = utils.getIntOrChar(innerExpr)
    if utils.isRegister(outerAddr):
      if value == 0: resultAddress = '({})'.format(utils.getRegister(outerAddr))
      else: resultAddress = '{}({})'.format(value, utils.getRegister(outerAddr))
    else:
      if value == 0: resultAddress = outerAddr
      else: resultAddress = '{}+{}'.format(outerAddr, value)
    outer, inner = outerAddr, value
  else:
    # Parse inner expression
    exprReg = None
    if utils.isRegister(innerExpr): exprReg = innerExpr
    else:
      parsedExpr = expressions.parseRHS(innerExpr, props, 'any', 'number')
      resultLines += parsedExpr['lines']
      exprReg = parsedExpr['reg']

    limitedProps = utils.propsWithTempRegExcl(props, [exprReg])
    resultReg = addressReg
    if resultReg is 'any' or resultReg == exprReg:
      resultReg = utils.getTempRegister(limitedProps['tempRegisters'], 0)
   
    newAddress = outerAddr
    if utils.isRegister(outerAddr):
      newAddress = '({})'.format(utils.getRegister(outerAddr))
    resultLines.append(general.loadAsAddress(newAddress, resultReg, props, (outerAddr, '0')))
    addOperation = operations.binaryOperation('+', resultReg, exprReg, resultReg, limitedProps)

    resultLines += addOperation['lines']
    resultAddress = '({})'.format(utils.getRegister(resultReg))
    outer, inner = resultReg, '0'

  return { 'lines': resultLines, 'type': resultType, 'elemtype': elemType, 'reg': resultReg, 'address': resultAddress, 'outer': outer, 'inner': inner}
