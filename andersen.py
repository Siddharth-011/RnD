def perform_andersens_analysis(struct_dict, var_dict, stmt_lst):
    ptr_dict = {}
    isunk_ptr_dict = {}
    for var, typ in var_dict.items():
        if contains_pointer(typ, struct_dict):
            ptr_dict[var] = {}
            isunk_ptr_dict[var] = False
            if typ[-1] == '*':
                ptr_dict[var]['*'] = set()
            else:
                for field, field_typ in struct_dict[typ][0].items():
                    if field_typ[-1] == '*':
                        ptr_dict[var][field] = set()
    
    new_stmt_lst = get_stmts(struct_dict, stmt_lst)

    count = 0
    change = True
    while change:
        change = False
        print("Iteration -", count)
        print(ptr_dict)
        for (lhs, rhs) in new_stmt_lst:
            # print(lhs, rhs)
            pointees = get_pointees(ptr_dict, rhs, isunk_ptr_dict)
            vars, fld = get_defs(ptr_dict, lhs)
            for var in vars:
                old_len = len(ptr_dict[var][fld])
                ptr_dict[var][fld].update(pointees)
                change = change or (old_len != len(ptr_dict[var][fld]))
        # ptr_dict_copy.clear()
        count += 1
    print("Iteration -", count, "(confirmation)")
    # print(ptr_dict)
    for key, val in ptr_dict.items():
        print(key,":")
        for key2, val2 in val.items():
            print('\t',key2, '-', val2)


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

def get_stmts(struct_dict, stmt_lst):
    new_stmt_lst = []
    for stmt in stmt_lst:
        if stmt[0] == 'ASG':
            if contains_pointer(stmt[1][0], struct_dict):
                new_stmt_lst.append([stmt[1][1], stmt[2][1]])
        # elif stmt[0] == 'MAL':
        #     new_stmt_lst.append([['PTR', stmt[1][1]], ['VAR', '$'+str(stmt[2])]])
        #     var_dict['$'+str(stmt[2])] = 
            #TODO
    return new_stmt_lst