from pta_helper import *
import copy

def perform_lfcpa(struct_dict, var_dict, stmt_lst, result_dest):
    new_stmt_lst, successors, predecessors = get_fspta_stmts(struct_dict, stmt_lst, True)

    get_stmt_graph(new_stmt_lst, successors, result_dest+'code')

    ptr_dicts = [{}]
    liveness_dicts = []
    set_dicts(var_dict, struct_dict, ptr_dicts[0])

    temp_liveness_dict = {}
    for flds in ptr_dicts[0].values():
        for fld in flds:
            if fld not in temp_liveness_dict:
                temp_liveness_dict[fld] = set()
    liveness_dicts.append(copy.deepcopy(temp_liveness_dict))

    temp_ptr_dict = {}
    set_dicts(var_dict, struct_dict, temp_ptr_dict, False)
    # temp_liveness_dict = {}
    # for fld in liveness_dicts[0]:
    #     temp_liveness_dict[fld] = set()

    for _ in range(len(new_stmt_lst)-1):
        ptr_dicts.append(copy.deepcopy(temp_ptr_dict))
        liveness_dicts.append(copy.deepcopy(temp_liveness_dict))
    liveness_dicts.append(liveness_dicts.pop(0))
    del temp_ptr_dict
    del temp_liveness_dict

    if new_stmt_lst[-1][0] == 'loop':
        liveness_dicts.append(liveness_dicts.pop(0))
        updt_stmt_list = new_stmt_lst[:-1]
    else:
        updt_stmt_list = new_stmt_lst

    iters = []
    iter = 0
    while True:
        iter += 1
        l_iter = preform_ptbla(updt_stmt_list, successors, ptr_dicts, liveness_dicts, result_dest+'la/iter_'+str(iter)+'_')
        if l_iter == 1:
            iters.append((1,0))
            break
        pt_iter = preform_lbpta(updt_stmt_list, predecessors, ptr_dicts, liveness_dicts, result_dest+'pta/iter_'+str(iter)+'_')
        iters.append((l_iter, pt_iter))
        if pt_iter == 1:
            break
    print("LFCPA Iteration -", len(iters), iters)
    # save_points_to_graph(ptr_dicts[len(updt_stmt_list)-1], result_dest)


def preform_lbpta(new_stmt_lst, predecessors, ptr_dicts, liveness_dicts, result_dest):
    iter = 0
    change = True
    while change:
        change = False
        iter += 1
        
        stmt_no = 1
        for stmt in new_stmt_lst[1:]:
            ptr_dict_out = ptr_dicts[stmt_no]
            old_len = nested_len_pt(ptr_dict_out)

            pred_ptr_dicts = []
            for pred in predecessors[stmt_no]:
                pred_ptr_dicts.append(ptr_dicts[pred])

            set_lb_pin(ptr_dict_out, pred_ptr_dicts, liveness_dicts[stmt_no])
            save_points_to_graph(ptr_dict_out, result_dest+str(iter)+'stmt_'+str(stmt_no)+'_in')
            save_dict_to_json(ptr_dict_out, result_dest+str(iter)+'stmt_'+str(stmt_no)+'_in.json')

            set_pout(ptr_dict_out, stmt)
            save_points_to_graph(ptr_dict_out, result_dest+str(iter)+'stmt_'+str(stmt_no)+'_out')
            save_dict_to_json(ptr_dict_out, result_dest+str(iter)+'stmt_'+str(stmt_no)+'_out.json')

            change = change or (old_len != nested_len_pt(ptr_dict_out))

            stmt_no += 1
    return iter

def preform_ptbla(new_stmt_lst, successors, ptr_dicts, liveness_dicts, result_dest):
    iter = 0
    change = True
    
    while change:
        change = False
        iter += 1

        stmt_no = len(new_stmt_lst)-2
        for stmt in new_stmt_lst[-2::-1]:
            liveness_dict_in = liveness_dicts[stmt_no]
            old_len = nested_len_l(liveness_dict_in)

            succ_liveness_dicts = []
            for succ in successors[stmt_no]:
                succ_liveness_dicts.append(liveness_dicts[succ])

            set_lout(liveness_dict_in, succ_liveness_dicts)
            save_dict_to_json(liveness_dict_in, result_dest+str(iter)+'stmt_'+str(stmt_no)+'_out.json')
            
            set_lin(liveness_dict_in, stmt, ptr_dicts[stmt_no])
            save_dict_to_json(liveness_dict_in, result_dest+str(iter)+'stmt_'+str(stmt_no)+'_in.json')

            change = change or (old_len != nested_len_l(liveness_dict_in))

            stmt_no -= 1
    return iter