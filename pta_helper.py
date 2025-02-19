def get_pta_stmts(struct_dict, stmt_lst):
    new_stmt_lst = []
    for stmt in stmt_lst:
        if stmt[0] == 'ASG':
            if contains_pointer(stmt[1][0], struct_dict):
                new_stmt_lst.append([stmt[1][1], stmt[2][1]])
    return new_stmt_lst

def contains_pointer(struct, struct_dict):
    if struct == 'scalar':
        return False
    elif struct[-1] == '*':
        return True
    else:
        for typ in struct_dict[struct][0].values():
            if typ[-1] == '*':
                return True
    return False

def get_defs(ptr_dict, lhs):
    vars = []
    fld = ''
    match lhs[0]:
        case 'VAR':
            vars.append(lhs[1])
            fld = '*'
        case 'PTR':
            for var in ptr_dict[lhs[1]]['*']:
                vars.append(var)
            fld = '*'
        case 'FLP':
            for var in ptr_dict[lhs[1]]['*']:
                vars.append(var)
            fld = lhs[2]
        case 'FLD':
            vars.append(lhs[1])
            fld = lhs[2]
    return (vars, fld)

def get_pointees(ptr_dict, rhs, isunk_ptr_dict):
    pointees = set()
    match rhs[0]:
        case 'ADR':
            pointees.add(rhs[1])
        case 'VAR':
            for var in ptr_dict[rhs[1]]['*']:
                pointees.add(var)
        case 'PTR':
            for q in ptr_dict[rhs[1]]['*']:
                if isunk_ptr_dict[q]:
                    pointees.add('?')
                for var in ptr_dict[q]['*']:
                    pointees.add(var)
        case 'FLP':
            fld = rhs[2]
            for a in ptr_dict[rhs[1]]['*']:
                if isunk_ptr_dict[a]:
                    pointees.add('?')
                for var in ptr_dict[a][fld]:
                    pointees.add(var)
        case 'FLD':
            for var in ptr_dict[rhs[1]][rhs[2]]:
                pointees.add(var)
        case 'MAL':
            pointees.add(rhs[1])
    return pointees

def get_pointee(ptr_dict, rhs, var_to_set_dict):
    pointee = None
    match rhs[0]:
        case 'ADR':
            # pointees.add(rhs[1])
            pointee = rhs[1]
        case 'VAR':
            pointee = ptr_dict[rhs[1]]['*']
        case 'PTR':
            pointee = ptr_dict[rhs[1]]['*']
            if pointee != None:
                pointee = ptr_dict[pointee]['*']
        case 'FLP':
            pointee = ptr_dict[rhs[1]]['*']
            if pointee != None:
                fld = rhs[2]
                pointee = ptr_dict[pointee][fld]
        case 'FLD':
            pointee = ptr_dict[rhs[1]][rhs[2]]
        case 'MAL':
            pointee = rhs[1]
    return pointee

def get_def(ptr_dict, lhs):
    var = None
    fld = ''
    match lhs[0]:
        case 'VAR':
            var = lhs[1]
            fld = '*'
        case 'PTR':
            var = ptr_dict[lhs[1]]['*']
            fld = '*'
        case 'FLP':
            var = ptr_dict[lhs[1]]['*']
            fld = lhs[2]
        case 'FLD':
            var = lhs[1]
            fld = lhs[2]
    return (var, fld)

def set_dicts(var_dict, struct_dict, ptr_dict, isunk_ptr_dict, enable_unk = True):
    for var, typ in var_dict.items():
        if contains_pointer(typ, struct_dict):
            ptr_dict[var] = {}
            isunk_ptr_dict[var] = enable_unk
            if typ[-1] == '*':
                ptr_dict[var]['*'] = set()
            else:
                for field, field_typ in struct_dict[typ][0].items():
                    if field_typ[-1] == '*':
                        ptr_dict[var][field] = set()