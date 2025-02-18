import ply.lex as lex

# Tokens
reserved  = {
    'if' : 'IF',
    'goto' : 'GOTO',
    'read' : 'READ',
    'structs' : 'STRT',
    'funcs' : 'FUNCS',
    'main' : 'MAINCODE',
    'call' : 'CALL',
    'malloc' : 'MALLOC'
}
tokens = ['VARNAME', 'NUMBER', 'SPACES', 'NEWLINE', 'LTE', 'GTE', 'STARS'] + list(reserved.values())

literals = ['=', '!', '&', '<', '>', '{', '}', '-', '.', ':', ',', '[', ']', '(', ')']

# t_VARNAME = r'[a-zA-Z]+'
# t_TMPVARNAME = r't[0-9]+'

lno = 1

def t_STARS(t):
    r'\*+'
    # t.value = ['*', t.value]
    return t

def t_VARNAME(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value,'VARNAME')
    if t.type == 'VARNAME':
        t.value = ['VAR', str(t.value)]
    return t

def t_NUMBER(t):
    r'\d+(\.[\d]+)?'
    t.value = ['NUM', float(t.value)]
    return t

def t_NEWLINE(t):
    r'([\s\t]+)?\n[\s\t\n]*'
    t.value = t.value.count("\n")
    global lno
    lno += t.value
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
    raise Exception("Illegal character '"+ str(t.value[0])+ "', at line number "+ str(lno))
    # print("Illegal character '%s'" % t.value[0])
    # t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()