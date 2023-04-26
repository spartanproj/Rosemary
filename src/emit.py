class Emitter:
    def __init__(self,path):
        self.path=path
        self.header=""
        self.code=""
    def emitn(self,code):
        self.code+=code
    def emit(self,code):
        self.code+=code+"\n"
    def headeremit(self,code):
        self.header+=code+"\n"
    def write(self):
        with open(self.path, 'w') as file:
            file.write(self.header+self.code)
    