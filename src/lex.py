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
        if self.cur=="/" and self.peek()=="/":
            while self.cur!="\n":
                self.next()
    def getToken(self):
        self.skip()
        self.comm()
        token=None
        matched=True
        match self.cur:
            case "+":
                if self.peek()=="=":
                    token=Token(self.source[self.pos:self.pos+1],Type.PLUSEQ)
                    self.next()
                else:
                    token=Token(self.cur,Type.PLUS)
            case "-":
                if self.peek()=="=":
                    token=Token(self.source[self.pos:self.pos+1],Type.MINUSEQ)
                    self.next()
                else:
                    token=Token(self.cur,Type.MINUS)
            case "*":
                if self.peek()=="=":
                    token=Token(self.source[self.pos:self.pos+1],Type.ASTEQ)
                    self.next()
                else:
                    token=Token(self.cur,Type.ASTERISK)
            case "/":
                if self.peek()=="=":
                    token=Token(self.source[self.pos:self.pos+1],Type.SLASHEQ)
                    self.next()
                else:
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
            case "{":
                token=Token(self.cur,Type.LBRACK)
            case "}":
                token=Token(self.cur,Type.RBRACK)
            case "i":
                if self.peek()=="f":
                    token=Token(self.cur+self.source[self.pos+1],Type.IF)
                    self.next()
                    self.next()
            case "w":
                initpos=self.pos
                if self.peek()=="h":
                    self.next()
                    if self.peek()=="i":
                        self.next()
                        if self.peek()=="l":
                            self.next()
                            if self.peek()=="e":
                                token=Token(self.source[initpos:self.pos],Type.WHILE)
                                self.next()
                                self.next()
            case "e":
                initpos=self.pos
                if self.peek()=="l":
                    self.next()
                    if self.peek()=="i":
                        self.next()
                        if self.peek()=="f":
                            token=Token(self.source[initpos:self.pos],Type.ELIF)
                            self.next()
                            self.next()
                    elif self.peek()=="s":
                        self.next()
                        if self.peek()=="e":
                            token=Token(self.source[initpos:self.pos],Type.ELSE)
                            self.next()
                            self.next()
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
    def __init__(self,text,kind):
        self.text=text
        self.kind=kind
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
        STRING = 3 # string x = *"hello!"*
        label = 101
        goto = 102
        print = 103
        input = 104
        float = 105
        IF = 106
        WHILE = 109
        end=110
        loop=111
        int=112
        string=113 # *string* x = "hello!"
        ELIF=114
        ELSE=115
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
        LBRACK=212
        RBRACK=213
        PLUSEQ=214
        MINUSEQ=215
        ASTEQ=216
        SLASHEQ=217