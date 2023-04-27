import sys,os
from lex import *
log=True
def log(*args):
    if log==False:return -1
    for x in args:
        print(x)
    return 1
class Parser:
    def __init__(self,lexer,emitter,sourcelines):
        self.lexer = lexer
        self.emitter=emitter

        self.sourcelines=sourcelines
        self.floats=set()
        self.ints=set()
        self.strings=set()
        self.labels=set()
        self.gotos=set()
    
        self.curtok = None
        self.peektok = None
        self.line=1
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
        log("PROGRAM")
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
            log("print")
            self.next()
            if self.checkcur(Type.STRING):
                self.emitter.emit("printf(\""+self.curtok.text+"\\n\");")
                self.next()
            elif self.curtok.text in self.floats:
                self.emitter.emitn("printf(\"%" + "f\\n\", (float)(")
                self.expression()
                self.emitter.emit("));")
            elif self.curtok.text in self.ints:
                self.emitter.emitn("printf(\"%" + "d\\n\",")
                self.expression()
                self.emitter.emit(");")
            elif self.curtok.text in self.strings:
                self.emitter.emitn("printf(")
                self.emitter.emitn(self.curtok.text)
                self.emitter.emit(");")
                self.next()
            elif self.checkcur(Type.NUMBER):
                self.emitter.emit("printf(\"%d\",\""+self.curtok.text+"\"\\n\");")
                self.next()
            else:
                self.panic("Argument to print is erroneous - "+self.curtok.text)
        elif self.checkcur(Type.IF):
            log("IF")
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
                log("elif")
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
                log("else")
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
            log("loop")
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
            log("WHILE")
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
            log("label")
            self.next()
            if self.curtok.text in self.labels:
                self.panic("Label already exists: " + self.curtok.text)
            self.labels.add(self.curtok.text)
            self.emitter.emit(self.curtok.text+":")
            self.match(Type.IDENT)
        elif self.checkcur(Type.goto):
            log("goto")
            self.next()
            self.gotos.add(self.curtok.text)
            self.emitter.emit("goto "+self.curtok.text+";")
            self.match(Type.IDENT)
        elif self.checkcur(Type.float):
            log("float")
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
            log("int")
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
            log("ints")
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
            log("floats")
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
            log("string")
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
            log("strings")
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
            log("extern")
            print("""
WARNING
C CODE IS BEING INJECTED INTO YOUR PROGRAM""")
            self.next()
            self.matchn(Type.STRING)
            print(self.curtok.text,"\n\n")
            self.emitter.emit(self.curtok.text)
            self.next()
        elif self.checkcur(Type.IDENT):
            log("reassign")
            if self.checkpeek(Type.PLUSEQ):
                self.emitter.emitn(self.curtok.text+"+=")
                self.next()
                self.match(Type.PLUSEQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.MINUSEQ):
                self.emitter.emitn(self.curtok.text+"-=")
                self.next()
                self.match(Type.MINUSEQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.ASTEQ):
                self.emitter.emitn(self.curtok.text+"*=")
                self.next()
                self.match(Type.ASTEQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.SLASHEQ):
                self.emitter.emitn(self.curtok.text+"/=")
                self.next()
                self.match(Type.SLASHEQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.PLUSPLUS):
                if self.curtok.text in self.floats or self.curtok.text in self.ints:
                    self.emitter.emitn(self.curtok.text+"++;")
                    self.next()
                    self.match(Type.PLUSPLUS)
                else:
                    self.panic("Attempting to increment non-numeric value - "+self.curtok.text)
            elif self.checkpeek(Type.MINMIN):
                if self.curtok.text in self.floats or self.curtok.text in self.ints:
                    self.emitter.emitn(self.curtok.text+"--;")
                    self.next()
                    self.match(Type.MINMIN)
                else:
                    self.panic("Attempting to decrement non-numeric value - "+self.curtok.text)
            
            elif self.curtok.text in self.floats or self.curtok.text in self.ints or self.curtok.text in self.strings:
                self.emitter.emitn(self.curtok.text+"=")
                self.next()
                self.match(Type.EQ)
                self.expression()
                self.emitter.emit(";")
            else:
                self.panic("Attempting to reassign variable before assignment - "+self.curtok.text)
        elif self.checkcur(Type.input):
            log("input")
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
        else:
            self.panic("Invalid statement \""+self.curtok.text+"\"")
        self.nl()
    def strcmp(self):
        log("strcmp")
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
        log("COMPARISON")
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
        log("EXPRESSION")
        self.term()
        while self.checkcur(Type.PLUS) or self.checkcur(Type.MINUS):
            self.emitter.emitn(self.curtok.text)
            self.next()
            self.term()
        
    def term(self):
        log("TERM")
        self.unary()
        while self.checkcur(Type.ASTERISK) or self.checkcur(Type.FSLASH) or self.checkcur(Type.PERCENT):
            self.emitter.emitn(self.curtok.text)
            self.next()
            self.unary()
    def unary(self):
        log("UNARY")
        if self.checkcur(Type.PLUS) or self.checkcur(Type.MINUS):
            self.emitter.emitn(self.curtok.text)
            self.next()        
        self.primary()
    def primary(self):
        log("PRIMARY (" + self.curtok.text + ")")
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
        