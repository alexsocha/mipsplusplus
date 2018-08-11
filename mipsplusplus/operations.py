from mipsplusplus import utils
from mipsplusplus import general

UN_OPERATORS = {'not': 'not', 'neg': 'neg'}
BIN_OPERATORS = {
  '+': 'add', '-': 'sub', '*': 'mult', '/': 'div',
  '%': 'div', '<<': 'sll', '>>': 'srl', '>>>': 'sra', '<': 'slt',
  'and': 'and', 'or': 'or', 'xor': 'xor', 'nor': 'nor'
}
BIN_OPERATORS_IMM = {
  '+': 'addi', '<': 'slti',
  '<<': 'sll', '>>': 'srl', '>>>': 'sra',
  'and': 'andi', 'or': 'ori', 'xor': 'xori', 'nor': 'nor'
}
BIN_RESULT_REGS = {'*': '$lo', '/': '$lo', '%': '$hi'}
COND_OPERATORS = ['and', 'or', 'xor', 'nor']

def binaryOperation(operation, reg1, reg2, outputReg, props):
  resultLines = []
  standardComment = utils.formatComment('{} = {} {} {}'.format(outputReg, reg1, operation, reg2), props, 2)
  operationComment = utils.formatComment('{} {} {}'.format(reg1, '/' if operation == '%' else operation, reg2), props, 2)

  if reg1 == '0': reg1 = '$0'
  if reg2 == '0': reg2 = '$0'
  reg1 = utils.getRegister(reg1)
  reg2 = utils.getRegister(reg2)

  didChangeReg1 = False
  if (not operation in BIN_OPERATORS_IMM and utils.isIntOrChar(reg1)) or (utils.isIntOrChar(reg1) and utils.isIntOrChar(reg2)):
    tempReg = utils.getTempRegister(props['tempRegisters'], 0)
    resultLines.append(general.loadIntOrChar(reg1, tempReg, props))
    reg1 = tempReg
    didChangeReg1 = True
  if not operation in BIN_OPERATORS_IMM and utils.isIntOrChar(reg2):
    tempReg = utils.getTempRegister(props['tempRegisters'], 1 if didChangeReg1 else 0)
    resultLines.append(general.loadIntOrChar(reg2, tempReg, props))
    reg2 = tempReg

  # Using 2 registers
  if utils.isRegister(reg1) and utils.isRegister(reg2):
    if operation in BIN_RESULT_REGS:
      # Move from hi/lo
      resultLines.append('{} {}, {}{}'.format(BIN_OPERATORS[operation], reg1, reg2, operationComment))
      resultLines.append(general.loadRegHiLo(BIN_RESULT_REGS[operation], outputReg, {**props, 'comment': standardComment}))
    else:
      resultLines.append('{} {}, {}, {}{}'.format(BIN_OPERATORS[operation], utils.getRegister(outputReg), reg1, reg2, standardComment))
  else:
    # Immediate
    regNum, number = (reg1, utils.getIntOrChar(reg2)) if utils.isRegister(reg1) else (reg2, utils.getIntOrChar(reg1))
    resultLines.append('{} {}, {}, {}{}'.format(BIN_OPERATORS_IMM[operation], utils.getRegister(outputReg), regNum, number, standardComment))

  return { 'lines': resultLines, 'reg': outputReg }

def unaryOperation(operation, reg1, outputReg, props):
  resultLines = []

  if utils.isIntOrChar(reg1):
    tempReg = utils.getTempRegister(props['tempRegisters'], 0)
    resultLines.append(general.loadIntOrChar(reg1, tempReg, props))
    reg1 = tempReg

  comment = utils.formatComment('{} = {} {}'.format(outputReg, operation, reg1), props, 2)
  resultLines.append('{} {}, {}{}'.format(UN_OPERATORS[operation], utils.getRegister(outputReg), utils.getRegister(reg1), comment))
  return { 'lines': resultLines, 'reg': outputReg }
