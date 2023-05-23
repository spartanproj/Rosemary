from lex import *
from parse import *
from emit import *
myname=__file__.split("/")
dup=list(myname)
myname=myname[len(myname)-1]
if len(sys.argv) < 3:
    sys.exit("Error: Compiler needs source file as argument.")

with open(sys.argv[1], 'r') as inputFile:
    source = inputFile.read()
# Initialize the lexer and parser.
sourcelines=source.split("\n")
start=log(myname,0,"Rosemary Compiler",HIGH)
if "-std" in sys.argv:
    path=""
    for j in range(0,len(dup)-2):
        path+=dup[j]+"/"
    with open(path+"std.rh", 'r') as stdlib:
        stdsource = stdlib.read()
    source=stdsource+"\n"+source
lexer = Lexer(source)
emitter=Emitter(sys.argv[2])
parser = Parser(lexer,emitter,sourcelines,sys.argv[1])
parser.program() # Start the parser.
emitter.write()
end=log(myname,parser.line,"Compiling completed.",HIGH)
log(myname,parser.line,f"Time taken: ~{round(end-start,5)} seconds")