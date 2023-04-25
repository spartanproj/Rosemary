import sys
from lex import *
log=True
def log(*args):
    if log==False:return -1
    for x in args:
        print(x)
    return 1
class Parser:
    def __init__(self,lexer,emitter):
        self.lexer = lexer
        self.emitter=emitter
        self.symbols=set()
        self.labels=set()
        self.gotos=set()
        self.curtok = None
        self.peektok = None
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
    def next(self):
        self.curtok=self.peektok
        self.peektok=self.lexer.getToken()
    def panic(self,msg):
        sys.exit("Error - "+msg)
    def program(self):
        log("PROGRAM")
        self.emitter.headeremit("#include <stdio.h>")
        self.emitter.headeremit("int main(void) {")
        while self.checkcur(Type.NEWLINE):
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
            else:
                self.emitter.emitn("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emit("));")
        elif self.checkcur(Type.IF):
            log("IF")
            self.next()
            self.emitter.emit("if(")
            self.comparison()
            self.nl()
            self.emitter.emit("){")
            while not self.checkcur(Type.end):
                self.statement()
            self.match(Type.end)
            self.emitter.emit("}")
        elif self.checkcur(Type.WHILE):
            log("WHILE")
            self.next()
            self.emitter.emitn("while(")
            self.comparison()
            self.nl()
            self.emitter.emit("){")
            while not self.checkcur(Type.end):
                self.statement()
            self.match(Type.end)
            self.emitter.emit("}")
        elif self.checkcur(Type.label):
            log("label")
            self.next()
            if self.curtok.text in self.labels:
                self.panic("Label already exists: " + self.curToken.text)
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
            if self.curtok.text not in self.symbols:
                self.symbols.add(self.curtok.text)
                self.emitter.headeremit("float " + self.curtok.text + ";")
            self.emitter.emitn(self.curtok.text+"=")
            self.match(Type.IDENT)
            self.match(Type.EQ)
            self.expression()
            self.emitter.emit(";")
        elif self.checkcur(Type.input):
            log("input")
            self.next()
            if self.curtok.text not in self.symbols:
                self.symbols.add(self.curtok.text)
                self.emitter.headeremit("float " + self.curtok.text + ";")
            self.emitter.emit("if(0 == scanf(\"%" + "f\", &" + self.curtok.text + ")) {")
            self.emitter.emit(self.curtok.text + " = 0;")
            self.emitter.emitn("scanf(\"%")
            self.emitter.emit("*s\");")
            self.emitter.emit("}")
            self.match(Type.IDENT)
        else:
            self.panic("Invalid statement \""+self.curtok.text+"\"")
        self.nl()
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
        while self.checkcur(Type.ASTERISK) or self.checkcur(Type.FSLASH):
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
        elif self.checkcur(Type.IDENT):
            if self.curtok.text not in self.symbols:
                self.panic("Referencing variable before assignment: " + self.curtok.text)
            self.emitter.emitn(self.curtok.text)
            self.next()
        else:
            self.panic("Unexpected token at "+self.curtok.text)
    def nl(self):
        self.match(Type.NEWLINE)
        while self.checkcur(Type.NEWLINE):
            self.next()