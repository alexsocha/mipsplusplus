# MIPS++ Programming Language
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
* **comments** The level of commenting in the generated MIPS code.
0 = none, 1 = minimal, 2 = almost every line. Defaults to 1.

* **registers** List of temporary registers (in order) for the compiler to use where necessary. These should not be used to store variables as they may be overridden. The compiler will indicate if more are required for any particular statement. Defaults to `[$t0, $t1, $t2]`.

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
Not yet written.
