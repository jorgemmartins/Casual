class Decl(object):
    def __init__(self, id, args, return_type):
        self.type = "Function Declaration"
        self.id = id
        self.args = args  # List of FuncArg
        self.return_type = return_type

    def __str__(self):
        s = "DECL\n"
        s += "id: " + str(self.id) + "\n"
        s += "".join(["arg: " + str(i) + "\n" for i in self.args])
        s += "return_type: " + str(self.return_type) + "\n"
        return s


class Def(object):
    def __init__(self, id, args, return_type, block):
        self.type = "Function Definition"
        self.id = id
        self.args = args  # List of FuncArg
        self.return_type = return_type
        self.block = block

    def __str__(self):
        s = "DEF\n"
        s += "id: " + str(self.id) + "\n"
        s += "".join(["arg:" + str(i) + "\n" for i in self.args])
        s += "return_type: " + str(self.return_type) + "\n"
        s += str(self.block) + "\n"
        return s


class FuncArg(object):
    def __init__(self, id, var_type):
        self.type = "FUNC_ARGS"
        self.id = id
        self.var_type = var_type

    def __str__(self):
        s = "(id: " + str(self.id) + ","
        s += "var_type: " + str(self.var_type) + ")"
        return s


class Block(object):
    def __init__(self, statements):
        self.type = "Block"
        self.statements = statements  # List of statement

    def __str__(self):
        s = "BLOCK\n"
        s += "".join(["stmt: " + str(i) + "\n" for i in self.statements])
        return s


class ReturnStatement(object):
    def __init__(self, ret_value):
        self.type = "RET_STMT"
        self.ret_value = ret_value  # List of statement

    def __str__(self):
        s = "Return " + str(self.ret_value)
        return s


class IfStatement(object):
    def __init__(self, expr, block, else_block):
        self.type = "IF_STMT"
        self.expr = expr  # List of statement
        self.block = block
        self.else_block = else_block

    def __str__(self):
        s = "If " + str(self.expr) + " then: \n"
        s += str(self.block)
        if self.else_block:
            s += "Else: \n"
            s += str(self.else_block)
        return s


class WhileStatement(object):
    def __init__(self, expr, block):
        self.type = "WHILE_STMT"
        self.expr = expr
        self.block = block

    def __str__(self):
        s = "While " + str(self.expr) + "\n"
        s += str(self.block)
        return s


class VarDeclaration(object):
    def __init__(self, id, var_type, expr):
        self.type = "VAR_DECL"
        self.id = id
        self.var_type = var_type
        self.expr = expr

    def __str__(self):
        s = str(self.id) + ":" + \
            str(self.var_type) + " = " + str(self.expr) + "\n"
        return s


class VarAssignment(object):
    def __init__(self, id, expr):
        self.type = "VAR_ASSIGN"
        self.id = id
        self.expr = expr

    def __str__(self):
        s = str(self.id) + " = " + str(self.expr) + "\n"
        return s


class BinOp(object):
    def __init__(self, op, expr, expr2):
        self.type = "BIN_OP"
        self.op = op
        self.expr = expr
        self.expr2 = expr2

    def __str__(self):
        s = str(self.expr) + str(self.op) + str(self.expr2)
        return s


class UnOp(object):
    def __init__(self, op, expr):
        self.type = "Un_OP"
        self.op = op
        self.expr = expr

    def __str__(self):
        s = str(self.op) + str(self.expr)
        return s


class ExprVar(object):
    def __init__(self, id):
        self.type = "EXPR_VAR"
        self.id = id

    def __str__(self):
        s = str(self.id)
        return s


class ExprLiteral(object):
    def __init__(self, literal_type, literal):
        self.type = "EXPR_LIT"
        self.literal_type = literal_type
        self.literal = literal

    def __str__(self):
        s = str(self.literal)
        return s


class FuncInvocation(object):
    def __init__(self, id, args):
        self.type = "FUNC_CALL"
        self.id = id
        self.args = args

    def __str__(self):
        s = "CALL " + str(self.id) + "("
        for i in range(len(self.args)):
            s += "arg:" + str(self.args[i])
            if i != len(self.args)-1:
                s += ", "
        s += ")\n"
        return s


class IndexAccess(object):
    def __init__(self, id, call_type):
        self.type = "INDEX_ACCESS"
        self.id = id
        self.call_type = call_type

    def __str__(self):

        s = "array access: "+str(self.id)
        if type(self.call_type) is tuple:
            s += "("
            for i in range(len(self.call_type[0])):
                s += "arg:" + str(self.call_type[0][i])
                if i != len(self.call_type[0])-1:
                    s += ", "
            s += ")"
            s += "["+str(self.call_type[1])+"]"
        else:
            s += "["+str(self.call_type)+"]"
        return s
