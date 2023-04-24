import sys
from lex import *
log=True
def log(*args):
    if log==False:return -1
    for x in args:
        print(x)
    return 1
class Parser:
    def __init__(self,lexer):
        self.lexer = lexer
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
        while self.checkcur(Type.NEWLINE):
            self.next()
        while not self.checkcur(Type.EOF):
            self.statement()
        for label in self.gotos:
            if label not in self.labels:
                self.panic("Attempting to GOTO to undeclared label: " + label)
    def statement(self):
        if self.checkcur(Type.PRINT):
            log("PRINT")
            self.next()
            if self.checkcur(Type.STRING):
                self.next()
            else:
                self.expression()
        elif self.checkcur(Type.IF):
            log("IF")
            self.next()
            self.comparison()
            self.nl()
            while not self.checkcur(Type.END):
                self.statement()
            self.match(Type.END)
        elif self.checkcur(Type.WHILE):
            log("WHILE")
            self.next()
            self.comparison()
            self.nl()
            while not self.checkcur(Type.END):
                self.statement()
            self.match(Type.END)
        elif self.checkcur(Type.LABEL):
            log("LABEL")
            self.next()
            if self.curtok.text in self.labels:
                self.panic("Label already exists: " + self.curToken.text)
            self.labels.add(self.curtok.text)
            self.match(Type.IDENT)
        elif self.checkcur(Type.GOTO):
            log("GOTO")
            self.next()
            self.gotos.add(self.curtok.text)
            self.match(Type.IDENT)
        elif self.checkcur(Type.LET):
            log("LET")
            self.next()
            if self.curtok.text not in self.symbols:
                self.symbols.add(self.curtok.text)
            self.match(Type.IDENT)
            self.match(Type.EQ)
            self.expression()
        elif self.checkcur(Type.INPUT):
            log("INPUT")
            self.next()
            if self.curtok.text not in self.symbols:
                self.symbols.add(self.curtok.text)
            self.match(Type.IDENT)
        else:
            self.panic("Invalid statement \""+self.curtok.text+"\"")
        self.nl()
    def comparison(self):
        log("COMPARISON")
        self.expression()
        if self.isCompOp():
            self.next()
            self.expression()
        else:
            self.panic("Expected comparison operator at: " + self.curtok.text)
        while self.isCompOp():
            self.next()
            self.expression()
    def isCompOp(self):
        return self.checkcur(Type.GT) or self.checkcur(Type.GTEQ) or self.checkcur(Type.LT) or self.checkcur(Type.LTEQ) or self.checkcur(Type.EQEQ) or self.checkcur(Type.NOTEQ)
    def expression(self):
        log("EXPRESSION")
        self.term()
        while self.checkcur(Type.PLUS) or self.checkcur(Type.MINUS):
            self.next()
            self.term()
    def term(self):
        log("TERM")
        self.unary()
        while self.checkcur(Type.ASTERISK) or self.checkcur(Type.FSLASH):
            self.next()
            self.unary()
    def unary(self):
        log("UNARY")
        if self.checkcur(Type.PLUS) or self.checkcur(Type.MINUS):
            self.next()        
        self.primary()
    def primary(self):
        log("PRIMARY (" + self.curtok.text + ")")
        if self.checkcur(Type.NUMBER):
            self.next()
        elif self.checkcur(Type.IDENT):
            if self.curtok.text not in self.symbols:
                self.panic("Referencing variable before assignment: " + self.curtok.text)
            self.next()
        else:
            self.panic("Unexpected token at "+self.curtok.text)
    def nl(self):
        log("NEWLINE")
        self.match(Type.NEWLINE)
        while self.checkcur(Type.NEWLINE):
            self.next()