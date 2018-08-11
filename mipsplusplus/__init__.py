from mipsplusplus import main

def compile(lines, comments=1, registers=['$t0', '$t1', '$t2']):
  return main.compile(lines, comments, registers)
