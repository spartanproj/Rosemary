from lex import *
source = "IF+-123 foo*THEN/"
lexer = Lexer(source)
token = lexer.getToken()
while token.type != Type.EOF:
    print(token.type)
    token = lexer.getToken()