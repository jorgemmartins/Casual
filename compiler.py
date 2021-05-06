#############################################################
###############Casual Language Compiler######################
#############################################################
###################Jorge Martins fc51033#####################
#############################################################

from ast import *
import re

dict_types = {"INT": "i32", "FLOAT": "double",
              "STRING": "i8*", "BOOLEAN": "i1", "VOID": "void"}


var_types = {}

func_types = {}

array_size = {}


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
        emitter << "declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #1"
        for decl_or_def in ast:
            func_types["@" + decl_or_def.id] = decl_or_def.return_type

        for decl_or_def in ast:
            compile(decl_or_def, emitter)
        return emitter.get_code()
    elif type(ast) == Decl:
        # this is commented cause llvm does not let declaration and definition of same func
        # definition = "declare " + \
        #     dict_types[ast.return_type]+" @" + ast.id + "("
        # i = 0
        # for var in ast.args:
        #     definition += dict_types[var.var_type] + \
        #         " " + emitter.get_pointer_name(var.id)
        #     if i != len(ast.args)-1:
        #         definition += ", "
        #     i += 1
        #     var_types[emitter.get_pointer_name(var.id)] = (var.var_type, "arg")
        # emitter << definition + ") #1"
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
                try:
                    ptype = func_types["@"+registo]
                except:
                    ptype = ast.ret_value.literal_type
            if len(ptype) == 2:
                ptype = ptype[0]
            emitter << f"   ret {dict_types[ptype]} {registo}"

        return
    elif type(ast) == IfStatement:
        registo = compile(ast.expr, emitter)
        rr = "%" + emitter.get_id()
        label1 = "%" + emitter.get_id()
        label2 = "%" + emitter.get_id()
        label3 = "%" + emitter.get_id()
        emitter << f"   {rr} = icmp ne i1 {registo}, 0"
        if ast.else_block:
            emitter << f"   br i1 {rr}, label {label1}, label {label2}"
        else:
            emitter << f"   br i1 {rr}, label {label1}, label {label3}"

        emitter << f"{label1[1:]}:"
        for stmt in ast.block.statements:
            compile(stmt, emitter)
        emitter << f"   br label {label3}"
        if ast.else_block:
            emitter << f"{label2[1:]}:"
            for stmt in ast.else_block.statements:
                compile(stmt, emitter)
        emitter << f"   br label {label3}"
        emitter << f"{label3[1:]}:"
        return
    elif type(ast) == WhileStatement:
        label1 = "%" + emitter.get_id()
        label2 = "%" + emitter.get_id()
        label3 = "%" + emitter.get_id()
        emitter << f"   br label {label1}"
        emitter << f"{label1[1:]}:"  # verificacao da guarda
        registo = compile(ast.expr, emitter)
        rr = "%" + emitter.get_id()
        emitter << f"   {rr} = icmp ne i1 {registo}, 0"
        emitter << f"   br i1 {rr}, label {label2}, label {label3}"
        emitter << f"{label2[1:]}:"
        for stmt in ast.block.statements:
            compile(stmt, emitter)
        emitter << f"   br label {label1}"
        emitter << f"{label3[1:]}:"
        return
    elif type(ast) == VarDeclaration:
        pname = emitter.get_pointer_name(ast.id)
        registo = compile(ast.expr, emitter)
        var_types[pname] = ast.var_type
        if ast.var_type == "STRING":
            emitter << f"   {pname} = alloca {dict_types[ast.var_type]}"
            if len(registo) == 2:
                emitter << f"   store {dict_types[ast.var_type]} getelementptr inbounds ([{registo[1]} x i8],[{registo[1]} x i8]* {registo[0]}, i64 0, i64 0), {dict_types[ast.var_type]}* {pname}"
            else:
                emitter << f"   store {dict_types[ast.var_type]} {registo}, {dict_types[ast.var_type]}* {pname}"
        elif ast.var_type[0] == "[":
            aux = ast.var_type.replace("[", "")
            aux = aux.replace("]", "")
            rr = "%" + emitter.get_id()
            emitter << f"   {rr} = alloca [{registo[1]} x {dict_types[aux]}]"
            emitter << f"   {pname} = bitcast [{registo[1]} x {dict_types[aux]}]* {rr} to i8*"
            array_size[pname] = registo[1]
            emitter << f"   call void @llvm.memcpy.p0i8.p0i8.i64(i8* {pname}, i8* bitcast ([{registo[1]} x {dict_types[aux]}]* {registo[0]} to i8*), i64 {4*registo[1]}, i1 false)"
        else:
            emitter << f"   {pname} = alloca {dict_types[ast.var_type]}"
            emitter << f"   store {dict_types[ast.var_type]} {registo}, {dict_types[ast.var_type]}* {pname}"
        return
    elif type(ast) == VarAssignment:
        pname = emitter.get_pointer_name(ast.id)
        ptype = var_types[pname]
        registo = compile(ast.expr, emitter)
        if ptype == "STRING":
            if len(registo) == 2:
                emitter << f"   store {dict_types[ptype]} getelementptr inbounds ([{registo[1]} x i8],[{registo[1]} x i8]* {registo[0]}, i64 0, i64 0), {dict_types[ptype]}* {pname}"
            else:
                emitter << f"   store {dict_types[ptype]} {registo}, {dict_types[ptype]}* {pname}"
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
            try:
                ptype = func_types["@"+r1]
            except:
                ptype = ast.expr.literal_type
        if len(ptype) == 2:
            ptype = ptype[0]

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
                emitter << f"   {rr} = icmp eq {dict_types[ptype]} {r1}, {r2}"
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
        if ptype[0] == "[":
            ptype = ptype.replace("[", "")
            ptype = ptype.replace("]", "")
        emitter << f"   {reg} = load {dict_types[ptype]}, {dict_types[ptype]}* {pname}"
        return reg
    elif type(ast) == ExprLiteral:
        if ast.literal_type == "BOOLEAN":
            if ast.literal == True:
                return "1"
            else:
                return "0"
        elif ast.literal_type == "STRING":
            id = emitter.get_id()
            str_name = f"@.casual_str_{id}"
            str_decl = f"""{str_name} = private unnamed_addr constant [{len(ast.literal)+1} x i8] c"{ast.literal}\\00" """
            emitter.lines.insert(0, str_decl)
            return (str_name, len(ast.literal)+1)
        elif ast.literal_type[0] == "[":
            id = emitter.get_id()
            str_name = f"@.casual_arr_{id}"
            aux = ast.literal_type.replace("[", "")
            aux = aux.replace("]", "")
            str_decl = f""" {str_name} = private unnamed_addr constant[{len(ast.literal)} x {dict_types[aux]}]["""
            i = 0
            for pos in ast.literal:
                r1 = compile(pos, emitter)
                if aux == "STRING":
                    str_decl += f"{dict_types[aux]} {r1[0]}"
                else:
                    str_decl += f"{dict_types[aux]} {r1}"
                if i != len(ast.literal)-1:
                    str_decl += ", "
                i += 1
            str_decl += "]"
            emitter.lines.insert(0, str_decl)
            return (str_name, len(ast.literal))
        else:
            return str(ast.literal)
    elif type(ast) == FuncInvocation:
        if ast.id == "print":
            _printaux(emitter, ast.args[0])
        else:
            nreg = "%" + emitter.get_id()
            line = f"""   {nreg} = call {dict_types[func_types["@"+ast.id]]} {"@"+ast.id}("""
            i = 0
            for arg in ast.args:
                r1 = compile(arg, emitter)
                ptype = None
                try:
                    ptype = var_types[r1]
                except:
                    try:
                        ptype = func_types["@"+r1]
                    except:
                        ptype = arg.literal_type
                if len(ptype) == 2:
                    ptype = ptype[0]
                line += f"{dict_types[ptype]} {r1}"
                if i != len(ast.args)-1:
                    line += ", "
                i += 1
            emitter << line + ")"
            var_types[nreg] = func_types["@"+ast.id]
            return nreg
        return
    elif type(ast) == IndexAccess:
        nreg = "%" + emitter.get_id()
        ptype = None
        try:
            ptype = var_types[emitter.get_pointer_name(ast.id)]
        except:
            ptype = func_types["@"+ast.id]
        if len(ptype) == 2:
            ptype = ptype[0]
        if ptype[0] == "[":
            ptype = ptype.replace("[", "")
            ptype = ptype.replace("]", "")
        index = compile(ast.call_type, emitter)
        rr = "%" + emitter.get_id()
        rr2 = "%" + emitter.get_id()
        emitter << f"   {rr} = bitcast i8* {emitter.get_pointer_name(ast.id)} to [{array_size[emitter.get_pointer_name(ast.id)]}  x {dict_types[ptype]}]*"
        emitter << f"   {rr2} = getelementptr inbounds [{array_size[emitter.get_pointer_name(ast.id)]} x {dict_types[ptype]}], [{array_size[emitter.get_pointer_name(ast.id)]} x  {dict_types[ptype]}]* {rr}, i64 0, i64 {index}"
        emitter << f"   {nreg} = load {dict_types[ptype]}, {dict_types[ptype]}* {rr2}"
        var_types[nreg] = ptype
        return nreg


