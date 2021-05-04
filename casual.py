import sys
import ply.yacc as yacc
from lexer import *
from ast import *
from parser import parser
from semantic import verify, Context
from compiler import compile


if __name__ == "__main__":

    file = open(sys.argv[1], 'r')
    filename = sys.argv[1].split(".")[-2]
    input_data = file.read()

    ast = parser.parse(input_data)
    verify(Context(), ast)
    llvmcode = compile(ast)
    if llvmcode:
        with open(filename+".ll", "w") as f:
            f.write(llvmcode)
        import subprocess

        r = subprocess.call(
            "llc " + filename + ".ll && clang " + filename +
            ".s -o " + filename + " && ./"+filename,
            shell=True,
        )
