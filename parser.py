import ply.yacc as yacc
from scanner import tokens

precedence = (
    ('left', 'NUMBER'),
    ('left', 'VARNAME'),
    ('nonassoc', 'LVL1'),
    ('nonassoc', 'LVL2'),
)

#TODO
# list of statements
statements = []
lnomap = [0,]

structlist = set()
defstructlist = {'scalar', 'bool'}
usedstructlist = set()
structdict = {}

funclist = set()
deffunclist = set()
usedfunclist = set()

varlist = set()
vardict = {}

lno = 1
alno = 1

start = "prog"

def checkvar(var):
    if var not in varlist:
        raise Exception("Variable '"+ var +"' used without initialization, at line number "+ str(lno))
    return vardict[var]

def checktype(var, typ):
    if checkvar(var) != typ:
        raise Exception("Type Error: Variable '"+ var +"' expected to be '"+ typ +"', but got '"+ vardict[var] +"' instead, at line number "+ str(lno))

def checkfield(var, field):
    typ = checktype(var)
    if typ[-1] == '*':
        raise Exception("Type Error: Variable '"+ var +"' expected to be a structure, but got a structure pointer ('"+ typ +"') instead, at line number "+ str(lno))
    if field not in structdict[typ][1]:
        raise Exception("Type Error: '"+ var +"' is not a field of structure '"+ typ +"', at line number "+ str(lno))
    return structdict[typ][0][field]

def checkptrfield(var, field):
    typ = checktype(var)
    if typ[-1] != '*':
        raise Exception("Type Error: Variable '"+ var +"' expected to be a structure pointer, but got a structure ('"+ typ +"') instead, at line number "+ str(lno))
    

def p_space(p):
    '''space : %prec LVL1
             | SPACES %prec LVL2'''
    p[0] = ''

def p_bool_op(p):
    '''boolop : space LTE space
              | space GTE space
              | space "<" space
              | space ">" space
              | space "=" "=" space
              | space "!" "=" space'''
    if p[2] == '<=':
        p[0] = 'LTE'
    elif p[2] == '>=':
        p[0] = 'GTE'
    elif p[2] == '<':
        p[0] = 'LT'
    elif p[2] == '>':
        p[0] = 'GT'
    elif p[2] == '=':
        p[0] = 'EQ'
    else:
        p[0] = 'NEQ'

def p_bool_exp(p):
    '''boolexp : VARNAME boolop VARNAME
               | VARNAME boolop NUMBER
               | NUMBER boolop VARNAME
               | NUMBER boolop NUMBER'''
    p[0] = [p[2], p[1], p[3]]
    if p[1][0] == 'VAR':
        checktype(p[1][1], 'scalar')
    if p[3][0] == 'VAR':
        checktype(p[3][1], 'scalar')


def p_lhs(p):
    '''lhs : VARNAME
           | "*" VARNAME
           | VARNAME "-" ">" VARNAME
           | VARNAME "." VARNAME'''
    if len(p) == 2:
        # print("VAR")
        p[0] = [checkvar(p[1][1]), p[1]]
    elif p[1] == '*':
        # print("PTR")
        p[0] = [checkvar(p[2][1]) + '*', ['PTR', p[2]]]
    elif p[2] == '-':
        # print("FLP")
        p[0] = ['FLP', p[1], p[4]]
    else:
        # print("FLD")
        p[0] = ['FLD', p[1], p[3]]
    
def p_rhs(p):
    '''rhs : boolexp
           | lhs
           | "&" VARNAME
           | NUMBER'''
    if len(p)==3:
        p[0] = ['ADR', p[2]]
    else:
        p[0] = p[1]
    # print(p[0][0])

def p_stmt(p):
    '''stmt : lhs space "=" space rhs
            | READ SPACES VARNAME
            | GOTO SPACES NUMBER
            | CALL SPACES VARNAME
            | IF SPACES boolexp SPACES GOTO SPACES NUMBER
            | IF SPACES VARNAME SPACES GOTO SPACES NUMBER'''
    if p[3] == '=':
        p[0] = ['ASG', p[1], p[5]]
    elif p[1] == 'read':
        p[0] = ['INP', p[3]]
    elif p[1] == 'goto':
        if p[3][1] != int(p[3][1]):
            raise Exception("Line numbers should be integers")
        p[0] = ['GOT', int(p[3][1])]
    elif p[1] == 'call':
        p[0] = ['CAL', p[3][1]]
        usedfunclist.add(p[0][1])
    else:
        if p[7][1] != int(p[7][1]):
            raise Exception("Line numbers should be integers")
        p[0] = ['IF', p[3], int(p[7][1])]
        if p[3][0] == 'VAR':
            checktype(p[3][1], 'scalar')
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
    p[0] = p[1]

