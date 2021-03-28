#############################################################
#############Casual Language Lexer and Parser################
#############################################################
################Jorge Martins fc51033########################
#############################################################
import ply.yacc as yacc
import ply.lex as lex

# Reserved keywords
keywords = (
    # Types
    'INT', 'FLOAT', 'STRING', 'BOOLEAN',
    # Conditional
    'IF', 'ELSE',
    # Misc
    'RETURN', 'DEF'
)

tokens = (
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
    'SEMI', 'COLON',

    # Comments
    'POUND',

    # Values
    'INTEGER', 'BOOL', 'FLOAT', 'STRING', 'NAME'
)

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

# Comments
t_POUND = r'#'

# Values
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_BOOL = r'true|false'
t_STRING = r'\"([^\\\"]|\\.)*\"'


def t_INTEGER(t):
    r'\d((_|\d)*\d)?'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_FLOAT(t):
    r'(\d*[.])?\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Float value too large %d", t.value)
        t.value = 0.0
    return t


# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):  # need to add column + line
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
