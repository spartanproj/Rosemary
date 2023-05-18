import sys,os,datetime
from lex import *
logy=True
LOW=0
MED=1
HIGH=2
def log(filename,line,arg,level=LOW):
    if logy==False and level==LOW:return -1
    time=datetime.datetime.now()
    ms=datetime.datetime.now()
    x=time.strftime(r"%Y-%m-%d %H:%M:%S%z")
    realms=ms.strftime("%f")[0:4]
    print(f"{x}.{realms} @ line {line} @ {filename} - ",end="")
    print(arg,end="")
    print()
    return datetime.datetime.timestamp(time)
class Parser:
    def __init__(self,lexer,emitter,sourcelines,fname):
        self.lexer = lexer
        self.emitter=emitter
        self.fname=fname
        self.sourcelines=sourcelines
        self.floats=set()
        self.ints=set()
        self.strings=set()
        self.labels=set()
        self.gotos=set()
        self.funcs=[]

        self.curtok = None
        self.peektok = None
        self.line=0
        self.next()
        self.next()
    def checkcur(self,kind):
        return kind==self.curtok.kind
    def checkpeek(self,kind):
        return kind == self.peektok.kind
    def match(self,kind):
        if not self.checkcur(kind):
            self.panic("Expected "+kind.name+" , got "+self.curtok.kind.name)
        self.next()
    def matchopt(self,kind):
        if self.checkcur(kind):
            self.next()
            return 1
        return 0
    def matchoptn(self,kind):
        if self.checkcur(kind):
            return 1
        return 0
    def funcvals(self,func) -> int:
        for value1 in self.funcs:
            for key,value in value1.items():
                if key==func:
                    return [int(value),value1["argtype"]]
        return -1
    def matchn(self,kind):
        if not self.checkcur(kind):
            self.panic("Expected "+kind.name+" , got "+self.curtok.kind.name)
    def next(self):
        self.curtok=self.peektok
        self.peektok=self.lexer.getToken()
    def panic(self,msg):
        sys.exit("Error - "+msg+ " at token "+self.curtok.text+f" (line {self.line} - `{self.sourcelines[self.line-1].strip()}`)")
    def warning(self,msg):
        sys.exit("Warning - "+msg+ " at token "+self.curtok.text+f" (line {self.line} - `{self.sourcelines[self.line-1].strip()}`)")
    def program(self):
        log(self.fname,self.line,"PROGRAM")
        self.line+=1
        self.emitter.headeremit("#include <stdio.h>")
        self.emitter.headeremit("#include <stdint.h>")
        self.emitter.headeremit("#include <stdlib.h>")
        self.emitter.headeremit("#include <string.h>")
        self.emitter.headeremit("int main(void) {")
        self.emitter.headeremit("int iterable;")
        while self.checkcur(Type.NEWLINE):
            self.line+=1
            self.next()
        while not self.checkcur(Type.EOF):
            self.statement()
        self.emitter.emit("return 0;")
        self.emitter.emit("}");
        for label in self.gotos:
            if label not in self.labels:
                self.panic("Attempting to goto to undeclared label: " + label)
    def statement(self):
        if self.checkcur(Type.print):
            log(self.fname,self.line,"print")
            self.next()
            if self.checkcur(Type.STRING):
                self.emitter.emit("printf(\""+self.curtok.text+"\");")
                self.next()
            elif self.curtok.text in self.floats:
                self.emitter.emitn("printf(\"%" + "f\", (float)(")
                self.expression()
                self.emitter.emit("));")
            elif self.curtok.text in self.ints:
                self.emitter.emitn("printf(\"%" + "d\",")
                self.expression()
                self.emitter.emit(");")
            elif self.curtok.text in self.strings:
                self.emitter.emitn("printf(")
                self.emitter.emitn(self.curtok.text)
                self.emitter.emit(");")
                self.next()
            elif self.checkcur(Type.NUMBER):
                self.emitter.emit("printf(\"%d\",\""+self.curtok.text+"\"\");")
                self.next()
            else:
                self.panic("Argument to print is erroneous - "+self.curtok.text)
        elif self.checkcur(Type.IF):
            log(self.fname,self.line,"IF")
            self.next()
            self.emitter.emitn("if(")
            if self.checkpeek(Type.DOUDOL):
                self.strcmp()
            else:
                self.comparison()
            self.match(Type.LBRACK)
            self.nl()
            self.emitter.emit("){")
            while not self.checkcur(Type.RBRACK):
                self.statement()
            self.match(Type.RBRACK)
            self.emitter.emit("}")
            while self.checkcur(Type.ELIF):
                log(self.fname,self.line,"elif")
                self.next()
                self.emitter.emitn("else if(")
                if self.checkpeek(Type.DOUDOL):
                    self.strcmp()
                else:
                    self.comparison()
                self.match(Type.LBRACK)
                self.nl()
                self.emitter.emit("){")
                while not self.checkcur(Type.RBRACK):
                    self.statement()
                self.match(Type.RBRACK)
                self.emitter.emit("}")
            if self.checkcur(Type.ELSE):
                log(self.fname,self.line,"else")
                self.next()
                self.emitter.emitn("else")
                self.match(Type.LBRACK)
                self.nl()
                self.emitter.emit("{")
                while not self.checkcur(Type.RBRACK):
                    self.statement()
                self.match(Type.RBRACK)
                self.emitter.emit("}")
        elif self.checkcur(Type.ELIF) or self.checkcur(Type.ELSE):
            ifse="if" if self.checkcur(Type.ELIF) else "se"
            self.panic(f"El{ifse} without if")
        elif self.checkcur(Type.loop):
            log(self.fname,self.line,"loop")
            self.next()
            self.emitter.emitn("for(iterable=0;iterable<")
            self.expression()
            self.match(Type.LBRACK)
            self.nl()
            self.emitter.emit(";iterable++){")
            while not self.checkcur(Type.RBRACK):
                self.statement()
            self.match(Type.RBRACK)
            self.emitter.emit("}")
        elif self.checkcur(Type.WHILE):
            log(self.fname,self.line,"WHILE")
            self.next()
            self.emitter.emitn("while(")
            self.comparison()
            self.match(Type.LBRACK)
            self.nl()
            self.emitter.emit("){")
            while not self.checkcur(Type.RBRACK):
                self.statement()
            self.match(Type.RBRACK)
            self.emitter.emit("}")
        elif self.checkcur(Type.label):
            log(self.fname,self.line,"label")
            self.next()
            if self.curtok.text in self.labels:
                self.panic("Label already exists: " + self.curtok.text)
            self.labels.add(self.curtok.text)
            self.emitter.emit(self.curtok.text+":")
            self.match(Type.IDENT)
        elif self.checkcur(Type.goto):
            log(self.fname,self.line,"goto")
            self.next()
            self.gotos.add(self.curtok.text)
            self.emitter.emit("goto "+self.curtok.text+";")
            self.match(Type.IDENT)
        elif self.checkcur(Type.float):
            log(self.fname,self.line,"float")
            self.next()
            if self.curtok.text not in self.floats:
                self.floats.add(self.curtok.text)
                self.emitter.headeremit("float " + self.curtok.text + ";")
            self.emitter.emitn(self.curtok.text+"=")
            self.match(Type.IDENT)
            self.match(Type.EQ)
            self.expression()
            self.emitter.emit(";")
        elif self.checkcur(Type.int):
            log(self.fname,self.line,"int")
            self.next()
            if self.curtok.text not in self.ints:
                self.ints.add(self.curtok.text)
                self.emitter.headeremit("int64_t " + self.curtok.text + ";")
            self.emitter.emitn(self.curtok.text+"=")
            self.match(Type.IDENT)
            self.match(Type.EQ)
            try:
                int(self.curtok.text)
            except:
                if self.curtok.text not in self.ints:
                    self.panic("Attempting to assign non-integer value to int variable")
            self.expression()
            self.emitter.emit(";")
        elif self.checkcur(Type.ints):
            log(self.fname,self.line,"ints")
            self.next()
            while self.checkcur(Type.IDENT):
                if self.curtok.text in self.floats or self.curtok.text in self.ints or self.curtok.text in self.strings:
                    self.panic("Attempting to redeclare variable - "+self.curtok.text)
                self.emitter.emitn("int64_t ")
                self.emitter.emitn(self.curtok.text)
                self.emitter.emit("=0;")
                self.ints.add(self.curtok.text)
                self.next()
                if not self.checkcur(Type.COMMA):
                    break
                self.next()
        elif self.checkcur(Type.floats):
            log(self.fname,self.line,"floats")
            self.next()
            while self.checkcur(Type.IDENT):
                if self.curtok.text in self.floats or self.curtok.text in self.ints or self.curtok.text in self.strings:
                    self.panic("Attempting to redeclare variable - "+self.curtok.text)
                self.emitter.emitn("float ")
                self.emitter.emitn(self.curtok.text)
                self.emitter.emit("=0;")
                self.floats.add(self.curtok.text)
                self.next()
                if not self.checkcur(Type.COMMA):
                    break
                self.next()  
        elif self.checkcur(Type.string):
            log(self.fname,self.line,"string")
            self.next()
            if self.curtok.text not in self.strings:
                self.strings.add(self.curtok.text)
                self.emitter.headeremit("char * " + self.curtok.text + "=malloc(8192);")
            self.emitter.emitn(self.curtok.text+"=\"")
            self.match(Type.IDENT)
            self.match(Type.EQ)
            try:
                str(self.curtok.text)
            except:
                self.panic("Attempting to assign non-string value to string variable")
            self.matchn(Type.STRING)
            self.emitter.emitn(self.curtok.text)
            self.next()
            self.emitter.emit("\";")
        elif self.checkcur(Type.strings):
            log(self.fname,self.line,"strings")
            self.next()
            while self.checkcur(Type.IDENT):
                if self.curtok.text in self.floats or self.curtok.text in self.ints or self.curtok.text in self.strings:
                    self.panic("Attempting to redeclare variable - "+self.curtok.text)
                self.emitter.emitn("char * ")
                self.emitter.emitn(self.curtok.text)
                self.emitter.emit("=malloc(8192);")
                self.strings.add(self.curtok.text)
                self.next()
                if not self.checkcur(Type.COMMA):
                    break
                self.next() 
        elif self.checkcur(Type.extern):
            log(self.fname,self.line,"extern")
            
            self.next()
            self.matchn(Type.STRING)
            log(self.fname,self.line,"C Injection Warning - "+"`"+self.curtok.text+"`",HIGH)
            self.emitter.emit(self.curtok.text)
            self.next()
        elif self.checkcur(Type.IDENT):
            log(self.fname,self.line,"ident")
            if self.checkpeek(Type.PLUSEQ):
                log(self.fname,self.line,"pluseq")
                self.emitter.emitn(self.curtok.text+"+=")
                self.next()
                self.match(Type.PLUSEQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.MINUSEQ):
                log(self.fname,self.line,"minuseq")
                self.emitter.emitn(self.curtok.text+"-=")
                self.next()
                self.match(Type.MINUSEQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.ASTEQ):
                log(self.fname,self.line,"asteq")
                self.emitter.emitn(self.curtok.text+"*=")
                self.next()
                self.match(Type.ASTEQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.SLASHEQ):
                log(self.fname,self.line,"slasheq")
                self.emitter.emitn(self.curtok.text+"/=")
                self.next()
                self.match(Type.SLASHEQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.PLUSPLUS):
                log(self.fname,self.line,"increment")
                if self.curtok.text in self.floats or self.curtok.text in self.ints:
                    self.emitter.emitn(self.curtok.text+"++;")
                    self.next()
                    self.match(Type.PLUSPLUS)
                else:
                    self.panic("Attempting to increment non-numeric value - "+self.curtok.text)
            elif self.checkpeek(Type.MINMIN):
                log(self.fname,self.line,"decrement")
                if self.curtok.text in self.floats or self.curtok.text in self.ints:
                    self.emitter.emitn(self.curtok.text+"--;")
                    self.next()
                    self.match(Type.MINMIN)
                else:
                    self.panic("Attempting to decrement non-numeric value - "+self.curtok.text)
            
            elif self.curtok.text in self.floats or self.curtok.text in self.ints or self.curtok.text in self.strings:
                log(self.fname,self.line,"reassign")
                self.emitter.emitn(self.curtok.text+"=")
                self.next()
                self.match(Type.EQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.LNBRACK):
                log(self.fname,self.line,"function call")
                self.emitter.emit(self.curtok.text+"(")
                funcname=self.curtok.text
                self.next()
                self.next()
                argtypes=self.funcvals(funcname)
                iterations=range(self.funcvals(funcname)[0])
                for j in iterations:
                    matches= {
                        "int":Type.NUMBER,
                        "float":Type.NUMBER,
                        "string":Type.STRING
                    }
                    currentargtype=argtypes[1][j]
                    self.matchn(matches[currentargtype])
                    filler="" if self.curtok.kind!=Type.STRING else "\""
                    self.emitter.emitn(filler+self.curtok.text+filler)
                    self.next()
                    if j+1!=len(iterations):
                        self.match(Type.COMMA)
                        self.emitter.emitn(",")
                self.emitter.emit(");")
                self.match(Type.RNBRACK)
            else:
                self.panic("Attempting to reassign variable before assignment - "+self.curtok.text)
        elif self.checkcur(Type.input):
            log(self.fname,self.line,"input")
            self.next()
            if self.curtok.text not in self.floats and self.curtok.text not in self.ints and self.curtok.text not in self.strings:
                self.panic("Attempting to input into uninitialised variable "+self.curtok.text)
            if self.curtok.text in self.floats:
                self.emitter.emit("if(0 == scanf(\"%" + "f\", &" + self.curtok.text + ")) {")
                self.emitter.emit(self.curtok.text + " = 0;")
                self.emitter.emitn("scanf(\"%")
                self.emitter.emit("*s\");")
                self.emitter.emit("}")
            elif self.curtok.text in self.ints:
                self.emitter.emit("if(0 == scanf(\"%" + "d\", &" + self.curtok.text + ")) {")
                self.emitter.emit(self.curtok.text + " = 0;")
                self.emitter.emitn("scanf(\"%")
                self.emitter.emit("*s\");")
                self.emitter.emit("}")
            elif self.curtok.text in self.strings:
                self.emitter.emit("if(0 == scanf(\"%" + "s\", " + self.curtok.text + ")) {")
                self.emitter.emit(self.curtok.text + " = 0;")
                self.emitter.emitn("scanf(\"%")
                self.emitter.emit("*s\");")
                self.emitter.emit("}")
            self.match(Type.IDENT)
        elif self.checkcur(Type.inc):
            pass
        elif self.checkcur(Type.func):
            log(self.fname,self.line,"func definition")
            self.emitter.emitn("int ")
            self.next()
            self.emitter.emitn(self.curtok.text)
            name=self.curtok.text
            self.next()
            self.match(Type.LNBRACK)
            self.emitter.emitn("(")
            args,iters=0,0
            typeslist=[]
            typen=""
            matchto= {
                    "int":self.ints,
                    "float":self.floats,
                    "string":self.strings
                }
            argstofunc=[]
            while self.curtok.kind in [Type.float,Type.int,Type.string]:
                args+=1
                self.emitter.emitn(self.curtok.text if self.curtok.kind!=Type.string else "char *"+" ")
                if not self.curtok.kind in [Type.float,Type.int,Type.string]:
                    self.panic(f"Unknown type {self.curtok.text}")
                else:
                    typen=self.curtok.text
                    typeslist+="n" # filler character
                    typeslist[iters]=typen
                    self.next()
                self.emitter.emitn(" "+self.curtok.text)
                self.matchn(Type.IDENT)
                argstofunc.append({self.curtok.text:typen})
                matchto[typen].add(self.curtok.text)
                self.next()
                if self.checkcur(Type.COMMA):
                    self.match(Type.COMMA)
                    self.emitter.emitn(",")
                else:
                    break
                iters+=1
            self.funcs.append({f"{name}":f"{args}","argtype":typeslist})
            self.match(Type.RNBRACK)
            self.match(Type.LBRACK)
            self.emitter.emit("){")
            self.nl()
            while not self.checkcur(Type.RBRACK):
                self.statement()
            for k in argstofunc:
                for varname,typen in k.items():
                    matchto[typen].remove(varname)
            self.match(Type.RBRACK)
            self.emitter.emitn("}")
        else:
            self.panic("Invalid statement \""+self.curtok.text+"\"")
        self.nl()
    def strcmp(self):
        log(self.fname,self.line,"strcmp")
        prevtok=self.curtok.text
        self.next()
        self.emitter.emitn("!strcmp(")
        self.emitter.emitn(prevtok)
        self.match(Type.DOUDOL)
        self.emitter.emitn(",\"")
        self.matchn(Type.STRING)
        self.emitter.emit(self.curtok.text+"\")")
        self.next()
    def comparison(self):
        log(self.fname,self.line,"COMPARISON")
        self.expression()
        if self.isCompOp():
            self.emitter.emitn(self.curtok.text)
            self.next()
            self.expression()
        else:
            self.panic("Expected comparison operator at: " + self.curtok.text)
        while self.isCompOp():
            self.emitter.emitn(self.curtok.text)
            self.next()
            self.expression()
    def isCompOp(self):
        return self.checkcur(Type.GT) or self.checkcur(Type.GTEQ) or self.checkcur(Type.LT) or self.checkcur(Type.LTEQ) or self.checkcur(Type.EQEQ) or self.checkcur(Type.NOTEQ)
    def expression(self):
        log(self.fname,self.line,"EXPRESSION")
        self.term()
        while self.checkcur(Type.PLUS) or self.checkcur(Type.MINUS):
            self.emitter.emitn(self.curtok.text)
            self.next()
            self.term()
        
    def term(self):
        log(self.fname,self.line,"TERM")
        self.unary()
        while self.checkcur(Type.ASTERISK) or self.checkcur(Type.FSLASH) or self.checkcur(Type.PERCENT):
            self.emitter.emitn(self.curtok.text)
            self.next()
            self.unary()
    def unary(self):
        log(self.fname,self.line,"UNARY")
        if self.checkcur(Type.PLUS) or self.checkcur(Type.MINUS):
            self.emitter.emitn(self.curtok.text)
            self.next()        
        self.primary()
    def primary(self):
        log(self.fname,self.line,"PRIMARY (" + self.curtok.text + ")")
        if self.checkcur(Type.NUMBER):
            self.emitter.emitn(self.curtok.text)
            self.next()
        elif self.checkcur(Type.STRING):
            self.emitter.emitn("\""+self.curtok.text+"\"")
            self.next()
        elif self.checkcur(Type.IDENT):
            if self.curtok.text in self.floats or self.curtok.text in self.ints or self.curtok.text in self.strings:
                pass
            else:
                self.panic("Referencing variable before assignment: " + self.curtok.text)
            self.emitter.emitn(self.curtok.text)
            self.next()
        else:
            self.panic("Unexpected token at "+self.curtok.text)
    def nl(self):
        self.match(Type.NEWLINE)
        self.line+=1
        while self.checkcur(Type.NEWLINE):
            self.next()
            self.line+=1
        