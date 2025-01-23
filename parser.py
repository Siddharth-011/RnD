import ply.yacc as yacc
from scanner import tokens

# precedence = (
#     ('right', 'LVL1'),
#     ('right', 'LVL2'),
#     ('right', 'LVL3'),
#     # ('left', ':'),
# )

#TODO
# list of statements
statements = []
lnomap = [0,]
structlist = []
funclist = []
tpyes = ['scalar']

lno = 1
alno = 1

start = "prog"

def p_space(p):
    '''space :
             | space SPACES'''
    p[0] = ''

def p_var(p):
    '''var : VARNAME
           | TMPVARNAME'''
    p[0] = p[1]

def p_elem(p):
    '''elem : space var space
            | space NUMBER space'''
    p[0] = p[2]

def p_bool_exp(p):
    '''boolexp : elem LTE elem
               | elem GTE elem
               | elem "<" elem
               | elem ">" elem
               | elem "=" "=" elem
               | elem "!" "=" elem'''
    if p[2] == '<=':
        # print('LTE')
        p[0] = ['LTE', p[1], p[3]]
    elif p[2] == '>=':
        # print('GTE')
        p[0] = ['GTE', p[1], p[3]]
    elif p[2] == '<':
        # print('LT')
        p[0] = ['LT', p[1], p[3]]
    elif p[2] == '>':
        # print('GT')
        p[0] = ['GT', p[1], p[3]]
    elif p[2] == '=':
        # print('EQ')
        p[0] = ['EQ', p[1], p[4]]
    else:
        # print("NEQ")
        p[0] = ['NEQ', p[1], p[4]]

def p_lhs(p):
    '''lhs : space var space
           | space "*" var space
           | space var "-" ">" var space
           | space var "." var space'''
    if p[2] == '*':
        # print("PTR")
        p[0] = ['PTR', p[3]]
    elif p[3] == '-':
        # print("FLP")
        p[0] = ['FLP', p[2], p[5]]
    elif p[3] == '.':
        # print("FLD")
        p[0] = ['FLD', p[2], p[4]]
    else:
        # print("VAR")
        p[0] = p[2]
    
def p_rhs(p):
    '''rhs : boolexp
           | lhs
           | space "&" var space
           | space NUMBER space'''
    if len(p)==2:
        p[0] = p[1]
    elif p[2] == '&':
        p[0] = ['ADR', p[3]]
    else:
        p[0] = p[2]
    # print(p[0][0])

def p_stmt(p):
    '''stmt : lhs "=" rhs
            | space READ space var space
            | space GOTO space NUMBER space
            | space IF boolexp GOTO space NUMBER space
            | space IF space var space GOTO space NUMBER space'''
    if p[2] == '=':
        p[0] = ['ASG', p[1], p[3]]
    elif p[2] == 'read':
        p[0] = ['INP', p[4]]
    elif p[2] == 'goto':
        p[0] = ['GOT', p[4][1]]
    elif p[4] == 'goto':
        p[0] = ['IF', p[3], p[6][1]]
    else:
        p[0] = ['IF', p[4], p[8][1]]
    # print(lno,p[0])
    global alno
    alno += 1
    
def p_tac(p):
    '''tac : CODE ":"
           | tacnl stmt'''
    if p[2] != ':':
        print(lno, p[2])
        statements.append(p[2])
    # | stmt
    # elif p[1] != '':
    #     # print(lno, p[1])
    #     lnomap.append(0)
    #     statements.append(p[1])

def p_tac_nl(p):
    r'tacnl : tac NEWLINE'
    global lno
    lno += p[2]
    for _ in range(p[2]):
        lnomap.append(alno)

def p_nl(p):
    r'nl : NEWLINE'
    global lno
    lno += p[1]

def p_funcbody(p):
    '''funcbody :
                | funcbody nl stmt'''
    # if p[2] != ':':
    #     print(lno, p[2])
    #     statements.append(p[2])

def p_func(p):
    '''func : FUNCS ":" nl
            | func VARNAME "{" funcbody spnl "}" nl'''

def p_space_nl(p):
    '''spnl : space
            | nl'''

def p_list(p):
    '''list : VARNAME
            | list spnl "," spnl VARNAME'''
    if len(p) == 2:
        p[0] = [p[1][1],]
    else:
        p[0] = p[1]
        p[0].append(p[5][1])

def p_dec_list(p):
    '''declist : VARNAME space ":" space "{" spnl list spnl "}"
               | VARNAME "*" space ":" space "{" spnl list spnl "}"
               | declist spnl "," spnl VARNAME space ":" space "{" spnl list spnl "}"
               | declist spnl "," spnl VARNAME "*" space ":" space "{" spnl list spnl "}"'''
    # if len(p) == 4:
    #     print(p[2], p[3])
    # else:
    #     print(p[3], p[4])

def p_lists(p):
    '''structlist : spnl STLT space "=" space "{" spnl "}"
                  | spnl STLT space "=" space "{" spnl list spnl "}"
       varlist : nl VARLT space "=" space "{" spnl "}"
               | nl VARLT space "=" space "{" spnl declist spnl "}"
       funclist : nl FNLT space "=" space "{" spnl "}"
                | nl FNLT space "=" space "{" spnl list spnl "}"'''
    # if len(p) == 5:
    #     # structlist = p[4]
    #     print(p[4])

# def p_lists(p):
#     '''structlist : spnl STLT ":"
#                   | spnl STLT ":" nl list
#        varlist : nl VARLT ":" spnl "{" spnl "}"
#                | nl VARLT ":" spnl "{" spnl declist spnl "}"
#        funclist : nl FNLT ":"
#                 | nl FNLT ":" list'''
    
def p_struct(p):
    '''struct : nl
              | struct VARNAME space "{" spnl declist spnl "}" nl
              | struct VARNAME "*" space "{" spnl declist spnl "}" nl'''

def p_structs(p):
    '''structs : nl STRT ":" struct'''

def p_prog(p):
    '''prog : structlist varlist funclist structs func tac'''

def p_error(p):
    if p:
        print("Syntax error at line %d" % lno)
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

while True:
    try:
        # s = input('tac > ')
        f = open("test.txt", 'r')
        s = f.read()
    except EOFError:
        break
    # if not s:
    #     continue
    # print(s)
    parser.parse(s)
    print(lnomap)
    lno = 0
    for s in statements:
        if s[0] == 'IF':
            s[2] = lnomap[s[2]]
        elif s[0] == 'GOT':
            s[1] = lnomap[s[1]]
        lno += 1
        print(lno, s)
    break