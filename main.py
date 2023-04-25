from lex import *
from parse import *
from emit import *
print("Rosemary Compiler")
if len(sys.argv) != 2:
    sys.exit("Error: Compiler needs source file as argument.")
with open(sys.argv[1], 'r') as inputFile:
    source = inputFile.read()
# Initialize the lexer and parser.
lexer = Lexer(source)
emitter=Emitter("out.c")
parser = Parser(lexer,emitter)
parser.program() # Start the parser.
emitter.write()
print("Compiling completed.")