import graphviz

num_colors = 9
colorscheme = 'set19'

def nested_len(ptr_dict):
    return sum(sum(len(val2) for val2 in val.values()) for val in ptr_dict.values())

def get_fspta_stmts(struct_dict, stmt_lst):
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
        if stmt[0] == 'ASG':
            if contains_pointer(stmt[1][0], struct_dict):
                new_stmt_lst.append(['ASG', stmt[1][1], stmt[2][1]])
                counter_lst[counter] = counter
                counter_to_stmt[counter] = new_stmt_counter
                stmt_to_counter[new_stmt_counter] = counter
                new_stmt_counter += 1
        elif stmt[0] == 'GOT':
            counter_lst[counter] = stmt[1]
        elif stmt[0] == 'IF':
            new_stmt_lst.append(['IF', stmt[1], stmt[2]])
            counter_lst[counter] = counter
            counter_to_stmt[counter] = new_stmt_counter
            stmt_to_counter[new_stmt_counter] = counter
            new_stmt_counter += 1
        counter += 1
    
    new_stmt_lst.append(stmt_lst[-1])
    counter_to_stmt[counter] = new_stmt_counter
    stmt_to_counter[new_stmt_counter] = counter
    counter += 1
    new_stmt_counter += 1

    new_stmt_lst.append(['loop'])
    counter_to_stmt[counter] = new_stmt_counter
    stmt_to_counter[new_stmt_counter] = counter

    successors = [None]*len(new_stmt_lst)

    predecessors = [[] for _ in range(len(new_stmt_lst))]
    new_stmt_counter = 0
    for stmt in new_stmt_lst[0:-2]:
        if stmt[0] == 'IF':
            succ1 = counter_to_stmt[get_new_loc(stmt_to_counter[new_stmt_counter]+1, counter_lst)]
            succ2 = counter_to_stmt[get_new_loc(stmt[2], counter_lst)]
            successors[new_stmt_counter] = [succ1, succ2]
            predecessors[succ1].append(new_stmt_counter)
            predecessors[succ2].append(new_stmt_counter)
        else:
            succ = counter_to_stmt[get_new_loc(stmt_to_counter[new_stmt_counter]+1, counter_lst)]
            successors[new_stmt_counter] = [succ]
            predecessors[succ].append(new_stmt_counter)
        new_stmt_counter += 1

    if len(predecessors[-1]) == 0:
        new_stmt_lst.pop()
        predecessors.pop()
        successors.pop()

    # for i in range(len(new_stmt_lst)):
    #     print(i, format_stmt(new_stmt_lst[i]), successors[i], predecessors[i])
    get_stmt_graph(new_stmt_lst, successors)

    return (new_stmt_lst, successors, predecessors)

def get_new_loc(ind, counter_lst):
    seen = set()
    seen_size = -1
    while seen_size!=len(seen):
        if ind == counter_lst[ind]:
            break
        seen_size = len(seen)
        seen.add(ind)
        
        while counter_lst[ind] == None:
            ind += 1
            seen.add(ind)
        ind = counter_lst[ind]

    if ind != counter_lst[ind]:
        ind = counter_lst[-1]

    for seen_ind in seen:
        counter_lst[seen_ind] = ind

    return ind

def format_stmt(stmt):
    match stmt[0]:
        case 'ASG':
            return format_elem(stmt[1])+' = '+format_elem(stmt[2])
        # case 'GOT':
        #     return 'goto '+str(stmt[1])
        case 'IF':
            return 'if '+format_elem(stmt[1])
        case 'CAL':
            return 'call '+stmt[1]
        case 'INP':
            return 'read '+stmt[1]
        case _:
            return stmt[0]

def format_elem(elem):
    match elem[0]:
        case 'VAR':
            return elem[1]
        case 'PTR':
            return '*'+elem[1]
        case 'FLP':
            return elem[1]+'->'+elem[2]
        case 'FLD':
            return elem[1]+'.'+elem[2]
        case 'ADR':
            return '&'+elem[1]
        case 'NUM':
            num = str(elem[1])
            if num[-1]=='0':
                return num[:-2]
            return num
        case 'BEX':
            return format_elem(elem[2])+elem[1]+format_elem(elem[3])
        case 'MAL':
            return 'malloc('+elem[1]+')'
        
def get_stmt_graph(stmt_lst, successors):
    dot = graphviz.Digraph(comment="stmt_graph", node_attr={'shape':'box'}, graph_attr={'dpi':'250'}, engine='dot')
    
    i = 0
    # with dot.subgraph(name='cluster0') as c:
    for stmt in stmt_lst:
        dot.node(str(i), format_stmt(stmt))
        i += 1
        # c.attr(label = 'Hello')

    i = 0
    for succs in successors[:-1]:
        if succs:
            for succ in succs:
                dot.edge(str(i), str(succ))
        i += 1

    dot.render('doctest-output/test.gv', format='png', cleanup=True, engine='dot')
    return dot

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

def get_pin(ptr_dict_in, ptr_dicts):
    for ptr in ptr_dict_in.keys():
        for fld in ptr_dict_in[ptr].keys():
            ptr_dict_in[ptr][fld].clear()
            for ptr_dict in ptr_dicts:
                ptr_dict_in[ptr][fld].update(ptr_dict[ptr][fld])
