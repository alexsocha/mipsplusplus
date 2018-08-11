from mipsplusplus import utils
from mipsplusplus import operations

OPERATOR_ORDERING = [
  ['addressof', 'not', 'neg'],
  ['*', '/', '%'],
  ['+', '-'],
  ['<<', '>>', '<<<', '>>>'],
  ['<', '>', '<=', '>='],
  ['==', '!='],
  ['and', 'or', 'xor', 'nor'],
  ['as']
]

EXPR_OPERATORS = set([op for ops in OPERATOR_ORDERING for op in ops] +  ['(', ')'])

def splitExpression(expression):
  squareBracketDepth = 0
  isSingleQuote = False
  isDoubleQuote = False
  funcBracketDepth = 0

  # Split expression on whitespace or single operators, 
  # given it isn't in single quotes, double quotes, square brackets,
  # or within a a function such as alloc(...)
  tokenList = ['']
  tokenIdx = 0
  i = 0
  while i < len(expression):
    char = expression[i]

    if char == '\'': isSingleQuote = not isSingleQuote
    if char == '"': isDoubleQuote = not isDoubleQuote
    
    if isSingleQuote == False and isDoubleQuote == False:
      if funcBracketDepth == 0:
        if char == '[': squareBracketDepth += 1
        elif char == ']': squareBracketDepth -= 1
        elif char == '(':
          isSysFunc = False
          for func in utils.SYS_FUNCTIONS:
            if tokenList[tokenIdx] == func: isSysFunc = True
          if isSysFunc: funcBracketDepth += 1

        if funcBracketDepth == 0 and squareBracketDepth == 0:
          nextOperator = None
          for op in EXPR_OPERATORS:
            spacedOp = ' {} '.format(op) if op.isalnum() else op
            if expression[i:].startswith(spacedOp):
              if nextOperator is None or len(spacedOp) > len(nextOperator):
                nextOperator = spacedOp

          if char.isspace() or nextOperator is not None:
            if tokenList[tokenIdx] != '':
              tokenList += ['']
              tokenIdx += 1
            if nextOperator is not None:
              tokenList[tokenIdx] += nextOperator.strip()
              tokenList += ['']
              tokenIdx += 1
              i += len(nextOperator)-1
            i += 1
            while i < len(expression):
              if not expression[i].isspace(): break
              else: i += 1
            continue
      else:
        if char == '(': funcBracketDepth += 1
        elif char == ')': funcBracketDepth -= 1

    tokenList[tokenIdx] += char
    i += 1
  
  if len(tokenList) > 0 and tokenList[-1] == '':
    tokenList = tokenList[:-1]

  # Convert minus sign to negative e.g. ['+', '-', '8'] => ['+', '-8']
  newTokenList = []
  tokenIdx = 0
  while tokenIdx < len(tokenList):
    if tokenList[tokenIdx] == '-' and tokenIdx < len(tokenList)-1:
      if tokenIdx == 0 or tokenList[tokenIdx-1] in EXPR_OPERATORS:
        newTokenList.append('-' + tokenList[tokenIdx+1])
        tokenIdx += 2
        continue
    newTokenList.append(tokenList[tokenIdx])
    tokenIdx += 1

  return newTokenList

def infixToPostfix(tokenList, getToken = lambda item: item):
  # Get priorities from ordering
  priorities = {}
  for (level, ops) in enumerate(OPERATOR_ORDERING):
    priorities = {**priorities, **{op: len(OPERATOR_ORDERING)-level for op in ops}}
  # Convert expression to reverse polish (postfix) notation
  stack = []
  output = []
  for item in tokenList:
    token = getToken(item)
    if token not in EXPR_OPERATORS:
      output.append(item)
    elif token == '(':
      stack.append(item)
    elif token == ')':
      while stack and getToken(stack[-1]) != '(':
        output.append(stack.pop())
      stack.pop()
    else:
      while stack and getToken(stack[-1]) != '(' and priorities[token] <= priorities[getToken(stack[-1])]:
        output.append(stack.pop())
      stack.append(item)
  while stack: output.append(stack.pop())
  return output

def isInBrackets(string, idx, b1='(', b2=')'):
  bracketTeir = 0
  for i, ch in enumerate(string):
    if ch == b1: bracketTeir += 1
    if ch == b2: bracketTeir -= 1
    if i == idx: return bracketTeir > 0


def isTopLevel(string, idx, b1='(', b2=')'):
  if isInBrackets(string, idx, '(', ')'): return False
  if isInBrackets(string, idx, '[', ']'): return False
  isSingleQuote = False
  isDoubleQuote = False
  for i, ch in enumerate(string):
    if ch == '\'': isSingleQuote = not isSingleQuote
    if ch == '"': isDoubleQuote = not isDoubleQuote
    if i == idx: return not isSingleQuote and not isDoubleQuote
