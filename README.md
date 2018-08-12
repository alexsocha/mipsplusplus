# MIPS++ Programming Language
[![Build Status](https://travis-ci.com/alexsocha/mipsplusplus.svg?branch=master)](https://travis-ci.com/alexsocha/mipsplusplus)
[![PyPI version](https://badge.fury.io/py/mipsplusplus.svg)](https://badge.fury.io/py/mipsplusplus)

<img src="https://raw.githubusercontent.com/alexsocha/mipsplusplus/master/logo.svg?sanitize=true" align="left" hspace="10" width="150px">

**MIPS++** is a low-level programming language based on the [MIPS architecture](https://en.wikipedia.org/wiki/MIPS_architecture). Its purpose is to generate faithful MIPS assembly code using a clearer syntax, with a focus on optimization. It is also a superset of MIPS.

Current features include arithmetic expressions, data types, register aliases (i.e. local variables), conditional jumps and arrays.

## Usage

Installing:
```
pip install mipsplusplus
```

Command line:
```
python -m mipsplusplus path/to/source.mpp -o output.asm
--comments 1 --registers "$t0" "$t1" "$t1"
```

Python:
```python
import mipsplusplus

compiled = mipsplusplus.compile(lines=source.readlines(),
  comments=1, registers=['$t0', '$t1', '$t2'])
```

### Optional Parameters
* **comments:** The level of commenting in the generated MIPS code.
0 = none, 1 = minimal, 2 = almost every line. Defaults to 1.

* **registers:** List of temporary registers (in order) for the compiler to use where necessary. These should not be used to store variables as they may be overridden. The compiler will indicate if more are required for any particular statement. Defaults to `[$t0, $t1, $t2]`.

## Syntax Example
The following program converts a decimal number to an arbitrary base.
```ruby
.data
byte[30] digits
string numPrompt = "Enter number: "
string basePrompt = "Enter base: "
string convertedInfo = "Converted: "

.text
@alias $num = $t3, $base = $t4, $i = $t5

print numPrompt
$num = input()

print basePrompt
$base = input()

$i = 0
calcLoop:
  digits[$i] = $num % $base
  $num = $num / $base

  $i = $i + 1
  goto calcLoop if $num > 0

print convertedInfo
printLoop:
  $i = $i - 1
  goto endPrintLoop if i < 0

  @alias $digit = $t3
  $digit = digits[$i]

  goto printAsChar if $digit > 9

  print $digit
  goto printLoop

  printAsChar:
    print (55 + $digit) as char
    goto printLoop
endPrintLoop:
exit
```

## Language Reference
### Definitions
```ruby
.data
# Numeric
int x = 123456789 # 4 bytes
short y = -32000  # 2 bytes
byte z = 64       # 1 byte
char letter = 'C' # 1 byte

# Addresses/arrays
string greeting = "hello"
char[20] name # Empty string with space for 20 characters

int[] numbers = [20, -65, 42]
byte[30] byteArray

.text
# ...code
```

### Registers and Variables
```ruby
# Any register can be given an alias, which remains
# for all following lines or until it is reassigned
@alias $num = $t3, $array = $t4, $character = $t5

# Direct register assignment
$num = 42
$character = 'K'

# Loading from defined variables
$num = x
$array = numbers
$character = letter

# Saving to defined variables
x = $num
letter = 'M'
y = letter # Uses ASCII value
```

### Operators
```ruby
# Standard
$num = (x + y) / (z - 7)
$num = neg $num * (y % 8)

# Boolean logic
$true = 1
$false = 0
$bool = not ($true and $false) nor $true xor ($true or $false)

# Bitwise
$num = (1 << 4) and ($num >> 1) # Zeros are shifted in
$num = -8 >>> 2 # The sign bit is shifted in
# Note that <<< is not an operator

# Comparison
$condition = z < 200
# Note that this is the only comparison operator
# which can be used in arbitrary expressions
```

### Addresses
```ruby
# Addresses
$numAddress = addressof x # Requires explicit 'addressof' operator
$stringAddress = greeting
$arrayAddress = numbers

$offsetAddress = $numbers + 4
$offsetAddress = addressof $numbers[4] # Equivalent to previous line
```

### Arrays
```ruby
# Byte arrays
$num = byteArray[3]
byteArray[4] = 42 + $num - z

# Integer arrays
# (indexes must be multiplied by the number
# of bytes in the corresponding data type)
num = numbers[$index * 4] 
numbers[24] = 32 # Sets the 6th element

# Ambiguous arrays
$array = someArray

# - Explicit
$num = $array[0] as int # Load value as int
$array[4] as int = $num # Store value as int

# - Implied
$array[8] = 42 # Store int
$array[9] = 42 as byte # Store byte
$array[10] = $num + y + 3 # Store short
$array[11] = $array[12] as char # Load and store char (byte)

# - Combined
$array1[13] as int = 6 * ($array2[$i * 2] as short) # Load short, store int
$array3[14] = (22 - numbers[$i * 4]) as byte # Load int, store byte
```

### Control Flow
```ruby
label:
  # ...

# Jumping to labels
goto label
gotolink label # Return address is stored in $ra

# Jumping to addresses in registers
$storedLabel = label # (addressof label)
goto $storedLabel

# Conditional jumps
# (supports all comparison operators)
goto label if x > 9
goto label if $num + 4 != x
goto $storedLabel if $num % 7 <= x / y
goto $storedLabel if $condition1 and x < 8 # ($condition1 and x < 8) == 1

# - With link (only < 0 and >= 0)
gotolink label if $num < 0
gotolink $storedLabel if $num >= 0
```

### System Functions
```ruby
# Printing
print $num
print greeting
print $character as char

# Input integer
$num = input()
x = input() + 6
input() # Value is stored in $v0

# Input string
inputstr name
inputstr addressof $array[8]
inputstr $location, 40 # Max length 40

# Memory allocation
address = alloc(50) # Alocate 50 bytes, store first address as int
$array = alloc(20) + 4 # Offset by 4
alloc(80) # Address is stored in $v0

# Exit
exit
```
