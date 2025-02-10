def perform_andersens_analysis(struct_dict, var_dict, stmt_lst):
    ptr_dict = {}
    for var, typ in var_dict.items():
        if contains_pointer(typ, struct_dict):
            ptr_dict[var] = {}
            if typ[-1] == '*':
                ptr_dict[var]['*'] = set()
                if typ[-2] == '*':
                    continue
                for field, field_typ in struct_dict[typ[:-1]][0].items():
                    if field_typ[-1] == '*':
                        ptr_dict[var]['*'+field] = set()
            else:
                for field, field_typ in struct_dict[typ][0].items():
                    if field_typ[-1] == '*':
                        ptr_dict[var]['.'+field] = set()
    
    new_stmt_lst = get_stmts(struct_dict, stmt_lst)

    count = 0
    change = True
    while change:
        change = False
        print("Iteration -", count)
        print(ptr_dict)
        for (lhs, rhs) in new_stmt_lst:
            # print(lhs, rhs)
            pointers = get_pointers(ptr_dict, rhs)
            pointees = get_pointees(ptr_dict, lhs)
            for ptes in pointees:
                for ptrs in pointers:
                    for key, val in ptrs.items():
                        init_len = len(ptr_dict[ptes][key])
                        ptr_dict[ptes][key].update(val)
                        change = change or init_len!=len(ptr_dict[ptes][key])
        # ptr_dict_copy.clear()
        count += 1
    print("Iteration -", count, "(final)")
    # print(ptr_dict)
    for key, val in ptr_dict.items():
        print(key,":")
        for key2, val2 in val.items():
            print('\t',key2, '-', val2)


def get_pointees(ptr_dict, lhs):
    match lhs[0]:
        case 'VAR':
            return {lhs[1]}
        case 'PTR':
            return ptr_dict[lhs[1]]['*']
        case 'FLP':
            return ptr_dict[lhs[1]]['*'+lhs[2]]
        case 'FLD':
            return ptr_dict[lhs[1]]['.'+lhs[2]]

def get_pointers(ptr_dict, rhs):
    match rhs[0]:
        case 'ADR':
            ptrs = {'*' : rhs[1]}
            if rhs[1] in ptr_dict.keys():
                for key, val in ptr_dict[rhs[1]].items():
                    if key[0] == '.':
                        ptrs['*'+key[1:]] = val
            return [ptrs]
        case 'VAR':
            return [ptr_dict[rhs[1]]]
        case 'PTR':
            ptrs = []
            for ptr in ptr_dict[rhs[1]]['*']:
                ptrs.append(ptr_dict[ptr])
            return ptrs
        case 'FLP':
            ptrs = []
            for ptr in ptr_dict[rhs[1]]['*'+rhs[2]]:
                ptrs.append(ptr_dict[ptr])
            return ptrs
        case 'FLD':
            ptrs = []
            for ptr in ptr_dict[rhs[1]]['.'+rhs[2]]:
                ptrs.append(ptr_dict[ptr])
            return ptrs

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
        if stmt[0] != 'ASG':
            continue
        if contains_pointer(stmt[1][0], struct_dict):
            new_stmt_lst.append([stmt[1][1], stmt[2][1]])
    return new_stmt_lst