#############################################################
###############Casual Language Compiler######################
#############################################################
###################Jorge Martins fc51033#####################
#############################################################

from ast import *

dict_types = {"INT": "i32", "FLOAT": "float",
              "STRING": "i8*", "BOOLEAN": "i1", "VOID": "void"}


var_types = {}


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
        for decl_or_def in ast:
            compile(decl_or_def, emitter)
        return emitter.get_code()
    elif type(ast) == Decl:
        definition = "declare " + \
            dict_types[ast.return_type]+" @" + ast.id + "("
        i = 0
        for var in ast.args:
            definition += dict_types[var.var_type] + \
                " " + emitter.get_pointer_name(var.id)
            if i != len(ast.args)-1:
                definition += ", "
            i += 1
            var_types[emitter.get_pointer_name(var.id)] = (var.var_type, "arg")
        emitter << definition + ") #1"
        return
    elif type(ast) == Def:
        definition = "define " + \
            dict_types[ast.return_type]+" @" + ast.id + "("
        i = 0
        for var in ast.args:
            definition += dict_types[var.var_type] + \
                " " + emitter.get_pointer_name(var.id)
            if i != len(ast.args)-1:
                definition += ", "
            i += 1
            var_types[emitter.get_pointer_name(var.id)] = (var.var_type, "arg")
        emitter << definition + ") #0 {"
        for stmt in ast.block.statements:
            compile(stmt, emitter)
        emitter << "}"
    elif type(ast) == ReturnStatement:
        if not ast.ret_value:
            emitter << f"   ret void"
        else:
            registo = compile(ast.ret_value, emitter)
            ptype = None
            try:
                ptype = var_types[registo]
            except:
                ptype = ast.ret_value.literal_type
            if len(ptype) == 2:
                ptype = ptype[0]
            emitter << f"   ret {dict_types[ptype]} {registo}"

        return
    elif type(ast) == IfStatement:
        return
    elif type(ast) == WhileStatement:
        return
    elif type(ast) == VarDeclaration:
        pname = emitter.get_pointer_name(ast.id)
        registo = compile(ast.expr, emitter)
        var_types[pname] = ast.var_type
        if ast.var_type == "STRING":
            id = emitter.get_id()
            str_name = f"@.casual_str_{id}"
            str_decl = f"""{str_name} = private unnamed_addr constant [{len(registo)+1} x i8] c"{registo}\\00" """
            emitter.lines.insert(0, str_decl)
            emitter << f"   {pname} = alloca {dict_types[ast.var_type]}"
            emitter << f"   store {dict_types[ast.var_type]} getelementptr inbounds ([{len(registo)+1} x i8],[{len(registo)+1} x i8]* {str_name}, i64 0, i64 0), {dict_types[ast.var_type]}* {pname}"
        else:
            emitter << f"   {pname} = alloca {dict_types[ast.var_type]}"
            emitter << f"   store {dict_types[ast.var_type]} {registo}, {dict_types[ast.var_type]}* {pname}"
        return
    elif type(ast) == VarAssignment:
        pname = emitter.get_pointer_name(ast.id)
        ptype = var_types[pname]
        registo = compile(ast.expr, emitter)
        if ptype == "STRING":
            id = emitter.get_id()
            str_name = f"@.casual_str_{id}"
            str_decl = f"""{str_name} = private unnamed_addr constant [{len(registo)+1} x i8] c"{registo}\\00" """
            emitter.lines.insert(0, str_decl)
            emitter << f"   store {dict_types[ptype]} getelementptr inbounds ([{len(registo)+1} x i8],[{len(registo)+1} x i8]* {str_name}, i64 0, i64 0), {dict_types[ptype]}* {pname}"
            return
        else:
            emitter << f"   store {dict_types[ptype]} {registo}, {dict_types[ptype]}* {pname}"
        return
    elif type(ast) == BinOp:
        r1 = compile(ast.expr, emitter)
        r2 = compile(ast.expr2, emitter)
        rr = "%" + emitter.get_id()
        ptype = None
        try:
            ptype = var_types[r1]
        except:
            ptype = ast.expr.literal_type

        if ast.op == "+":
            if ptype == "INT":
                emitter << f"   {rr} = add nsw {dict_types[ptype]} {r1}, {r2}"
                var_types[rr] = "INT"
            else:
                emitter << f"   {rr} = fadd {dict_types[ptype]} {r1}, {r2}"
                var_types[rr] = "FLOAT"
        elif ast.op == "-":
            if ptype == "INT":
                emitter << f"   {rr} = sub nsw {dict_types[ptype]} {r1}, {r2}"
                var_types[rr] = "INT"
            else:
                emitter << f"   {rr} = fsub {dict_types[ptype]} {r1}, {r2}"
                var_types[rr] = "FLOAT"
        elif ast.op == "*":
            if ptype == "INT":
                emitter << f"   {rr} = mul nsw {dict_types[ptype]} {r1}, {r2}"
                var_types[rr] = "INT"
            else:
                emitter << f"   {rr} = fmul {dict_types[ptype]} {r1}, {r2}"
                var_types[rr] = "FLOAT"
        elif ast.op == "/":
            if ptype == "INT":
                emitter << f"   {rr} = sdiv {dict_types[ptype]} {r1}, {r2}"
                var_types[rr] = "INT"
            else:
                emitter << f"   {rr} = fdiv {dict_types[ptype]} {r1}, {r2}"
                var_types[rr] = "FLOAT"
        elif ast.op == "%":
            emitter << f"   {rr} = srem {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "INT"
        elif ast.op == ">":
            aux = "%" + emitter.get_id()
            if ptype == "INT":
                emitter << f"   {rr} = icmp sgt {dict_types[ptype]} {r1}, {r2}"
            else:
                emitter << f"   {rr} = fcmp ogt {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "BOOLEAN"
        elif ast.op == "<":
            if ptype == "INT":
                emitter << f"   {rr} = icmp slt {dict_types[ptype]} {r1}, {r2}"
            else:
                emitter << f"   {rr} = fcmp olt {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "BOOLEAN"
        elif ast.op == ">=":
            if ptype == "INT":
                emitter << f"   {rr} = icmp sge {dict_types[ptype]} {r1}, {r2}"
            else:
                emitter << f"   {rr} = fcmp oge {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "BOOLEAN"
        elif ast.op == "<=":
            if ptype == "INT":
                emitter << f"   {rr} = icmp sle {dict_types[ptype]} {r1}, {r2}"
            else:
                emitter << f"   {rr} = fcmp ole {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "BOOLEAN"
        elif ast.op == "<=":
            if ptype == "INT":
                emitter << f"   {rr} = icmp sle {dict_types[ptype]} {r1}, {r2}"
            else:
                emitter << f"   {rr} = fcmp ole {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "BOOLEAN"
        elif ast.op == "==":
            if ptype == "INT" or ptype == "BOOLEAN":
                emitter << f"   {rr} = icmp seq {dict_types[ptype]} {r1}, {r2}"
            else:
                emitter << f"   {rr} = fcmp oeq {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "BOOLEAN"
        elif ast.op == "!=":
            if ptype == "INT" or ptype == "BOOLEAN":
                emitter << f"   {rr} = icmp ne {dict_types[ptype]} {r1}, {r2}"
            else:
                emitter << f"   {rr} = fcmp une {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "BOOLEAN"
        elif ast.op == "&&":
            emitter << f"   {rr} = and {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "BOOLEAN"
        elif ast.op == "||":
            emitter << f"   {rr} = or {dict_types[ptype]} {r1}, {r2}"
            var_types[rr] = "BOOLEAN"
        return rr
    elif type(ast) == UnOp:
        r1 = compile(ast.expr, emitter)
        rr = "%" + emitter.get_id()
        emitter << f"   {rr} = xor i1 {r1}, true"
        var_types[rr] = "BOOLEAN"
        return rr
    elif type(ast) == ExprVar:
        vname = ast.id
        reg = "%" + emitter.get_id()
        pname = emitter.get_pointer_name(vname)
        ptype = var_types[pname]
        if len(ptype) == 2:
            return pname
        var_types[reg] = ptype
        emitter << f"   {reg} = load {dict_types[ptype]}, {dict_types[ptype]}* {pname}"
        return reg
    elif type(ast) == ExprLiteral:
        if ast.literal_type == "BOOLEAN":
            if ast.literal == True:
                return "1"
            else:
                return "0"
        else:
            return str(ast.literal)
    elif type(ast) == FuncInvocation:
        return
    elif type(ast) == FuncArg:
        return
    elif type(ast) == IndexAccess:
        return
