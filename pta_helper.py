from helper import *

def get_fspta_stmts(struct_dict, stmt_lst, lb = False):
    new_stmt_lst = [stmt_lst[0]]

    counter_lst = [None]*(len(stmt_lst)+1)
    counter_lst[0] = 0
    counter_lst[-2] = len(counter_lst)-2
    counter_lst[-1] = len(counter_lst)-1

    counter = 1
    new_stmt_counter = 1
    counter_to_stmt = {0:0}
    stmt_to_counter = {0:0}
    for stmt in stmt_lst[1:-1]:
        match stmt[0]:
            case 'ASG':
                check = contains_pointer(stmt[1][0], struct_dict)
                lhs = stmt[1][1]
                rhs = stmt[2][1]
                if check or (lb and ((lhs[0] == 'FLP') or (rhs[0] in ['FLP', 'PTR']))):
                    # if lb:
                    #     new_stmt_lst.append(['ASG', lhs, rhs, check])
                    # else:
                    #     new_stmt_lst.append(['ASG', lhs, rhs])
                    new_stmt_lst.append(['ASG', lhs, rhs, check])
                    
                    counter_lst[counter] = counter
                    counter_to_stmt[counter] = new_stmt_counter
                    stmt_to_counter[new_stmt_counter] = counter
                    new_stmt_counter += 1
            case 'GOT':
                if counter == stmt[1]:
                    counter_lst[counter] = -1
                else:
                    counter_lst[counter] = stmt[1]
            case 'IF':
                new_stmt_lst.append(['IF', stmt[1], stmt[2]])
                counter_lst[counter] = counter
                counter_to_stmt[counter] = new_stmt_counter
                stmt_to_counter[new_stmt_counter] = counter
                new_stmt_counter += 1
            case 'USE':
                if lb and (stmt[1][0][-1] == '*'):
                    new_stmt_lst.append(['USE', stmt[1][1]])
                    counter_lst[counter] = counter
                    counter_to_stmt[counter] = new_stmt_counter
                    stmt_to_counter[new_stmt_counter] = counter
                    new_stmt_counter += 1
        counter += 1
    
    new_stmt_lst.append(stmt_lst[-1])
    counter_to_stmt[counter] = new_stmt_counter
    stmt_to_counter[new_stmt_counter] = counter

    new_stmt_lst.append(['loop'])
    counter_to_stmt[counter + 1] = new_stmt_counter + 1
    stmt_to_counter[new_stmt_counter + 1] = counter + 1

    successors = [None]*len(new_stmt_lst)

    predecessors = [[] for _ in range(len(new_stmt_lst))]
    new_stmt_counter = 0
    for stmt in new_stmt_lst[0:-2]:
        if stmt[0] == 'IF':
            succ1 = counter_to_stmt[get_next_counter(stmt_to_counter[new_stmt_counter]+1, counter_lst)]
            succ2 = counter_to_stmt[get_next_counter(stmt[2], counter_lst)]
            successors[new_stmt_counter] = [succ1, succ2]
            predecessors[succ1].append(new_stmt_counter)
            predecessors[succ2].append(new_stmt_counter)
        else:
            succ = counter_to_stmt[get_next_counter(stmt_to_counter[new_stmt_counter]+1, counter_lst)]
            successors[new_stmt_counter] = [succ]
            predecessors[succ].append(new_stmt_counter)
        new_stmt_counter += 1

    if len(predecessors[-1]) == 0:
        new_stmt_lst.pop()
        predecessors.pop()
        successors.pop()

    #TODO (Print)
    # get_stmt_graph(new_stmt_lst, successors)

    return (new_stmt_lst, successors, predecessors)

def get_pta_stmts(struct_dict, stmt_lst):
    new_stmt_lst = []
    for stmt in stmt_lst:
        if stmt[0] == 'ASG':
            if contains_pointer(stmt[1][0], struct_dict):
                new_stmt_lst.append([stmt[1][1], stmt[2][1]])
    return new_stmt_lst

