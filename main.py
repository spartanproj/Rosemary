from lex import *
from parse import *
from emit import *
print("Rosemary Compiler")
if len(sys.argv) != 3:
    sys.exit("Error: Compiler needs source file as argument.")
with open(sys.argv[1], 'r') as inputFile:
    source = inputFile.read()
# Initialize the lexer and parser.
source=source.replace("{","")
source=source.replace("}","end")
source=source.replace("if","IF")
source=source.replace("while","WHILE")
lexer = Lexer(source)
emitter=Emitter(sys.argv[2])
parser = Parser(lexer,emitter)
parser.program() # Start the parser.
emitter.write()
print("Compiling completed.")