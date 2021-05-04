#############################################################
###############Casual Language Compiler######################
#############################################################
###################Jorge Martins fc51033#####################
#############################################################

from ast import *

dict_types = {"INT": "i32", "FLOAT": "float",
              "STRING": "i8*", "BOOLEAN": "i8", "VOID": "void"}


class Emitter(object):
    def __init__(self):
        self.count = 0
        self.lines = []

    def get_count(self):
        self.count += 1
        return self.count

    def get_id(self):
        id = self.get_count()
        return f"cas_{id}"

    def __lshift__(self, v):
        self.lines.append(v)

    def get_code(self):
        return "\n".join(self.lines)

    def get_pointer_name(self, n):
        return f"%pont_{n}"


def compile(ast, emitter=None):

    if type(ast) == list and len(ast) > 0 and (type(ast[0]) == Decl or type(ast[0]) == Def):

        emitter = Emitter()

        emitter << "declare i32 @printf(i8*, ...) #1"

        emitter << "define i32 @main() #0 {"

        emitter << "   ret i32 0"
        emitter << "}"

        for decl_or_def in ast:
            compile(decl_or_def, emitter)
        return emitter.get_code()
    elif type(ast) == Decl:
        return
    elif type(ast) == Def:
        definition = "define " + \
            dict_types[ast.return_type]+" @" + ast.id + "("
        for i in range(0, len(ast.args)):
            definition += dict_types[ast.args[i].var_type] + " %" + str(i)
            if i != len(ast.args)-1:
                definition += ", "
        emitter << definition + ") #0 {"
        for stmt in ast.block.statements:
            compile(stmt, emitter)
        emitter << "}"
    elif type(ast) == ReturnStatement:
        if not ast.ret_value:
            emitter << "ret void"
        return
    elif type(ast) == IfStatement:
        return
    elif type(ast) == WhileStatement:
        return
    elif type(ast) == VarDeclaration:
        return
    elif type(ast) == VarAssignment:
        return
    elif type(ast) == BinOp:
        return
    elif type(ast) == UnOp:
        return
    elif type(ast) == ExprVar:
        return
    elif type(ast) == ExprLiteral:
        return
    elif type(ast) == FuncInvocation:
        return
    elif type(ast) == FuncArg:
        return
    elif type(ast) == IndexAccess:
        return
