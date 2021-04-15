#############################################################
###################Casual Language Parser####################
#############################################################
###################Jorge Martins fc51033#####################
#############################################################
import sys
import ply.yacc as yacc
from lexer import *
from ast import *
from semantic import verify, Context

file = open(sys.argv[1], 'r')
input_data = file.read()

#############################
###########PARSER############
#############################
precedence = (
    ('left', 'LT', 'GT', 'LE', 'GE', 'OR', 'AND', 'EQ', 'NEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'NOT'),
)


def p_program(t):
    '''program : declaration program
                | definition program
                | empty'''
    if len(t) == 3 and t[2]:
        t[0] = [t[1]] + t[2]
    elif len(t) == 3 and not t[2]:  # So we wont get an annoying None in the AST
        t[0] = [t[1]]


def p_declaration(t):
    'declaration : DECL ID LPAREN function_args RPAREN COLON return_type'
    t[0] = Decl(t[2], t[4], t[7])


def p_definition(t):
    'definition : DEF ID LPAREN function_args RPAREN COLON return_type block'
    t[0] = Def(t[2], t[4], t[7], t[8])


def p_function_args(t):
    '''function_args : ID COLON var_type function_args
                    | COMMA function_args
                    | empty'''
    if len(t) == 5:
        # im gonna do a list of tuples with the structure
        if t[4]:
            t[0] = [FuncArg(t[1], t[3])] + t[4]
        else:
            t[0] = [FuncArg(t[1], t[3])]
    elif len(t) == 3:
        t[0] = t[2]
    else:
        t[0] = []


def p_return_type(t):
    '''return_type : INT
                    | FLOAT
                    | STRING
                    | BOOLEAN
                    | VOID
                    | LBRACKET var_type RBRACKET'''
    if len(t) == 2:
        t[0] = t[1].upper()
    else:
        t[0] = '['+t[2]+']'


def p_block(t):
    'block : LBRACE recursive_statement RBRACE'
    t[0] = Block(t[2])


def p_recursive_statement(t):
    '''recursive_statement : statement recursive_statement
                            | empty'''
    if len(t) == 3 and t[2]:
        t[0] = [t[1]] + t[2]
    elif len(t) == 3 and not t[2]:
        t[0] = [t[1]]


def p_statement(t):
    '''statement : return_statement
            | expression SEMI
            | if_statement
            | while_statement
            | variable_declaration
            | variable_assignment'''
    t[0] = t[1]


def p_return_statement(t):  # return statement
    '''return_statement : RETURN ret_value SEMI'''
    t[0] = ReturnStatement(t[2])


def p_ret_value(t):  # return value
    '''ret_value : expression
                | empty'''
    if len(t) == 2:
        t[0] = t[1]


def p_if_statement(t):  # if statement
    '''if_statement : IF expression block else_statement'''
    t[0] = IfStatement(t[2], t[3], t[4])


def p_else_statement(t):  # else
    '''else_statement : ELSE block
                | empty'''
    if len(t) == 3:
        t[0] = t[2]
    else:
        t[0] = None


def p_while_stmt(t):  # while statement
    '''while_statement : WHILE expression block'''
    t[0] = WhileStatement(t[2], t[3])


def p_variable_declaration(t):  # variable declaration
    '''variable_declaration : ID COLON var_type EQUALS expression SEMI'''
    t[0] = VarDeclaration(t[1], t[3], t[5])


def p_variable_assignment(t):  # variable assignment
    '''variable_assignment : ID EQUALS expression SEMI'''
    t[0] = VarAssignment(t[1], t[3])


def p_var_type(t):
    '''var_type : FLOAT
                | INT
                | STRING
                | BOOLEAN
                | LBRACKET var_type RBRACKET'''
    if len(t) == 2:
        t[0] = t[1].upper()
    else:
        t[0] = '[' + t[2] + ']'


def p_expression(t):
    '''expression : expression_binary_operation
                    | expression_variable
                    | expression_unary_operation
                    | expression_literal
                    | function_invocation
                    | index_access'''
    t[0] = t[1]


def p_expression_binary_operation(t):
    '''expression_binary_operation : expression PLUS expression
                                | expression MINUS expression
                                | expression TIMES expression
                                | expression DIVIDE expression
                                | expression MOD expression
                                | expression AND expression
                                | expression OR expression
                                | expression LT expression
                                | expression GT expression
                                | expression LE expression
                                | expression GE expression
                                | expression EQ expression
                                | expression NEQ expression'''
    t[0] = BinOp(t[2], t[1], t[3])


def p_expression_variable(t):
    '''expression_variable : ID'''
    t[0] = ExprVar(t[1])


def p_expression_unary_operation(t):
    '''expression_unary_operation : NOT expression'''
    t[0] = UnOp(t[1], t[2])


def p_expression_literal(t):
    '''expression_literal : LBRACE array_literal RBRACE
                | INT_LITERAL
                | FLOAT_LITERAL
                | STRING_LITERAL
                | BOOLEAN_LITERAL'''
    if type(t[1]) == int:
        t[0] = ExprLiteral('INT', t[1])
    elif type(t[1]) == float:
        t[0] = ExprLiteral('FLOAT', t[1])
    elif t[1] == "{":
        t[0] = ExprLiteral('ARRAY', t[2])
    elif type(t[1]) == str:
        t[0] = ExprLiteral('STRING', t[1])
    elif type(t[1]) == bool:
        t[0] = ExprLiteral('BOOLEAN', t[1])


def p_array_literal(t):
    '''array_literal : expression array_literal
                    | COMMA array_literal
                    | empty'''
    if len(t) == 3 and t[1] != ',':
        if t[2]:
            t[0] = [(t[1])] + t[2]
        else:
            t[0] = [(t[1])]
    elif len(t) == 3 and t[1] == ',':
        t[0] = t[2]
    else:
        t[0] = []


def p_function_invocation(t):
    '''function_invocation : ID LPAREN func_invocation_args RPAREN'''
    t[0] = FuncInvocation(t[1], t[3])


def p_func_invocation_args(t):
    '''func_invocation_args : expression func_invocation_args
                            | COMMA func_invocation_args
                            | empty'''
    if len(t) == 3 and t[1] != ',':
        if t[2]:
            t[0] = [(t[1])] + t[2]
        else:
            t[0] = [(t[1])]
    elif len(t) == 3 and t[1] == ',':
        t[0] = t[2]
    else:
        t[0] = []


def p_index_access(t):
    '''index_access : ID index_access_aux'''
    t[0] = IndexAccess(t[1], t[2])


def p_index_access_aux(t):
    '''index_access_aux : LBRACKET expression RBRACKET
                        | LPAREN func_invocation_args RPAREN LBRACKET expression RBRACKET'''
    if len(t) == 4:
        t[0] = t[2]
    else:
        t[0] = (t[2], t[5])


def p_empty(t):
    '''empty : '''
    pass


def p_error(t):
    print("Syntax error at '%s' on line '%d' and column '%d'" %
          (t.value, t.lexer.lineno, find_column(input_data, t)))


parser = yacc.yacc()
ast = parser.parse(input_data)

verify(Context(), ast)
