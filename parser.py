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

flno = 0
lnomap = []
lno = 1
alno = 0

# Used for error checking
defstructlist = {'scalar'}
usedstructlist = set()
deffunclist = set()
funcdict = {}
usedfunclist = set()

# Used for error checking
varlist = set()
structdict = {}
# Saved for each function
vardict = {}

start = "prog"

def prepare_next_function():
    global lnomap, alno
    statements.clear()
    lnomap = []
    alno = 0
    varlist.clear()
    vardict.clear()

def checkvar(var):
    if var not in varlist:
        raise Exception("Variable '"+ var +"' used without initialization, at line number "+ str(lno))
    return vardict[var]

def checktype(var, typ):
    if checkvar(var) != typ:
        raise Exception("Type Error: Variable '"+ var +"' expected to be '"+ typ +"', but got '"+ vardict[var] +"' instead, at line number "+ str(lno))

def checkfield(var, field):
    typ = checkvar(var)
    if typ[-1] == '*':
        raise Exception("Type Error: Variable '"+ var +"' expected to be a structure, but got a structure pointer ('"+ typ +"') instead, at line number "+ str(lno))
    if typ == 'scalar':
        raise Exception("Type Error: Tried to access a field of a scalar variable '"+ var+"' at line number "+str(lno))
    if field not in structdict[typ][1]:
        raise Exception("Type Error: '"+ var +"' is not a field of structure '"+ typ +"', at line number "+ str(lno))
    return structdict[typ][0][field]

def checkptrfield(var, field):
    typ = checkvar(var)
    if typ[-1] != '*':
        raise Exception("Type Error: Variable '"+ var +"' expected to be a structure pointer, but got a structure ('"+ typ +"') instead, at line number "+ str(lno))
    typ = typ[:-1]
    if typ == 'scalar':
        raise Exception("Type Error: Tried to access a field of a scalar pointer '"+ var+"' at line number "+str(lno))
    if field not in structdict[typ][1]:
        raise Exception("Type Error: '"+ var +"' is not a field of structure '"+ typ +"', at line number "+ str(lno))
    return structdict[typ][0][field]
    
def param_to_string(lst):
    op = '('
    l = len(lst)
    if l>0:
        op = op + lst[0]
    for ind in range(1,l):
        op = op + ', ' + lst[ind]
    return op + ')'

def clean_statements():
    lno = 0
    print(lnomap)
    for s in statements:
        if s[0] == 'IF':
            s[2] = lnomap[s[2]-flno]
        elif s[0] == 'GOT':
            s[1] = lnomap[s[1]-flno]
        print(lno, s)
        lno = lno+1
    return statements


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
    p[0] = ['scalar', [p[2], p[1], p[3]]]
    if p[1][0] == 'VAR':
        checktype(p[1][1], 'scalar')
    if p[3][0] == 'VAR':
        checktype(p[3][1], 'scalar')

def p_lhs(p):
    '''lhs : "*" VARNAME
           | VARNAME "-" ">" VARNAME
           | VARNAME "." VARNAME'''
    if p[1] == '*':
        # print("PTR")
        p[0] = [checkvar(p[2][1]) + '*', ['PTR', p[2]]]
    elif p[2] == '-':
        # print("FLP")
        p[0] = [checkptrfield(p[1][1], p[4][1]), ['FLP', p[1], p[4]]]
    else:
        # print("FLD")
        p[0] = [checkfield(p[1][1], p[3][1]), ['FLD', p[1], p[3]]]
    
def p_rhs(p):
    '''rhs : boolexp
           | lhs
           | VARNAME
           | "&" VARNAME
           | NUMBER'''
    if len(p)==3:
        p[0] = [checkvar(p[2][1])+"*", ['ADR', p[2]]]
    elif p[1][0] == 'NUM':
        p[0] = ['scalar', p[1]]
    elif p[1][0] == 'VAR':
        p[0] = [checkvar(p[1][1]), p[1]]
    else:
        p[0] = p[1]
    # print(p[0][0])

def p_var_dec(p):
    '''vardec : VARNAME SPACES list
              | VARNAME "*" SPACES list'''
    if len(p) == 5:
        typ = p[1][1] + '*'
        lst = p[4]
    else:
        typ = p[1][1]
        lst = p[3]
    if varlist.intersection(lst):
        raise Exception("Redeclaration of variable/s "+str(varlist.intersection(lst))+" at line number "+str(lno))
    usedstructlist.add(typ)
    for elem in lst:
        vardict[elem] = typ
    varlist.update(lst)