def get_defs(ptr_dict, lhs):
    vars = []
    fld = ''
    match lhs[0]:
        case 'VAR':
            vars.append(lhs[1])
            fld = '*'
        case 'PTR':
            for var in (ptr_dict[lhs[1]]['*'] - {'?'}):
                vars.append(var)
            fld = '*'
        case 'FLP':
            for var in (ptr_dict[lhs[1]]['*'] - {'?'}):
                vars.append(var)
            fld = lhs[2]
        case 'FLD':
            vars.append(lhs[1])
            fld = lhs[2]
    return (vars, fld)

def get_pointees(ptr_dict, rhs):
    pointees = set()
    match rhs[0]:
        case 'ADR':
            pointees.add(rhs[1])
        case 'VAR':
            for var in ptr_dict[rhs[1]]['*']:
                pointees.add(var)
        case 'PTR':
            for q in ptr_dict[rhs[1]]['*']:
                if q == '?':
                    pointees.add('?')
                else:
                    for var in ptr_dict[q]['*']:
                        pointees.add(var)
        case 'FLP':
            fld = rhs[2]
            for a in ptr_dict[rhs[1]]['*']:
                if a == '?':
                    pointees.add('?')
                else:
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
                pointee = ptr_dict[var_to_set_dict[pointee]]['*']
        case 'FLP':
            pointee = ptr_dict[rhs[1]]['*']
            if pointee != None:
                fld = rhs[2]
                pointee = ptr_dict[var_to_set_dict[pointee]][fld]
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

def set_dicts(var_dict, struct_dict, ptr_dict, enable_unk = True):
    for var, typ in var_dict.items():
        if contains_pointer(typ, struct_dict):
            ptr_dict[var] = {}
            
            if enable_unk:
                if typ[-1] == '*':
                    ptr_dict[var]['*'] = {'?',}
                else:
                    for field, field_typ in struct_dict[typ][0].items():
                        if field_typ[-1] == '*':
                            ptr_dict[var][field] = {'?',}
            else:
                if typ[-1] == '*':
                    ptr_dict[var]['*'] = set()
                else:
                    for field, field_typ in struct_dict[typ][0].items():
                        if field_typ[-1] == '*':
                            ptr_dict[var][field] = set()

def unify(ptr_dict, sets_to_unify, var_to_set_dict, set_to_var_dict):
    if sets_to_unify[0] == sets_to_unify[1]:
        return False
    else:
        # print(sets_to_unify)
        new_set = sets_to_unify[0]
        unified_set = sets_to_unify[1]
        # print(new_set)

        set_to_var_dict[new_set].extend(set_to_var_dict.pop(unified_set))

        for var, old_set in var_to_set_dict.items():
            if old_set == unified_set:
                var_to_set_dict[var] = new_set

        if new_set not in ptr_dict:
            return False

        new_sets_to_unify_dict = {}
        for fld, var in ptr_dict[new_set].items():
            if var != None:
                new_sets_to_unify_dict[fld] = [var_to_set_dict[var]]
            else:
                new_sets_to_unify_dict[fld] = []

        sets_to_unify = list(sets_to_unify)

        for fld, var in ptr_dict[unified_set].items():
            if var != None:
                new_sets_to_unify_dict[fld].append(var_to_set_dict[var])
        del ptr_dict[unified_set]

        change = False

        for new_sets_to_unify in new_sets_to_unify_dict.values():
            if len(new_sets_to_unify) != 2:
                continue
            change = unify(ptr_dict, new_sets_to_unify, var_to_set_dict, set_to_var_dict) or change

        return change

def get_must_pt(ptr_dict, p, f):
    ptrs = ptr_dict[p][f]
    if len(ptrs) > 1:
        return []
    elif len(ptrs) == 1 and '?' not in ptrs:
        return list(ptrs)
    else:
        return ['$all']

def get_strong_update(ptr_dict, lhs):
    vars = []
    fld = ''

    match lhs[0]:
        case 'VAR':
            vars.append(lhs[1])
            fld = '*'
        case 'PTR':
            # for var in ptr_dict[lhs[1]]['*']:
            #     vars.append(var)
            vars.extend(get_must_pt(ptr_dict, lhs[1], '*'))
            fld = '*'
        case 'FLP':
            # for var in ptr_dict[lhs[1]]['*']:
            #     vars.append(var)
            vars.extend(get_must_pt(ptr_dict, lhs[1], '*'))
            fld = lhs[2]
        case 'FLD':
            vars.append(lhs[1])
            fld = lhs[2]
    return (vars, fld)
