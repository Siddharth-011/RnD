from pta_helper import *
import graphviz

def perform_andersens_analysis(struct_dict, var_dict, stmt_lst):
    ptr_dict = {}
    isunk_ptr_dict = {}
    
    set_dicts(var_dict, struct_dict, ptr_dict, isunk_ptr_dict, False)
    
    new_stmt_lst = get_pta_stmts(struct_dict, stmt_lst)

    count = 0
    change = True
    while change:
        change = False
        # print("Iteration -", count)
        # print(ptr_dict)
        for (lhs, rhs) in new_stmt_lst:
            pointees = get_pointees(ptr_dict, rhs, isunk_ptr_dict)
            # print(pointees)
            vars, fld = get_defs(ptr_dict, lhs)
            for var in vars:
                old_len = len(ptr_dict[var][fld])
                ptr_dict[var][fld].update(pointees)
                change = change or (old_len != len(ptr_dict[var][fld]))
        count += 1

    print("Andersens Iteration -", count, "(confirmation)")

    dot = graphviz.Digraph(comment="Andersen's PTA", node_attr={'colorscheme':'set19', 'style':'filled'}, edge_attr={'colorscheme':'set19'}, engine='dot')
    count = 0
    color_dict = {}
    for node in ptr_dict.keys():
        count = count%9 + 1
        color_dict[node] = str(count)
        dot.node(node, color = str(count))
    for key, val in ptr_dict.items():
        print(key,":")
        for key2, val2 in val.items():
            print('\t',key2, '-', val2)
            for v in val2:
                dot.edge(key, v, label = key2, color = color_dict[key])
    dot.render('andersens', format='png', cleanup=True)

def perform_steensgaards_analysis(struct_dict, var_dict, stmt_lst):
    ptr_dict = {}
    isunk_ptr_dict = {}
    var_to_set_dict = {}

    for var, typ in var_dict.items():
        var_to_set_dict[var] = var
        if contains_pointer(typ, struct_dict):
            ptr_dict[var] = {}
            isunk_ptr_dict[var] = False
            if typ[-1] == '*':
                ptr_dict[var]['*'] = None
            else:
                for field, field_typ in struct_dict[typ][0].items():
                    if field_typ[-1] == '*':
                        ptr_dict[var][field] = None

    new_stmt_lst = get_pta_stmts(struct_dict, stmt_lst)

    count = 0
    change = True

    while change:
        change = False
        # print("Iteration -",count)
        for (lhs, rhs) in new_stmt_lst:
            pointee = get_pointee(ptr_dict, rhs, var_to_set_dict)
            if pointee != None:
                pointee = var_to_set_dict[pointee]
                # print(pointee)
                var, fld = get_def(ptr_dict, lhs)
                # sets_to_unify = set([pointee])
                # print(ptr_dict)
                # print(var_to_set_dict)
                if var != None:
                    var = var_to_set_dict[var]
                    old_var = ptr_dict[var][fld]
                    if old_var is None:
                        ptr_dict[var][fld] = pointee
                        change = True
                    else:
                        sets_to_unify = set([pointee, var_to_set_dict[old_var]])
                        # sets_to_unify.add(var_to_set_dict[ptr_dict[var][fld]])
                        # vars_to_unify.add(ptr_dict[vars][fld])
                        change = unify(ptr_dict, sets_to_unify, var_to_set_dict) or change

        count += 1

    print("Steensgard Iteration -", count, "(confirmation)")
    for key, val in ptr_dict.items():
        print(key,":")
        for key2, val2 in val.items():
            print('\t',key2, '-', val2)
    
    set_to_var_dict = {}
    for var, set_ in var_to_set_dict.items():
        if set_ in set_to_var_dict:
            set_to_var_dict[set_].append(var)
        else:
            set_to_var_dict[set_] = [var]
    print(set_to_var_dict)

def unify(ptr_dict, sets_to_unify, var_to_set_dict):
    if len(sets_to_unify) == 1:
        return False
    else:
        print(sets_to_unify)
        new_set = sets_to_unify.pop()
        # print(new_set)

        # var_to_set_dict[new_set] = new_set

        new_sets_to_unify_dict = {}
        for fld, val in ptr_dict[new_set].items():
            new_sets_to_unify_dict[fld] = set([val])

        for var, old_set in var_to_set_dict.items():
            if old_set in sets_to_unify:
                var_to_set_dict[var] = new_set

        sets_to_unify = list(sets_to_unify)

        for old_set in sets_to_unify:
            for fld, var in ptr_dict[old_set].items():
                if var != None:
                    new_sets_to_unify_dict[fld].add(var_to_set_dict[var])
            del ptr_dict[old_set]

        change = False

        for vars in new_sets_to_unify_dict.values():
            vars.discard(None)
            vars = list(vars)
            new_sets_to_unify = set()

            for var in vars:
                new_sets_to_unify.add(var_to_set_dict[var])

            change = unify(ptr_dict, sets_to_unify, var_to_set_dict) or change

        return change