def p_stmt(p):
    '''stmt : vardec
            | lhs space "=" space rhs
            | VARNAME space "=" space rhs
            | READ SPACES VARNAME
            | GOTO SPACES NUMBER
            | CALL SPACES VARNAME funcargs
            | IF SPACES boolexp SPACES GOTO SPACES NUMBER
            | IF SPACES VARNAME SPACES GOTO SPACES NUMBER'''
    if len(p) == 2:
        return
    elif p[3] == '=':
        if p[1][0] == 'VAR':
            p[1] = [checkvar(p[1][1]), p[1]]
        if p[1][0] != p[5][0]:
            raise Exception("Type Mismatch: LHS type - '"+p[1][0]+"', RHS type - '"+p[5][0]+"' on assignment statement at line "+str(lno))
        p[0] = ['ASG', p[1][1], p[5][1]]
    elif p[1] == 'read':
        checktype(p[3][1], 'scalar')
        p[0] = ['INP', p[3]]
    elif p[1] == 'goto':
        if p[3][1] != int(p[3][1]):
            raise Exception("Line numbers should be integers")
        p[0] = ['GOT', int(p[3][1])]
    elif p[1] == 'call':
        p[0] = ['CAL', p[3][1], p[4][1]]
        usedfunclist.add(p[0][1]+param_to_string(p[4][0]))
    else:
        if p[7][1] != int(p[7][1]):
            raise Exception("Line numbers should be integers")
        if p[3][0] == 'VAR':
            checktype(p[3][1], 'scalar')
            p[0] = ['IF', p[3], int(p[7][1])]
        else:
            p[0] = ['IF', p[3][1], int(p[7][1])]
    # print(lno,p[0])
    global alno
    alno += 1

    print(lno, p[0])
    statements.append(p[0])
    
def p_tac(p):
    '''tac : nl MAINCODE ":"
           | tac stmtnl stmt'''
    # if p[2] != ':':
    #     print(lno, p[3])
    #     statements.append(p[3])
    # | stmt
    # elif p[1] != '':
    #     # print(lno, p[1])
    #     lnomap.append(0)
    #     statements.append(p[1])

# def p_tac_nl(p):
#     r'tacnl : tac NEWLINE'
#     global lno
#     lno += p[2]
#     for _ in range(p[2]):
#         lnomap.append(alno)

def p_nl(p):
    r'nl : NEWLINE'
    global lno
    lno += p[1]
    p[0] = p[1]

def p_stmt_nl(p):
    r'stmtnl : NEWLINE'
    global lno
    lno += p[1]
    for _ in range(p[1]):
        lnomap.append(alno)

def p_funcbody(p):
    '''funcbody : stmt
                | funcbody stmtnl stmt'''
    if len(p) != 2:
        print(lno, p[3])
        statements.append(p[3])
    else:
        print(lno, p[1])
        lnomap.append(0)
        statements.append(p[1])

def p_arg_list(p):
    '''arglist : VARNAME
               | arglist space "," space VARNAME'''
    if len(p) == 2:
        p[0] = [[checkvar(p[1][1])], [p[1][1]]]
    else:
        p[1][0].append(checkvar(p[5][1]))
        p[1][1].append(p[5][1])
        p[0] = p[1]

def p_func_args(p):
    '''funcargs : "(" space ")"
                | "(" space arglist space ")"'''
    if len(p) == 4:
        p[0] = [[], []]
    else:
        p[0] = p[3]

def p_param_list(p):
    '''paramlist : VARNAME SPACES VARNAME
                 | paramlist space "," space VARNAME SPACES VARNAME'''
    if len(p) == 4:
        p[0] = [[p[1][1]], {p[3][1]:p[1][1]}, {p[3][1]}]
    elif p[7][1] not in p[1][2]:
        p[1][1][p[7][1]] = p[5][1]
        p[1][2].add(p[7][1])
        p[1][0].append(p[5][1])
        p[0] = [p[1][0], p[1][1], p[1][2]]
    else:
        raise Exception("Same variable ("+p[7]+") occurs mulltiple times in Function Parameter List at line number "+str(lno))