#TODO
def set_pin(ptr_dict_in, ptr_dicts):
    for ptr in ptr_dict_in.keys():
        for fld in ptr_dict_in[ptr].keys():
            ptr_dict_in[ptr][fld].clear()
            for ptr_dict in ptr_dicts:
                ptr_dict_in[ptr][fld].update(ptr_dict[ptr][fld])

def set_lb_pin(ptr_dict_in, ptr_dicts, liveness_dict):
    for ptr, ptr_dict in ptr_dict_in.items():
        for fld, fld_dict in ptr_dict.items():
            fld_dict.clear()
            if ptr not in liveness_dict[fld]:
                continue
            for ptr_dict in ptr_dicts:
                ptr_dict_in[ptr][fld].update(ptr_dict[ptr][fld])

def set_pout(ptr_dict_out, stmt):
    if stmt[0] != 'ASG' or not stmt[3]:
        return
    
    lhs = stmt[1]
    rhs = stmt[2]

    pointees = get_pointees(ptr_dict_out, rhs)
    vars, fld = get_defs(ptr_dict_out, lhs)

    su_vars, su_fld = get_strong_update(ptr_dict_out, lhs)
    for su_var in su_vars:
        if su_var == '$all':
            for var in ptr_dict_out.values():
                if su_fld in var:
                    var[su_fld].clear()
        else:
            ptr_dict_out[su_var][su_fld].clear()

    for var in vars:
        ptr_dict_out[var][fld].update(pointees)

def set_lhsref(lhsref, lhs, check = False):
    if lhs[0] in ['PTR', 'FLP']:
        lhsref['*'] = [lhs[1]]
    elif check:
        lhsref['*'] = []

def set_lhsrhsref(ref, stmt, ptr_dict):
    set_lhsref(ref, stmt[1], True)
    rhs = stmt[2]
    check = stmt[3]
    match rhs[0]:
        case 'VAR':
            ref['*'].append(rhs[1])
        case 'PTR':
            ref['*'].append(rhs[1])
            if check:
                ref['*'].extend(ptr_dict[rhs[1]]['*'])
                # for q in ptr_dict[rhs[1]]['*']:
                #     ref['*'].append(q)
        case 'FLP':
            ref['*'].append(rhs[1])
            if check:
                fld = rhs[2]
                qs = ptr_dict[rhs[1]][fld]
                if len(qs) != 0:
                    ref[fld] = []
                    ref[fld].extend(qs)
                    # for q in qs:
                        # ref[fld].append(q)
        case 'FLD':
            ref[rhs[2]] = [rhs[1]]
            if len(ref['*']) == 0:
                del ref['*']

def get_ref(stmt, ptr_dict, liveness_dict):
    ref = {}
    if stmt[0] == 'ASG':
        lhs = stmt[1]
        vars, fld = get_defs(ptr_dict, lhs)

        if liveness_dict[fld].isdisjoint(vars):
            if sum(len(x) for x in liveness_dict.values()) != 0:
                set_lhsref(ref, lhs)
        else:
            set_lhsrhsref(ref, stmt, ptr_dict)

    elif stmt[0] == 'USE':
        ref['*'] = [stmt[1]]

    return ref

def set_lin(lout, stmt, ptr_dict):
    ref = get_ref(stmt, ptr_dict, lout)
    
    if (stmt[0] == 'ASG') and stmt[3]:
        vars, fld = get_strong_update(ptr_dict, stmt[1])
        lout[fld].difference_update(vars)

    for fld, vars in ref.items():
        lout[fld].update(vars)

def set_lout(liveness_dict_out, liveness_dicts):
    for fld, fld_dict in liveness_dict_out.items():
        fld_dict.clear()
        for liveness_dict in liveness_dicts:
            fld_dict.update(liveness_dict[fld])