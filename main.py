#############################################################
#############Casual Language Lexer and Parser################
#############################################################
################Jorge Martins fc51033########################
#############################################################
import sys
import ply.yacc as yacc
import ply.lex as lex

file = open(sys.argv[1], 'r')
input_data = file.read()

# Reserved keywords
keywords = {
    # Types
    'Int': 'INT',
    'Float': 'FLOAT',
    'String': 'STRING',
    'Boolean': 'BOOLEAN',
    'void': 'VOID',
    # Conditional
    'if': 'IF',
    'else': 'ELSE',
    'def': 'DEF',
    'decl': 'DECL',
    # Loop
    'while': 'WHILE',
    # Misc
    'return': 'RETURN'
}

tokens = list(keywords.values()) + [
    # Operators
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'OR', 'AND', 'NOT',
    'LT', 'GT', 'GE', 'LE',
    'EQ', 'NEQ',

    # Assignment
    'EQUALS',

    # Delimiters
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'SEMI', 'COLON', 'COMMA',

    # Values
    'ID', 'FLOAT_LITERAL', 'INT_LITERAL', 'BOOLEAN_LITERAL', 'STRING_LITERAL'
]

# Operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_OR = r'\|\|'
t_AND = r'&&'
t_NOT = r'!'
t_LT = r'<'
t_GT = r'>'
t_GE = r'>='
t_LE = r'<='
t_EQ = r'=='
t_NEQ = r'!='

# Assignment
t_EQUALS = r'='

# Delimiters
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMI = r';'
t_COLON = r':'
t_COMMA = r'\,'


def t_FLOAT_LITERAL(t):
    r'(\d*)?[.]\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Float value too large %d", t.value)
        t.value = 0.0
    return t


def t_INT_LITERAL(t):
    r'\d((_|\d)*\d)?'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_STRING_LITERAL(t):
    r'\"([^\\\"]|\\.)*\"'
    try:
        t.value = str(t.value)[1:-1]  # removing the ""
    except ValueError:
        print("Not a string %s", t.value)
        t.value = ""
    return t


def t_BOOLEAN_LITERAL(t):
    r'true|false'
    try:
        t.value = bool(t.value)
    except ValueError:
        print("Not a boolean %b", t.value)
        t.value = ""
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value, 'ID')    # Check for reserved words
    return t


def t_COMMENT(t):
    r'\#.*'
    pass  # ignore this token


# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


# Build the lexer
lexer = lex.lex()

# dictionary of names
names = {}


#############################
######PROGRAM SKELETON#######
#############################
def p_program(t):
    '''program : declaration program
                | definition program
                | empty'''

    if len(t) == 3:
        t[0] = ('program', t[1], t[2])
    else:
        t[0] = ()


def p_declaration(t):
    'declaration : DECL ID LPAREN function_args RPAREN COLON return_type'
    t[0] = ('declaration', t[1], t[2], t[3],
            ('functions_args', t[4]), t[5], t[6], t[7])


def p_definition(t):
    'definition : DEF ID LPAREN function_args RPAREN COLON return_type block'
    t[0] = ('definition', t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8])


def p_function_args(t):
    '''function_args : ID COLON var_type function_args
                    | COMMA function_args
                    | empty'''
    if len(t) == 5:
        # im gonna do a list of tuples with the structure
        if t[4]:
            t[0] = [(t[1], t[2], t[3])] + t[4]
        else:
            t[0] = [(t[1], t[2], t[3])]
    elif len(t) == 3:                     # (ID,COLON,type)
        t[0] = t[2]
    else:
        t[0] = t[1]


def p_return_type(t):
    '''return_type : INT
                    | FLOAT
                    | STRING
                    | BOOLEAN
                    | VOID'''
    t[0] = ('return_type', t[1])


def p_block(t):
    'block : LBRACE recursive_statement RBRACE'
    t[0] = ('block', t[2])


def p_recursive_statement(t):
    '''recursive_statement : statement recursive_statement
                            | empty'''
    t[0] = t[1]

#############################
###########STATEMENTS########
#############################


def p_statement(t):
    '''statement : return_statement
            | expression SEMI
            | if_statement
            | while_statement
            | variable_declaration
            | variable_assignment'''
    t[0] = ('statement', t[1])


def p_return_statement(t):  # return statement
    '''return_statement : RETURN ret_value SEMI'''
    t[0] = ('return_statement', t[1], t[2])


def p_ret_value(t):  # return value
    '''ret_value : expression
                | empty'''
    t[0] = t[1]


def p_if_statement(t):  # if statement
    '''if_statement : IF expression block else_statement'''
    t[0] = ('if_statement', t[1], t[2], t[3], t[4])


def p_else_statement(t):  # else
    '''else_statement : ELSE block
                | empty '''
    if len(t) == 3:
        t[0] = ('else_statement', t[1], t[2])
    else:
        t[0] = ('else_statement', t[1])


def p_while_stmt(t):  # while statement
    '''while_statement : WHILE expression block'''
    t[0] = ('while_statement', t[1], t[2], t[3])


def p_variable_declaration(t):  # variable declaration
    '''variable_declaration : ID COLON var_type EQUALS expression SEMI'''
    t[0] = ('variable_declaration', t[3], t[1], t[5])


def p_variable_assignment(t):  # variable assignment
    '''variable_assignment : ID EQUALS expression SEMI'''
    t[0] = ('variable_assignment', t[1], t[3])


def p_var_type(t):
    '''var_type : FLOAT
                | INT
                | STRING
                | BOOLEAN'''
    t[0] = t[1]


#############################
##########EXPRESSIONS########
#############################
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
    t[0] = ('binary_operation', t[2], t[1], t[3])


def p_expression_variable(t):
    '''expression_variable : ID'''
    t[0] = t[1]


def p_expression_unary_operation(t):
    '''expression_unary_operation : NOT expression
                                | MINUS expression'''
    t[0] = ('unary_operation', t[1], t[2])


def p_expression_literal(t):
    '''expression_literal : FLOAT_LITERAL
                | INT_LITERAL
                | STRING_LITERAL
                | BOOLEAN_LITERAL'''
    if type(t[1]) == int:
        t[0] = ('INT', t[1])
    elif type(t[1]) == float:
        t[0] = ('FLOAT', t[1])
    elif type(t[1]) == str:
        t[0] = ('STRING', t[1])
    elif type(t[1]) == bool:
        t[0] = ('BOOLEAN', t[1])


def p_function_invocation(t):
    '''function_invocation : ID LPAREN func_invocation_args RPAREN'''
    t[0] = ('function_invocation', t[1], t[2], t[3])


def p_func_invocation_args(t):
    '''func_invocation_args : ID func_invocation_args
                            | COMMA func_invocation_args
                            | empty'''
    if len(t) == 2:
        t[0] = ('func_invocation_args', t[1], t[2])
    else:
        t[0] = ('func_invocation_args', t[1])


def p_index_access(t):
    '''index_access : ID index_access_aux'''
    t[0] = ('index_access', t[1]) + t[2]


def p_index_access_aux(t):
    '''index_access_aux : LBRACKET expression RBRACKET
                        | LPAREN func_invocation_args RPAREN LBRACKET expression RBRACKET'''


def p_empty(t):  # empty rule
    '''empty : '''
    t[0] = None


def p_error(t):
    print("Syntax error at '%s' on line '%d' and column '%d'" %
          (t.value, t.lexer.lineno, find_column(input_data, t)))


parser = yacc.yacc()
ast = parser.parse(input_data)
print(ast)