def _printaux(emitter, val):
    id = emitter.get_id()
    str_name = f"@.casual_str_{id}"
    nreg = "%" + emitter.get_id()
    reg = compile(val, emitter)
    ptype = None
    try:
        ptype = var_types[reg]
    except:
        try:
            ptype = func_types["@"+reg]
        except:
            ptype = val.literal_type
    if len(ptype) == 2:
        ptype = ptype[0]
    if ptype == "STRING":
        str_decl = f"""   {str_name} = private unnamed_addr constant [4 x i8] c"%s\\0A\\00" """
        emitter.lines.insert(0, str_decl)
        if len(reg) == 2:
            emitter << f"""   {nreg} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* {str_name}, i64 0, i64 0), [{reg[1]} x i8]* {reg[0]})"""
        else:
            emitter << f"""   {nreg} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* {str_name}, i64 0, i64 0), i8* {reg})"""
    elif ptype == "INT":
        str_decl = f"""   {str_name} = private unnamed_addr constant [4 x i8] c"%d\\0A\\00" """
        emitter.lines.insert(0, str_decl)
        emitter << f"""   {nreg} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* {str_name}, i64 0, i64 0), i32 {reg})"""
    elif ptype == "FLOAT":
        str_decl = f"""   {str_name} = private unnamed_addr constant [4 x i8] c"%f\\0A\\00" """
        emitter.lines.insert(0, str_decl)
        emitter << f"""   {nreg} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* {str_name}, i64 0, i64 0), double {reg})"""
    elif ptype == "BOOLEAN":
        str_decl = f"""   {str_name} = private unnamed_addr constant [4 x i8] c"%d\\0A\\00" """
        emitter.lines.insert(0, str_decl)
        emitter << f"""   {nreg} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* {str_name}, i64 0, i64 0), i1 {reg})"""
