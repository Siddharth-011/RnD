from pta_helper import *
import copy

def perform_fspta(struct_dict, var_dict, stmt_lst):
    new_stmt_lst, successors, predecessors = get_fspta_stmts(struct_dict, stmt_lst)

    ptr_dicts = [{}]
    set_dicts(var_dict, struct_dict, ptr_dicts[0])

    temp_ptr_dict = {}
    set_dicts(var_dict, struct_dict, temp_ptr_dict, False)

    for _ in range(len(new_stmt_lst)-1):
        ptr_dicts.append(copy.deepcopy(temp_ptr_dict))
    del temp_ptr_dict

    
    count = 0
    change = True
    while change:
        change = False
        # print("Iteration -", count)
        # print(ptr_dict)
        stmt_no = 1
        for stmt in new_stmt_lst[1:]:
            ptr_dict_out = ptr_dicts[stmt_no]
            old_len = nested_len_pt(ptr_dict_out)

            pred_ptr_dicts = []
            for pred in predecessors[stmt_no]:
                pred_ptr_dicts.append(ptr_dicts[pred])

            set_pin(ptr_dict_out, pred_ptr_dicts)

            if stmt[0] != 'ASG':
                stmt_no += 1
                continue

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

            change = change or (old_len != nested_len_pt(ptr_dict_out))

            stmt_no += 1
        count += 1

    print("FSPTA Iteration -", count, "(confirmation)")

    get_points_to_graph(ptr_dicts[-1], 'fspta')