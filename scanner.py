import ply.lex as lex

# Tokens
reserved  = {
    'if' : 'IF',
    'goto' : 'GOTO',
    'read' : 'READ',
    'structlist:' : 'STLT',
    'structs:' : 'STRT',
    'vars:' : 'VARS',
    'funcs:' : 'FUNCS',
    'code:' : 'CODE'
}
tokens = ['VARNAME', 'TMPVARNAME', 'NUMBER', 'SPACES', 'NEWLINE', 'LTE', 'GTE'] + list(reserved.values())

literals = ['=', '*', '!', '&', '<', '>', '{', '}', '-', '.']

# t_VARNAME = r'[a-zA-Z]+'
# t_TMPVARNAME = r't[0-9]+'

def t_TMPVARNAME(t):
    r't[0-9]+'
    t.value = ['TMP', str(t.value)]
    return t

def t_VARNAME(t):
    r'[a-zA-Z]+'
    t.type = reserved.get(t.value,'VARNAME')
    if t.type == 'VARNAME':
        t.value = ['VAR', str(t.value)]
    return t

def t_NUMBER(t):
    r'\d+(\.[\d]+)?'
    t.value = ['NUM', int(t.value)]
    return t

def t_NEWLINE(t):
    r'([\s\t]+)?\n[\s\t\n]*'
    t.value = t.value.count("\n")
    return t

#TODO
def t_SPACES(t):
    r'[\s\t]+'
    return t

t_LTE = r'<='
t_GTE = r'>='

# def t_newline(t):
#     r'[\s\t]*\n+'
#     t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()