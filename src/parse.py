import sys,os,datetime
from lex import *
LOW=0
MED=1
HIGH=2
NONE=3
maxlogy=NONE
if "-00" in sys.argv:
    maxlogy=NONE
elif "-01" in sys.argv:
    maxlogy=HIGH
elif "-02" in sys.argv:
    maxlogy=MED
else:
    maxlogy=LOW
def log(filename,line,arg,level=LOW):
    if maxlogy==LOW and level==LOW:return -1
    if maxlogy==MED and level<MED:return -1
    if maxlogy==HIGH and level<HIGH:return -1
    if maxlogy==3:return -1
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
        self.bools=set()
        self.labels=set()
        self.gotos=set()
        self.funcs=[]
        self.currentfunctionreturn=""
        self.infunc=False


        self.curtok = None
        self.peektok = None
        self.line=0
        self.next()
        self.next()
    def os(self):
        match sys.platform:
            case "linux":
                self.emitter.headeremit("#include <linux.h>")
                self.cexternal("open", ["string", "int", "mode_t"], "int")
                self.cexternal("close", ["int"], "int")
                self.cexternal("read", ["int", "void*", "size_t"], "ssize_t")
                self.cexternal("write", ["int", "const void*", "size_t"], "ssize_t")
                self.cexternal("lseek", ["int", "off_t", "int"], "off_t")
                self.cexternal("mkdir", ["string", "mode_t"], "int")
                self.cexternal("rmdir", ["string"], "int")
                self.cexternal("unlink", ["string"], "int")
                self.cexternal("rename", ["string", "string"], "int")
                self.cexternal("stat", ["string", "struct stat*"], "int")
                self.cexternal("chmod", ["string", "mode_t"], "int")
                self.cexternal("chown", ["string", "uid_t", "gid_t"], "int")
                self.cexternal("utime", ["string", "struct utimbuf*"], "int")
                self.cexternal("link", ["string", "string"], "int")
                self.cexternal("symlink", ["string", "string"], "int")
                self.cexternal("readlink", ["string", "char*", "size_t"], "ssize_t")
    def cexternal(self,name,types,ret):
        self.funcs.append({name: len(types), 'argtype': types, 'ret': ret})
    def functioncall(self):
        log(self.fname,self.line,"function call")
        self.emitter.emitn(self.curtok.text+"(")
        funcname=self.curtok.text
        self.next()
        self.next()
        argtypes=self.funcvals(funcname)
        try:
            iterations=range(self.funcvals(funcname)[0])
        except TypeError:
            iterations=range(self.funcvals(funcname))
        for j in iterations:
            matches= {
                "int":Type.NUMBER,
                "float":Type.NUMBER,
                "string":Type.STRING,
                "bool":Type.NUMBER
            }
            currentargtype=argtypes[1][j]
            match matches[currentargtype]:
                case Type.NUMBER:
                    if self.curtok.kind!=Type.NUMBER and self.curtok.text not in self.ints|self.floats|self.bools:
                        self.panic("Wrong arg type")
                case Type.STRING:
                    if self.curtok.kind!=Type.STRING and self.curtok.text not in self.strings:
                        self.panic("Wrong arg type")
                
            filler="" if self.curtok.kind!=Type.STRING else "\""
            self.emitter.emitn(filler+self.curtok.text+filler)
            self.next()
            if j+1!=len(iterations):
                self.match(Type.COMMA)
                self.emitter.emitn(",")
        self.emitter.emit(");")
        self.match(Type.RNBRACK)
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
    def funcvals(self,func):
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
        """
        Maths API
        """
        self.cexternal("sin", ["float"], "float")
        self.cexternal("cos", ["float"], "float")
        self.cexternal("tan", ["float"], "float")
        self.cexternal("asin", ["float"], "float")
        self.cexternal("acos", ["float"], "float")
        self.cexternal("atan", ["float"], "float")
        self.cexternal("atan2", ["float", "float"], "float")
        self.cexternal("sinh", ["float"], "float")
        self.cexternal("cosh", ["float"], "float")
        self.cexternal("tanh", ["float"], "float")
        self.cexternal("exp", ["float"], "float")
        self.cexternal("log", ["float"], "float")
        self.cexternal("log10", ["float"], "float")
        self.cexternal("pow", ["float", "float"], "float")
        self.cexternal("sqrt", ["float"], "float")
        self.cexternal("ceil", ["float"], "float")
        self.cexternal("floor", ["float"], "float")
        self.cexternal("fabs", ["float"], "float")
        self.cexternal("fmod", ["float", "float"], "float")
        self.cexternal("exp2", ["float"], "float")
        self.cexternal("expm1", ["float"], "float")
        self.cexternal("log1p", ["float"], "float")
        self.cexternal("log2", ["float"], "float")
        self.cexternal("cbrt", ["float"], "float")
        self.cexternal("erf", ["float"], "float")
        self.cexternal("erfc", ["float"], "float")
        self.cexternal("hypot", ["float", "float"], "float")
        self.cexternal("lgamma", ["float"], "float")
        self.cexternal("tgamma", ["float"], "float")
        self.cexternal("nearbyint", ["float"], "float")
        self.cexternal("rint", ["float"], "float")
        self.cexternal("round", ["float"], "float")
        self.cexternal("trunc", ["float"], "float")
        
        self.cexternal("strcpy", ["string", "string"], "string")
        self.cexternal("strncpy", ["string", "string", "int"], "string")
        self.cexternal("strcat", ["string", "string"], "string")
        self.cexternal("strncat", ["string", "string", "int"], "string")
        self.cexternal("strcmp", ["string", "string"], "int")
        self.cexternal("strncmp", ["string", "string", "int"], "int")
        self.cexternal("strlen", ["string"], "int")
        self.cexternal("strchr", ["string", "int"], "string")
        self.cexternal("strrchr", ["string", "int"], "string")
        self.cexternal("strstr", ["string", "string"], "string")
        self.cexternal("strtok", ["string", "string"], "string")
        log(self.fname,self.line,"PROGRAM")
        self.line+=1
        self.emitter.headeremit("#include <stdio.h>")
        self.emitter.headeremit("#include <stdint.h>")
        self.emitter.headeremit("#include <stdlib.h>")
        self.emitter.headeremit("#include <string.h>")
        self.emitter.headeremit("""
#include <math.h>
#ifndef _STDBOOL_H
#define _STDBOOL_H 
#define bool        _Bool   
#endif
FILE *fp;
long lSize;
char *buffer;  
int res;
        """)
        self.emitter.headeremit("int main(void) {")
        self.emitter.headeremit("int iterable;")
        
        while self.checkcur(Type.NEWLINE):
            self.line+=1
            self.next()
        while not self.checkcur(Type.EOF):
            self.statement()
        for string in self.strings:
            self.emitter.emit(f"free({string});")
        self.emitter.emit("free(buffer);")
        self.emitter.emit("return 0;")
        self.emitter.emit("}")
        self.emitter.emit(f"""
/*
    This C file was automatically generated by the Rosemary compiler.
    Rosemary is a language transpiled to C. It aims to merge performance with ease-of use. It is Turing complete, partly via its implementation of the `extern` keyword.
    For more information on this programming language see https://github.com/spartanproj/Rosemary
    
    This file was created at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S%z")}.
    {self.fname} -> {self.fname}.c -> {self.fname}.o
*/       """)
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
                failed=False
            elif self.curtok.text in self.floats:
                self.emitter.emitn("printf(\"%" + "f\", (float)(")
                self.expression()
                self.emitter.emit("));")
                failed=False
            elif self.curtok.text in self.ints|self.bools:
                percentafter="ld" if self.curtok.text in self.ints else "d"
                self.emitter.emitn("printf(\"%" + f"{percentafter}\",")
                self.expression()
                self.emitter.emit(");")
                failed=False
                failed=False
            elif self.curtok.text in self.strings:
                self.emitter.emitn("printf(\"%s\",")
                self.emitter.emitn(self.curtok.text)
                self.emitter.emit(");")
                self.next()
                failed=False
            elif self.checkcur(Type.NUMBER):
                self.emitter.emit("printf(\"%ld\",\""+self.curtok.text+"\"\");")
                self.next()
            else:
                print("else")
                funcs=[]
                purelist=[]
                for value in self.funcs:
                    for key,val in value.items():
                        if isinstance(val,list) or key=="ret":
                            pass
                        else:
                            funcs.append({key:(value["ret"])})
                            purelist.append(key)
                failed=True
                for main in funcs:
                    for key,val in main.items():            
                        if self.curtok.text in purelist:
                            try:main[self.curtok.text]
                            except:continue
                            match main[self.curtok.text]:
                                case "int":
                                    self.emitter.emitn(f"printf(\"%" + "d\",")
                                case "float":
                                    self.emitter.emitn(f"printf(\"%" + ".2f\",")
                                case "string":
                                    self.emitter.emitn(f"printf(\"%" + "s\",")
                                case "bool":
                                    self.emitter.emitn(f"printf(\"%d\",")
                            self.functioncall()
                            self.emitter.antiemit(1)
                            self.emitter.emit(");")
                            failed=False
                if failed==True:
                    self.panic("Argument to print is erroneous - "+self.curtok.text)
        elif self.checkcur(Type.IF):
            log(self.fname,self.line,"IF")
            self.next()
            self.emitter.emitn("if(")
            if self.checkpeek(Type.EQEQ) and self.checkcur(Type.STRING):
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
                if self.checkpeek(Type.EQEQ) and self.checkcur(Type.STRING):
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
        elif self.checkcur(Type.bool):
            log(self.fname,self.line,"bool")
            self.next()
            if self.curtok.text not in self.bools:
                self.bools.add(self.curtok.text)
                self.emitter.headeremit("bool " + self.curtok.text + ";")
            self.emitter.emitn(self.curtok.text+"=")
            self.match(Type.IDENT)
            self.match(Type.EQ)
            try:
                bool(self.curtok.text)
            except:
                if self.curtok.text not in self.bools:
                    self.panic("Attempting to assign non-boolean value to boolean variable")
            self.expression()
            self.emitter.emit(";")
        elif self.checkcur(Type.ints):
            log(self.fname,self.line,"ints")
            self.next()
            while self.checkcur(Type.IDENT):
                if self.curtok.text in self.floats or self.curtok.text in self.ints or self.curtok.text in self.strings or self.curtok.text in self.bools:
                    self.panic("Attempting to redeclare variable - "+self.curtok.text)
                self.emitter.emitn("int64_t ")
                self.emitter.emitn(self.curtok.text)
                self.emitter.emit("=0;")
                self.ints.add(self.curtok.text)
                self.next()
                if not self.checkcur(Type.COMMA):
                    break
                self.next()
        elif self.checkcur(Type.bools):
            log(self.fname,self.line,"bools")
            self.next()
            while self.checkcur(Type.IDENT):
                if self.curtok.text in self.floats|self.ints|self.strings|self.bools:
                    self.panic("Attempting to redeclare variable - "+self.curtok.text)
                self.emitter.emitn("bool ")
                self.emitter.emitn(self.curtok.text)
                self.emitter.emit("=false;")
                self.bools.add(self.curtok.text)
                self.next()
                if not self.checkcur(Type.COMMA):
                    break
                self.next()
        elif self.checkcur(Type.floats):
            log(self.fname,self.line,"floats")
            self.next()
            while self.checkcur(Type.IDENT):
                if self.curtok.text in self.floats|self.ints|self.strings|self.bools:
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
                self.emitter.emit( "char *"+self.curtok.text + "=malloc(8192);")
            self.emitter.emitn(f"strcpy({self.curtok.text},")
            self.match(Type.IDENT)
            self.match(Type.EQ)
            try:
                str(self.curtok.text)
            except:
                self.panic("Attempting to assign non-string value to string variable")
            self.matchn(Type.STRING)
            self.emitter.emit(f"\"{self.curtok.text}\");")
            self.next()
        elif self.checkcur(Type.strings):
            log(self.fname,self.line,"strings")
            self.next()
            while self.checkcur(Type.IDENT):
                if self.curtok.text in self.floats|self.ints|self.strings|self.bools:
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
            log(self.fname,self.line,"extern",MED)
            
            self.next()
            self.matchn(Type.STRING)
            # log(self.fname,self.line,"C Injection Warning - "+"`"+self.curtok.text+"`",HIGH)
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
            
            elif self.curtok.text in self.floats|self.ints|self.strings|self.bools:
                log(self.fname,self.line,"reassign")
                self.emitter.emitn(self.curtok.text+"=")
                self.next()
                self.match(Type.EQ)
                self.expression()
                self.emitter.emit(";")
            elif self.checkpeek(Type.LNBRACK):
                self.functioncall()
            else:
                self.panic("Attempting to reassign variable before assignment - "+self.curtok.text)
        elif self.checkcur(Type.input):
            log(self.fname,self.line,"input")
            self.next()
            if self.curtok.text not in self.floats|self.ints|self.strings|self.bools:
                self.panic("Attempting to input into uninitialised variable "+self.curtok.text)
            if self.curtok.text in self.floats:
                self.emitter.emit("if(0 == scanf(\"%" + "f\", &" + self.curtok.text + ")) {")
                self.emitter.emit(self.curtok.text + " = 0;")
                self.emitter.emitn("scanf(\"%")
                self.emitter.emit("*s\");")
                self.emitter.emit("}")
            elif self.curtok.text in self.ints|self.bools:
                percentafter="ld" if self.curtok.text in self.ints else "d"
                self.emitter.emit("if(0 == scanf(\"%" + f"{percentafter}\", &" + self.curtok.text + ")) {")
                self.emitter.emit(self.curtok.text + " = 0;")
                self.emitter.emitn("scanf(\"%")
                self.emitter.emit("*s\");")
                self.emitter.emit("}")
            elif self.curtok.text in self.strings:
                self.emitter.emit("scanf(\"%" + "s\", " + self.curtok.text + ");")
            self.match(Type.IDENT)
        elif self.checkcur(Type.inc):
            pass
        elif self.checkcur(Type.UPTHINGY):
            self.next()
            while self.checkcur!=Type.UPTHINGY:
               match self.curtok.kind:
                    case Type.NEWLINE:
                        self.nl()
                    case Type.UPTHINGY:
                        self.next()
                        break
                    case _:
                        self.next()

        elif self.checkcur(Type.func):
            log(self.fname,self.line,"func definition")
            temp=""
            self.next()
            temp+=" "+(self.curtok.text)
            name=self.curtok.text
            self.next()
            self.match(Type.LNBRACK)
            temp+="("
            args,iters=0,0
            typeslist=[]
            typen=""
            matchto= {
                    "int":self.ints,
                    "float":self.floats,
                    "string":self.strings,
                    "bool":self.bools
                }
            argstofunc=[]
            
            
            while self.curtok.kind in [Type.float,Type.int,Type.string,Type.bool]:
                args+=1
                temp+=(self.curtok.text if self.curtok.kind!=Type.string else "char *"+" ")
                if not self.curtok.kind in [Type.float,Type.int,Type.string,Type.bool]:
                    self.panic(f"Unknown type {self.curtok.text}")
                else:
                    typen=self.curtok.text
                    typeslist+="n" # filler character
                    typeslist[iters]=typen
                    self.next()
                temp+=(" "+self.curtok.text)
                self.matchn(Type.IDENT)
                argstofunc.append({self.curtok.text:typen})
                matchto[typen].add(self.curtok.text)
                self.next()
                if self.checkcur(Type.COMMA):
                    self.match(Type.COMMA)
                    temp+=(",")
                else:
                    break
                iters+=1
            
            self.match(Type.RNBRACK)
            self.match(Type.ARROW)
            if self.curtok.kind not in [Type.int, Type.float, Type.string,Type.bool]:
                self.panic(f"Wrong return type {self.curtok.text}")
            else: 
                type=self.curtok.kind
                self.currentfunctionreturn=type
                typetext=self.curtok.text
                self.emitter.emitn(self.curtok.text if self.curtok.text!="string" else "char *")
                self.emitter.emitn(temp)
                self.next()
            self.funcs.append({f"{name}":f"{args}","argtype":typeslist,"ret":typetext})
            self.match(Type.LBRACK)
            self.emitter.emit("){")
            self.nl()
            self.infunc=True
            oldint=set(self.ints)
            oldfloats=set(self.floats)
            oldbool=set(self.bools)
            oldstring=set(self.strings)
            while not self.checkcur(Type.RBRACK):
                self.statement()
                self.emitter.emit("")
            self.infunc=False
            
            copyb=set(self.bools)
            for i in copyb:
                if i not in oldbool:
                    self.bools.remove(i)
            
            copyc=set(self.floats)
            for i in copyc:
                if i not in oldfloats:
                    self.floats.remove(i)

            copyd=set(self.ints)
            for i in copyd:
                if i not in oldint:
                    self.ints.remove(i)

            copye=set(self.strings)
            for i in copye:
                if i not in oldstring:
                    self.strings.remove(i)

            for k in argstofunc:
                for varname,typex in k.items():
                    matchto[typex].remove(varname)
            self.match(Type.RBRACK)
            self.emitter.emit("}")
        elif self.checkcur(Type.ret) and self.infunc:
            log(self.fname,self.line,"return")
            self.emitter.emitn("return ")
            self.match(Type.ret)
            match self.currentfunctionreturn:
                case Type.string:
                    if self.curtok.kind not in [Type.STRING, Type.IDENT]:
                        self.panic(f"Wrong return type")
                case Type.int:
                    if self.curtok.kind not in [Type.NUMBER, Type.IDENT]:
                        self.panic(f"Wrong return type")
                case Type.float:
                    if self.curtok.kind not in [Type.NUMBER, Type.IDENT]:
                        self.panic(f"Wrong return type")
                case Type.bool:
                    if self.curtok.kind not in [Type.NUMBER, Type.IDENT]:
                        self.panic(f"Wrong return type")
                case _:
                    self.panic("Not quite sure how we ended up here. Um maybe file a Github issue?")
            self.emitter.emit(self.curtok.text+";")
            self.next()
        else:
            self.panic("Invalid statement \""+self.curtok.text+"\"")
        self.nl()
    def strcmp(self):
        log(self.fname,self.line,"strcmp")
        prevtok=self.curtok.text
        self.next()
        self.emitter.emitn("!strcmp(\"")
        self.emitter.emitn(prevtok+"\"")
        self.emitter.emitn(",")
        self.match(Type.EQEQ)
        self.matchn(Type.IDENT)
        self.emitter.emitn(self.curtok.text+")")
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
            failed=True
            funcs=[]
            purelist=[]
            for value in self.funcs:
                for key,val in value.items():
                    if isinstance(val,list) or key=="ret":
                        pass
                    else:
                        funcs.append({key:(value["ret"])})
                        purelist.append(key)
            for main in funcs:
                    for key,val in main.items():                
                        if self.curtok.text in purelist:
                            self.functioncall()
                            failed=False
            if self.curtok.text in self.floats|self.ints|self.strings|self.bools:
                self.emitter.emitn(self.curtok.text)
                self.next()
                           
            elif not failed:
                pass
            else:
                self.panic("Referencing variable before assignment: " + self.curtok.text)
            
            
        else:
            self.panic("Unexpected token at "+self.curtok.text)
    def nl(self):
        self.match(Type.NEWLINE)
        self.line+=1
        while self.checkcur(Type.NEWLINE):
            self.next()
            self.line+=1
        