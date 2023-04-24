import enum,sys
class Lexer:
    def __init__(self,source):
        self.source=source+"\n"
        self.cur=""
        self.pos=-1
        self.next()
    def next(self):
        self.pos+=1
        if self.pos >= len(self.source):
            self.cur="\0"
        else:
            self.cur=self.source[self.pos]
    def peek(self):
        if self.pos+1 >= len(self.source):
            return "\0"
        else:
            return self.source[self.pos+1]
    def panic(self,msg):
        sys.exit("Lexing error - "+msg)
    def skip(self):
        while self.cur in [" ","\t","\r"]:
            self.next()
    def comm(self):
        if self.cur=="#":
            while self.cur!="\n":
                self.next()
    def getToken(self):
        self.skip()
        self.comm()
        token=None
        matched=True
        match self.cur:
            case "+":
                token=Token(self.cur,Type.PLUS)
            case "-":
                token=Token(self.cur,Type.MINUS)
            case "*":
                token=Token(self.cur,Type.ASTERISK)
            case "/":
                token=Token(self.cur,Type.FSLASH)
            case "\n":
                token=Token(self.cur,Type.NEWLINE)
            case "\0":
                token=Token(self.cur,Type.EOF)
            case "=":
                if self.peek()=="=":
                    last=self.cur
                    self.next()
                    token=Token(last+self.cur, Type.EQEQ)
                else:
                    token=Token(self.cur, Type.EQ)
            case ">":
                if self.peek()=="=":
                    last=self.cur
                    self.next()
                    token=Token(last+self.cur, Type.GTEQ)
                else:
                    token=Token(self.cur,Type.GT)
            case "<":
                if self.peek()=="=":
                    last=self.cur
                    self.next()
                    token=Token(last+self.cur, Type.LTEQ)
                else:
                    token=Token(self.cur,Type.LT)
            case "!":
                if self.peek()=="=":
                    last=self.cur
                    self.next()
                    token=Token(last+self.cur, Type.NOTEQ)
                else:
                    self.panic("Expected !=, got !"+self.peek())
            case "\"":
                self.next()
                start=self.pos
                while self.cur!="\"":
                    if self.cur in ["\r","\n","\t","\\","%"]:
                        self.panic("Illegal character in string literal "+self.cur)
                    self.next()

                tokText=self.source[start:self.pos]
                token=Token(tokText,Type.STRING)
            case _:
                matched=False
        if self.cur.isdigit() and not matched:
            start=self.pos
            while self.peek().isdigit():
                self.next()
            if self.peek()==".":
                self.next()
                if not self.peek().isdigit():
                    self.panic("Illegal character in number: "+self.cur)
                while self.peek().isdigit():
                    self.next()
            tokText=self.source[start:self.pos+1]
            token=Token(tokText, Type.NUMBER)
        elif self.cur.isalpha():
            start=self.pos
            while self.peek().isalnum():
                self.next()
            tokText=self.source[start:self.pos+1]
            keyw=Token.checkIfKeyword(tokText)
            if keyw==None:
                token=Token(tokText,Type.IDENT)
            else:
                token=Token(tokText,keyw)
        self.next()
        return token
class Token:
    def __init__(self,text,type):
        self.text=text
        self.type=type
    @staticmethod
    def checkIfKeyword(tokenText):
        for type in Type:
            # Relies on all keyword enum values being 1XX.
            if type.name == tokenText and type.value >= 100 and type.value < 200:
                return type
        return None
class Type(enum.Enum):
        EOF = -1
        NEWLINE = 0
        NUMBER = 1
        IDENT = 2
        STRING = 3
        LABEL = 101
        GOTO = 102
        PRINT = 103
        INPUT = 104
        LET = 105
        IF = 106
        LBRACK = 107
        RBRACK = 108
        WHILE = 109
        EQ = 201  
        PLUS = 202
        MINUS = 203
        ASTERISK = 204
        FSLASH = 205
        EQEQ = 206
        NOTEQ = 207
        LT = 208
        LTEQ = 209
        GT = 210
        GTEQ = 211