def p_funcbody(p):
    '''funcbody : stmt
                | funcbody nl stmt'''
    # if p[2] != ':':
    #     print(lno, p[2])
    #     statements.append(p[2])

def p_func(p):
    '''func : FUNCS ":" nl
            | func VARNAME "{" spnl funcbody spnl "}" nl
            | func VARNAME "{" spnl "}" nl'''
    if len(p) == 9:
        if p[2][1] in deffunclist:
            raise Exception("Redectaration of function '"+p[2][1]+"' at line number "+str(lno - p[8]))
        deffunclist.add(p[2][1])
    elif len(p) == 7:
        if p[2][1] in deffunclist:
            raise Exception("Redectaration of function '"+p[2][1]+"' at line number "+str(lno - p[6]))
        deffunclist.add(p[2][1])
    elif usedstructlist - defstructlist:
        raise Exception("Structure/s " + str(usedstructlist - defstructlist) + " used without definition")

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

def p_boxlist(p):
    '''blist : "[" spnl list spnl "]"
             | "[" spnl "]"'''
    p[0] = []
    if len(p) == 6:
        p[0] = p[3]

def p_dec_list(p):
    '''declist : VARNAME space ":" space blist
               | VARNAME "*" space ":" space blist
               | declist spnl "," spnl VARNAME space ":" space blist
               | declist spnl "," spnl VARNAME "*" space ":" space blist'''
    if len(p) < 8:
        elemtype = p[1][1]
        elemdict = {}
        elemlist = set()
    else:
        elemtype = p[5][1]
        elemdict = p[1][0]
        elemlist = p[1][1]
    usedstructlist.add(elemtype)
    if len(p)%2 == 1:
        elemtype = elemtype + '*'
    elemset = set(p[len(p)-1])
    if elemlist.intersection(elemset):
        raise Exception("Redectaration of variable/s or field/s "+str(elemlist.intersection(elemset))+" at line number "+str(lno))
    elemlist.update(elemset)
    for elem in elemset:
        elemdict[elem] = elemtype
    p[0] = [elemdict, elemlist]

def p_lists(p):
    '''structlist : spnl STLT space "=" space blist
       varlist : nl VARLT space "=" space "{" spnl "}"
               | nl VARLT space "=" space "{" spnl declist spnl "}"
       funclist : nl FNLT space "=" space blist'''
    if p[2] == 'structlist':
        structlist.update(p[6])
    elif p[2] == 'funclist':
        funclist.update(p[6])
    elif len(p) == 11:
        vardict.update(p[8][0])
        varlist.update(p[8][1])
    
def p_structs(p):
    '''structs : nl STRT ":" nl
              | structs VARNAME space "{" spnl declist spnl "}" nl
              | structs VARNAME space "{" spnl "}" nl'''
    if len(p) == 10:
        if p[2][1] in defstructlist:
            raise Exception("Redectaration of structure '"+p[2][1]+"' at line number "+str(lno - p[9]))
        structdict[p[2][1]] = p[6]
        defstructlist.add(p[2][1])
    elif len(p) == 8:
        if p[2][1] in defstructlist:
            raise Exception("Redectaration of structure '"+p[2][1]+"' at line number "+str(lno - p[7]))
        structdict[p[2][1]] = [{}, set()]
        defstructlist.update(p[2][1])

def p_prog(p):
    '''prog : structlist varlist funclist structs func tac'''

def p_error(p):
    if p:
        raise Exception("Syntax error at line " + str(lno) +" at '" + str(p.value) + "'")
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
    try:
        parser.parse(s)
    except Exception as X:
        print(X)
        exit()
    print(lnomap)
    lno = 0
    for s in statements:
        if s[0] == 'IF':
            s[2] = lnomap[s[2]]
        elif s[0] == 'GOT':
            s[1] = lnomap[s[1]]
        lno += 1
        # print(lno, s)
    if usedfunclist - deffunclist:
        print("Function/s " + str(usedfunclist - deffunclist) + " used without definition")
        exit()
    print(varlist)
    print(vardict)
    print('Structures')
    print(structlist)
    print(defstructlist)
    print(usedstructlist)
    print(structdict)
    print('Functions')
    print(funclist)
    print(deffunclist)
    print(usedfunclist)
    break