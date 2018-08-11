from mipsplusplus import utils
from mipsplusplus import definitions

def setMode(mode, props):
  modes = {1: 'print integer', 4: 'print string', 5: 'input integer', 8: 'input string',
    9: 'allocate memory', 10: 'exit', 11: 'print character'}
  comment = utils.formatComment("set mode to '{}'".format(modes[mode]), props, 2)
  return 'addi $v0, $0, {}{}'.format(mode, comment)

def storeToAddress(address, storeType, outputReg, props):
  if utils.isRegister(address): raise utils.CompileException('Can\'t store to register')
  numStoreFuncs = {'int': 'sw', 'short': 'sh', 'byte': 'sb', 'char': 'sb', 'number': 'sb'}
  storeFunc = 'sb'
  if storeType in definitions.NUM_TYPES: storeFunc = numStoreFuncs[storeType]
  
  comment = utils.formatComment('{} = {}'.format(address, outputReg), props, 2)
  return '{} {}, {}{}'.format(storeFunc, utils.getRegister(outputReg), address, comment)

def loadAsAddress(address, outputReg, props, outerInner = None):
  if utils.isRegister(address): raise utils.CompileException('Can\'t load register as address')

  if outerInner == None: comment = utils.formatComment('{} = address of {}'.format(outputReg, address), props, 2)
  else: comment = utils.formatComment('{} = address of {}[{}]'.format(outputReg, outerInner[0], outerInner[1]), props, 2)

  return '{} {}, {}{}'.format('la', utils.getRegister(outputReg), address, comment)

def loadFromAddress(address, loadType, outputReg, props, outerInner = None):
  numLoadFuncs = {'int': 'lw', 'short': 'lh', 'byte': 'lb', 'char': 'lb', 'number': 'lb', 'address': 'lw'}
  loadFunc = 'lb'
  if definitions.getSupertype(loadType) == 'address': loadType = 'address'
  if loadType in numLoadFuncs: loadFunc = numLoadFuncs[loadType]
  if utils.isRegister(address): raise utils.CompileException('Can\'t load directly from register')

  if outerInner == None: comment = utils.formatComment('{} = {}'.format(outputReg, address), props, 2)
  else: comment = utils.formatComment('{} = {}[{}]'.format(outputReg, outerInner[0], outerInner[1]), props, 2)

  return '{} {}, {}{}'.format(loadFunc, utils.getRegister(outputReg), address, comment)

def loadIntOrChar(value, outputReg, props):
  comment = utils.formatComment('{} = {}'.format(outputReg, value), props, 2)
  return 'addi {}, $0, {}{}'.format(utils.getRegister(outputReg), utils.getIntOrChar(value), comment)

def loadRegister(valueReg, outputReg, props):
  comment = utils.formatComment('{} = {}'.format(outputReg, valueReg), props, 2)
  return 'add {}, $0, {}{}'.format(utils.getRegister(outputReg), utils.getRegister(valueReg), comment)

def isRegHiLo(reg):
  return utils.getRegister(reg) == '$hi' or utils.getRegister(reg) == '$lo'

def loadRegHiLo(reg, outputReg, props):
  comment = utils.formatComment('{} = {}'.format(reg, outputReg), props, 2)
  return 'mf{} {}{}'.format(reg[1:], utils.getRegister(outputReg), comment)
