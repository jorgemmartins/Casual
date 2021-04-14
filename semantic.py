#############################################################
###########Casual Language Semantic Verifier#################
#############################################################
###################Jorge Martins fc51033#####################
#############################################################

from ast import *
RETURN_CODE = "$ret"


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
        if actual != expected:
            raise TypeError(f"Return esperava {expected} mas recebe {actual}")
    elif type(ast) == IfStatement:
        print("IF")
    elif type(ast) == WhileStatement:
        print("WHILE")
    elif type(ast) == VarDeclaration:
        print("VARDECL")
    elif type(ast) == VarAssignment:
        print("ASSIGN")
