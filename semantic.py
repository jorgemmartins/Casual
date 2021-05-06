#############################################################
###########Casual Language Semantic Verifier#################
#############################################################
###################Jorge Martins fc51033#####################
#############################################################

from ast import *

RETURN_CODE = "$ret"

bool_op = {"&&", "||"}
int_op = {"%"}
int_or_float_bool_op = {"<", ">", "<=", ">="}
int_or_float_num_op = {"+", "-", "*", "/"}
eq_op = {"==", "!="}


class TypeError(Exception):
    pass


class Context(object):
    def __init__(self):
        self.stack = [{}]

    def get_type(self, name):
        for scope in self.stack:
            if name in scope:
                return scope[name]
        raise TypeError(f"Variavel {name} nao esta no contexto")

    def set_type(self, name, value):
        scope = self.stack[0]
        scope[name] = value

    def has_var(self, name):
        for scope in self.stack:
            if name in scope:
                return True
        return False

    def has_var_in_current_scope(self, name):
        return name in self.stack[0]

    def enter_scope(self):
        self.stack.insert(0, {})

    def exit_scope(self):
        self.stack.pop(0)


def verify(ctx: Context, ast):
    # Since my ast is a list of Decl or Def im gonna verify each of those recursively
    if type(ast) == list and len(ast) > 0 and (type(ast[0]) == Decl or type(ast[0]) == Def):
        # Checking if the func declarations/definitions match
        for decl_or_def in ast:
            if type(decl_or_def) == Decl:
                name = decl_or_def.id
                if name == "print":
                    raise TypeError(
                        f"Funcao {name} eh nativa na linguagem e portanto nao pode ser redefinida/redeclarada")
                if ctx.has_var(name):
                    raise TypeError(
                        f"Funcao {name} ja esta definida ou declarada no contexto")
                ctx.set_type(
                    name, ("declaration", decl_or_def.return_type, decl_or_def.args))

            elif type(decl_or_def) == Def:
                name = decl_or_def.id
                if ctx.has_var(name):
                    assinatura = ctx.get_type(name)
                    # Se uma declaracao ja existe ent devemos verificar se o returntype e args batem certo
                    if type(assinatura) is tuple and len(assinatura) == 3 and assinatura[0] == "declaration":
                        decl = ctx.get_type(name)
                        # Verificar o return type
                        if decl_or_def.return_type != assinatura[1]:
                            raise TypeError(
                                f"Tipo de retorno da função {name} diferente da sua declaração")
                        # Verificar os argumentos
                        if len(decl_or_def.args) != len(assinatura[2]):
                            raise TypeError(
                                f"Argumentos da funcao {name} diferentes da declaração")
                        for i in range(len(decl_or_def.args)):
                            if decl_or_def.args[i].id != assinatura[2][i].id or decl_or_def.args[i].var_type != assinatura[2][i].var_type:
                                raise TypeError(
                                    f"Argumentos da funcao {name} diferentes da declaração")
                        ctx.set_type(
                            name, ("definition", decl_or_def.return_type, decl_or_def.args))
                    else:
                        raise TypeError(
                            f"Funcao {name} ja esta definida no contexto")
                else:
                    ctx.set_type(
                        name, ("definition", decl_or_def.return_type, decl_or_def.args))

        # Now we check the functions
        for decl_or_def in ast:
            if type(decl_or_def) == Def:
                verify(ctx, decl_or_def)
    elif type(ast) == Def:
        ctx.enter_scope()
        ctx.set_type(RETURN_CODE, ast.return_type)
        for arg in ast.args:
            ctx.set_type(arg.id, arg.var_type)
        # Bora po body
        ctx.enter_scope()
        for stmt in ast.block.statements:
            verify(ctx, stmt)
        ctx.exit_scope()
        ctx.exit_scope()
    elif type(ast) == ReturnStatement:
        expected = ctx.get_type(RETURN_CODE)
        if ast.ret_value == None and expected == "VOID":
            return
        actual = verify(ctx, ast.ret_value)
        if not actual:
            actual = "VOID"
        # if actual == "ARRAY" and len(ast.ret_value.literal) == 0:
        #     actual = expected
        # if actual == "ARRAY" and len(ast.ret_value.literal) > 0:
        #     tipo_do_array = verify(ctx, ast.ret_value.literal[0])
        #     for i in range(1, len(ast.ret_value.literal)):
        #         if verify(ctx, ast.ret_value.literal[i]) != tipo_do_array:
        #             tipo_do_array
        #             raise TypeError(
        #                 f"Elementos do array devem ter o mesmo tipo")
        #     actual = "[" + tipo_do_array + "]"
        if actual != expected:
            raise TypeError(f"Return esperava {expected} mas recebe {actual}")
    elif type(ast) == IfStatement:
        cond = ast.expr
        if verify(ctx, cond) != "BOOLEAN":
            raise TypeError(f"Condicao do if {cond} nao e boolean")
        for stmt in ast.block.statements:
            verify(ctx, stmt)
        if ast.else_block:
            for stmt in ast.else_block.statements:
                verify(ctx, stmt)
    elif type(ast) == WhileStatement:
        cond = ast.expr
        if verify(ctx, cond) != "BOOLEAN":
            raise TypeError(f"Condicao do while {cond} nao e boolean")
        for stmt in ast.block.statements:
            verify(ctx, stmt)
    elif type(ast) == VarDeclaration:
        name = ast.id
        if ctx.has_var_in_current_scope(name):
            raise TypeError(f"Variavel {name} ja esta definida no contexto")
        assign_value = verify(ctx, ast.expr)
        if assign_value == "ARRAY":
            if len(ast.expr.literal) == 0 and ast.var_type[0] == "[":
                ctx.set_type(name, ast.var_type)
                return
            tipo_do_array = verify(ctx, ast.expr.literal[0])
            for i in range(1, len(ast.expr.literal)):
                if verify(ctx, ast.expr.literal[i]) != tipo_do_array:
                    raise TypeError(
                        f"Elementos do array devem ter o mesmo tipo")
            assign_value = "[" + tipo_do_array + "]"
        if assign_value != ast.var_type:
            raise TypeError(
                f"Valor inicial para a variavel {name} invalido. Esperava {ast.var_type} mas esta a ser atribuido um {assign_value}")
        ctx.set_type(name, ast.var_type)

    elif type(ast) == VarAssignment:
        name = ast.id
        if not ctx.has_var_in_current_scope(name):
            raise TypeError(f"Variavel {name} nao esta definida no contexto")
        var_type = ctx.get_type(name)
        assign_value = verify(ctx, ast.expr)
        # if assign_value == "ARRAY":
        #     if len(ast.expr.literal) == 0 and var_type[0] == "[":
        #         ctx.set_type(name, var_type)
        #         return
        #     tipo_do_array = verify(ctx, ast.expr.literal[0])
        #     for i in range(1, len(ast.expr.literal)):
        #         if verify(ctx, ast.expr.literal[i]) != tipo_do_array:
        #             raise TypeError(
        #                 f"Elementos do array devem ter o mesmo tipo")
        #     assign_value = "[" + tipo_do_array + "]"
        if assign_value != var_type:
            raise TypeError(
                f"Valor inicial para a variavel {name} invalido. Esperava {var_type} mas esta a ser atribuido um {assign_value}")

        ctx.set_type(name, var_type)
    elif type(ast) == BinOp:
        expr_one_type = verify(ctx, ast.expr)
        expr_two_type = verify(ctx, ast.expr2)
        if ast.op in bool_op:
            if expr_one_type != "BOOLEAN":
                raise TypeError(f"A expressao {ast.expr} nao e boolean")
            if expr_two_type != "BOOLEAN":
                raise TypeError(f"A expressao {ast.expr2} nao e boolean")
            return "BOOLEAN"
        if ast.op in int_op:
            if expr_one_type != "INT":
                raise TypeError(f"A expressao {ast.expr} nao e int")
            if expr_two_type != "INT":
                raise TypeError(f"A expressao {ast.expr2} nao e int")
            return "INT"
        if ast.op in eq_op:
            if expr_one_type != "INT" and expr_one_type != "FLOAT" and expr_one_type != "BOOLEAN":
                raise TypeError(
                    f"A expressao {ast.expr} deve ser int, bool ou float")
            if expr_two_type != "INT" and expr_two_type != "FLOAT" and expr_two_type != "BOOLEAN":
                raise TypeError(
                    f"A expressao {ast.expr2} deve ser int, bool ou float")
            if expr_one_type != expr_two_type:
                raise TypeError(
                    f"O tipo das expressoes nao e igual. A expressao {ast.expr} e do tipo {expr_one_type} e a expressao {ast.expr2} e do tipo {expr_two_type}")
            return "BOOLEAN"
        if ast.op in int_or_float_bool_op or ast.op in int_or_float_num_op:
            if expr_one_type != "INT" and expr_one_type != "FLOAT":
                raise TypeError(
                    f"A expressao {ast.expr} deve ser int ou float")
            if expr_two_type != "INT" and expr_two_type != "FLOAT":
                raise TypeError(
                    f"A expressao {ast.expr2} deve ser int ou float")
            if expr_one_type != expr_two_type:
                raise TypeError(
                    f"O tipo das expressoes nao e igual. A expressao {ast.expr} e do tipo {expr_one_type} e a expressao {ast.expr2} e do tipo {expr_two_type}")
            if ast.op in int_or_float_bool_op:
                return "BOOLEAN"
            if ast.op in int_or_float_num_op:
                return expr_one_type
    elif type(ast) == UnOp:
        if ast.op == "!":
            expr_type = verify(ctx, ast.expr)
            if expr_type != "BOOLEAN":
                raise TypeError(f"A expressao {ast.expr} nao e boolean")
            return expr_type
    elif type(ast) == ExprVar:
        name = ast.id
        if not ctx.has_var(name):
            raise TypeError(f"Variavel {name} nao esta definida no contexto")
        return ctx.get_type(name)
    elif type(ast) == ExprLiteral:
        if ast.literal_type == "ARRAY" and len(ast.literal) > 0:
            tipo = verify(ctx, ast.literal[0])
            for i in range(1, len(ast.literal)):
                curr = verify(ctx, ast.literal[i])
                if tipo != curr and curr != "ARRAY":
                    raise TypeError(
                        f"Elementos do array devem ter o mesmo tipo")
            ast.literal_type = "["+verify(ctx, ast.literal[0])+"]"
        return ast.literal_type
    elif type(ast) == FuncInvocation:
        name = ast.id
        if name == "print":
            return
        if not ctx.has_var(name):
            raise TypeError(f"Funcao {name} nao esta definida no contexto")
        func_data = ctx.get_type(name)
        if len(ast.args) != len(func_data[2]):
            raise TypeError(
                f"Numero de argumentos errados para a funcao {name}. Esperava {len(func_data[2])} mas teve {len(ast.args)}")
        for i in range(len(ast.args)):
            expected = verify(ctx, func_data[2][i])
            actual = verify(ctx, ast.args[i])
            # if actual == "ARRAY" and len(ast.args[i].literal) == 0:
            #     actual = expected
            # if actual == "ARRAY" and len(ast.args[i].literal) > 0:
            #     tipo_do_array = verify(ctx, ast.args[i].literal[0])
            #     for j in range(1, len(ast.args[i].literal)):
            #         if verify(ctx, ast.args[i].literal[j]) != tipo_do_array:
            #             raise TypeError(
            #                 f"Elementos do array devem ter o mesmo tipo")
            #     actual = "[" + tipo_do_array + "]"
            if expected != actual:
                raise TypeError(
                    f"Diferente tipo de argumentos para a funcao {name} na posicao {i}. Esperava {expected} mas teve {actual}")
        return func_data[1]
    elif type(ast) == FuncArg:
        return ast.var_type
    elif type(ast) == IndexAccess:
        name = ast.id
        if not ctx.has_var(name):
            raise TypeError(
                f"Variavel/Funcao {name} nao esta definida no contexto")
        tipo = ctx.get_type(name)
        if type(tipo) is tuple:
            tipo = tipo[1]
        if tipo[0] != "[":
            raise TypeError(
                f"Nao eh possivel aceder a um index de um non-array type")
        data = ast.call_type
        if type(data) is tuple:  # chamada a funcao
            tipo = ctx.get_type(name)
            if len(tipo[2]) != len(data[0]):
                raise TypeError(
                    f"Numero de argumentos errados para a funcao {name}. Esperava {len(tipo[2])} mas teve {len(data[0])}")
            for i in range(len(tipo[2])):
                expected = verify(ctx, tipo[2][i])
                actual = verify(ctx, data[0][i])
                # if actual == "ARRAY" and len(data[0][i].literal) == 0:
                #     actual = expected
                # if actual == "ARRAY" and len(data[0][i].literal) > 0:
                #     tipo_do_array = verify(ctx, data[0][i].literal[0])
                #     for j in range(1, len(data[0][i].literal)):
                #         if verify(ctx, data[0][i].literal[j]) != tipo_do_array:
                #             raise TypeError(
                #                 f"Elementos do array devem ter o mesmo tipo")
                #     actual = "[" + tipo_do_array + "]"
                if expected != actual:
                    raise TypeError(
                        f"Diferente tipo de argumentos para a funcao {name} na posicao {i}. Esperava {expected} mas teve {actual}")
            isInt = verify(ctx, data[1])
            if isInt != "INT":
                raise TypeError(
                    f"Indice de acesso ao array deve ser um INT mas foi {isInt}")
            return str(tipo[1])[1:-1]
        else:  # acesso normal
            isInt = verify(ctx, data)
            if isInt != "INT":
                raise TypeError(
                    f"Indice de acesso ao array deve ser um INT mas foi {isInt}")
            return str(tipo)[1:-1]