def p_func_params(p):
    '''funcparams : "(" space ")"
                  | "(" space paramlist space ")"'''
    if len(p) == 4:
        p[0] = []
    else:
        p[0] = p[3][0]
        vardict.update(p[3][1])
        varlist.update(p[3][2])
    global flno
    flno = lno

def p_func(p):
    '''func : FUNCS ":"
            | func nl VARNAME funcparams spnl "{" spnl funcbody spnl "}"
            | func nl VARNAME funcparams spnl "{" spnl "}"'''
    if len(p) != 3:
        p[3][1] = p[3][1]+param_to_string(p[4])
        if p[3][1] in deffunclist:
            # raise Exception("Redeclaration of function '"+p[2][1]+"' at line number "+str(lno - p[10]))
            raise Exception("Redeclaration of function '"+p[3][1]+"' at line number "+str(flno))
        deffunclist.add(p[3][1])
        funcdict[p[3][1]] = [p[4], vardict, clean_statements()]
    elif usedstructlist - defstructlist:
        raise Exception("Structure/s " + str(usedstructlist - defstructlist) + " used without definition")
    prepare_next_function()

def p_space_nl(p):
    '''spnl : space
            | nl'''
    if p[1] == '':
        p[0] = 0
    else:
        p[0] = p[1]

def p_list(p):
    '''list : VARNAME space
            | list "," space VARNAME space'''
    if len(p) == 3:
        p[0] = {p[1][1]}
    else:
        p[0] = p[1]
        if p[4][1] in p[0]:
            raise Exception("Duplicate variable or field "+p[4][1]+" at line number "+str(lno))
        p[0].add(p[4][1])

def p_boxlist(p):
    '''blist : "[" spnl list spnl "]"
             | "[" spnl "]"'''
    p[0] = []
    if len(p) == 6:
        p[0] = p[3]

def p_dec_list(p):
    '''declist : VARNAME SPACES list
               | VARNAME "*" SPACES list
               | declist nl VARNAME SPACES list
               | declist nl VARNAME "*" SPACES list'''
    if len(p) < 6:
        elemtype = p[1][1]
        elemdict = {}
        elemlist = set()
        global flno
        flno = lno
    else:
        elemtype = p[3][1]
        elemdict = p[1][0]
        elemlist = p[1][1]
    usedstructlist.add(elemtype)
    if len(p)%2 == 1:
        elemtype = elemtype + '*'
    elemset = p[len(p)-1]
    if elemlist.intersection(elemset):
        raise Exception("Redeclaration of variable/s or field/s "+str(elemlist.intersection(elemset))+" at line number "+str(lno))
    elemlist.update(elemset)
    for elem in elemset:
        elemdict[elem] = elemtype
    p[0] = [elemdict, elemlist]
    
def p_structs(p):
    '''structs : spnl STRT ":" nl
              | structs VARNAME space "{" spnl declist spnl "}" nl
              | structs VARNAME space "{" spnl "}" nl'''
    if len(p) == 10:
        if p[2][1] in defstructlist:
            raise Exception("Redectaration of structure '"+p[2][1]+"' at line number "+str(flno - p[5]))
        structdict[p[2][1]] = p[6]
        defstructlist.add(p[2][1])
    elif len(p) == 8:
        if p[2][1] in defstructlist:
            raise Exception("Redectaration of structure '"+p[2][1]+"' at line number "+str(lno - p[5] - p[7]))
        structdict[p[2][1]] = [{}, set()]
        defstructlist.add(p[2][1])

def p_prog(p):
    '''prog : structs func tac'''

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

    # parser.parse(s)
    try:
        parser.parse(s)
    except Exception as X:
        print(X)
        exit()

    # print(lnomap)
    # lno = 0
    for s in statements:
        if s[0] == 'IF':
            s[2] = lnomap[s[2]]
        elif s[0] == 'GOT':
            s[1] = lnomap[s[1]]
        # lno += 1
        # print(lno, s)
    if usedfunclist - deffunclist:
        print("Function/s " + str(usedfunclist - deffunclist) + " used without definition")
        exit()
    print('Structures')
    print(defstructlist)
    print(usedstructlist)
    print(structdict)
    print('Functions')
    print(deffunclist)
    print(usedfunclist)
    break # type: ignore