from pta_helper import *
import graphviz

num_colors = 9
colorscheme = 'set19'

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

    count = 0
    dot = graphviz.Digraph(comment="Andersen's PTA", node_attr={'colorscheme':colorscheme, 'style':'filled'}, edge_attr={'colorscheme':colorscheme}, graph_attr={'rankdir':'LR', 'dpi':'250'}, engine='dot')
    color_dict = {}

    for node in ptr_dict.keys():
        count = count%num_colors + 1
        color_dict[node] = str(count)
        dot.node(node, color = str(count))

    for key, val in ptr_dict.items():
        print(key,":")
        for key2, val2 in val.items():
            print('\t',key2, '-', val2)
            for v in val2:
                dot.edge(key, v, label = key2, color = color_dict[key])
    # dot.unflatten(stagger=3)
    dot.render('andersens', format='png', cleanup=True)

def perform_steensgaards_analysis(struct_dict, var_dict, stmt_lst):
    ptr_dict = {}
    isunk_ptr_dict = {}
    var_to_set_dict = {}
    set_to_var_dict = {}

    for var, typ in var_dict.items():
        var_to_set_dict[var] = var
        set_to_var_dict[var] = [var]
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
        count += 1
        for (lhs, rhs) in new_stmt_lst:
            pointee = get_pointee(ptr_dict, rhs, var_to_set_dict)

            if pointee is None:
                continue

            pointee = var_to_set_dict[pointee]
            # print(pointee)
            var, fld = get_def(ptr_dict, lhs)
            # print(ptr_dict)
            # print(var_to_set_dict)

            if var == None:
                continue

            var = var_to_set_dict[var]
            old_var = ptr_dict[var][fld]
            if old_var is None:
                ptr_dict[var][fld] = pointee
                change = True
            else:
                sets_to_unify = [pointee, var_to_set_dict[old_var]]
                change = unify(ptr_dict, sets_to_unify, var_to_set_dict, set_to_var_dict) or change

    print("Steensgaard Iteration -", count, "(confirmation)")

    count = 0
    dot = graphviz.Digraph(comment="Steensgaard's PTA", node_attr={'colorscheme':colorscheme, 'style':'filled'}, edge_attr={'colorscheme':colorscheme}, graph_attr={'rankdir':'LR', 'dpi':'250'}, engine='dot')
    color_dict = {}

    for node in ptr_dict.keys():
        count = count%num_colors + 1
        color_dict[node] = str(count)
        vars = '\n'.join(set_to_var_dict[node])
        dot.node(node, vars, color = str(count))

    for key, val in ptr_dict.items():
        print(key,":")
        for key2, val2 in val.items():
            if val2 is None:
                continue
            print('\t',key2, '-', var_to_set_dict[val2])
            dot.edge(key, var_to_set_dict[val2], label = key2, color = color_dict[key])
    print(set_to_var_dict)

    dot.render('steensgaard', format='png', cleanup=True)