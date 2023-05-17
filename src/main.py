from lex import *
from parse import *
from emit import *
myname=__file__.split("/")
myname=myname[len(myname)-1]
log(myname,0,"Rosemary Compiler",HIGH)
if len(sys.argv) != 3:
    sys.exit("Error: Compiler needs source file as argument.")
with open(sys.argv[1], 'r') as inputFile:
    source = inputFile.read()
# Initialize the lexer and parser.
sourcelines=source.split("\n")
lexer = Lexer(source)
emitter=Emitter(sys.argv[2])
parser = Parser(lexer,emitter,sourcelines,sys.argv[1])
parser.program() # Start the parser.
emitter.write()
log(myname,parser.line,"Compiling completed.",HIGH)