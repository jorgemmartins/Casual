#############################################################
###################Casual Language Lexer#####################
#############################################################
###################Jorge Martins fc51033#####################
#############################################################
import ply.lex as lex

# Reserved keywords
keywords = {
    # Types
    'Int': 'INT',
    'Float': 'FLOAT',
    'String': 'STRING',
    'Boolean': 'BOOLEAN',
    'Void': 'VOID',
    # Conditional statements
    'if': 'IF',
    'else': 'ELSE',
    # Definition/declaration
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
