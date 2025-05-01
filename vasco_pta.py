from pta_helper import *
import copy

def is_equal(ptr_dict1:PointerDict, ptr_dict2:PointerDict):
    if (len(ptr_dict1)!=len(ptr_dict2)) or (set(ptr_dict1.keys())!=set(ptr_dict2.keys())):
        return False
    
    for key, val in ptr_dict1.items():
        for key2, val2 in ptr_dict2[key].items():
            if val2!=val[key2]:
                return False
            
    return True

def add_ptr_dict(ptr_dict:PointerDict, extra_ptr_dict:PointerDict, f_args, a_args):
    init_len = len(extra_ptr_dict)
    for f, a in zip(f_args, a_args):
        ptr_dict[f] = copy.deepcopy(extra_ptr_dict[a])

    for key, val in extra_ptr_dict.items():
        if key in ptr_dict:
            flds = ptr_dict[key]
            for key1, val1 in val.items():
                flds[key1].update(val1)
        else:
            flds = {}
            for key1, val1 in val.items():
                flds[key1] = val1.copy()
            ptr_dict[key] = flds
    
    return init_len!=len(ptr_dict)

def get_updated_func_dict(struct_dict, func_dict:dict):
    updated_func_dict = {}

    func_val = {'main':0}
    count = 1
    for func in func_dict.keys():
        if func=='main':
            continue
        func_val[func] = count
        count += 1

    for func, (args, var_dict, stmt_lst) in func_dict.items():
        funcID = "_"+str(func_val[func])

        new_stmt_lst, successors, predecessors = get_fspta_stmts(struct_dict, stmt_lst, vasco=True)

        new_args = []
        for arg in args:
            new_args.append(arg+funcID)

        new_var_dict = {}
        for varName, varType in var_dict.items():
            new_var_dict[varName+funcID] = varType

        new_stmt_lst = []
        for stmt in stmt_lst:
            new_stmt = copy.deepcopy(stmt)
            new_stmt.add_funcID(funcID)
            new_stmt_lst.append(new_stmt)
        
        updated_func_dict[func] = (new_args, new_var_dict, new_stmt_lst, successors, predecessors)

    return updated_func_dict


def perform_vascopta(struct_dict, func_dict, result_dest):
    updated_func_dict = get_updated_func_dict(struct_dict, func_dict)

    startedAnalysis = {}
    completedAnalysis = {}

    for func in func_dict.keys():
        startedAnalysis[func] = []
        completedAnalysis[func] = []

    context = ('main', {}, [])

    return vasco_pta_proc(struct_dict, updated_func_dict, context, result_dest, startedAnalysis, completedAnalysis)

def vasco_pta_proc(struct_dict, func_dict, context, result_dest, startedAnalysis:dict[str, list], completedAnalysis:dict[str, list]):

    # new_stmt_lst, successors, predecessors = get_fspta_stmts(struct_dict, stmt_lst)
    args, var_dict, stmt_lst, successors, predecessors = func_dict[context[0]]

    # infoDict = {'pos_dicts':get_stmt_graph(stmt_lst, successors, result_dest+'code')}

    ptr_dicts = [{}]
    set_ptr_dict(var_dict, struct_dict, ptr_dicts[0])

    temp_ptr_dict = {}
    set_ptr_dict(var_dict, struct_dict, temp_ptr_dict, False)

    for _ in range(len(stmt_lst)-1):
        ptr_dicts.append(copy.deepcopy(temp_ptr_dict))
    del temp_ptr_dict

    check = add_ptr_dict(ptr_dicts[0], context[1], args, context[2])

    sa_ind = len(startedAnalysis[context[0]])
    startedAnalysis[context[0]].append(copy.deepcopy(ptr_dicts[0]))

    # stmt_no = 0
    # for ptr_dict in ptr_dicts:
    #     save_dict_to_json(ptr_dict, result_dest+'pta/iter_0stmt_'+str(stmt_no)+'_out.json')
    #     stmt_no += 1

    iter = 0
    change = True
    while change:
        change = False
        iter += 1

        stmt_no = 0
        for stmt in stmt_lst:
            ptr_dict_out = ptr_dicts[stmt_no]
            old_len = nested_len_pt(ptr_dict_out)

            pred_ptr_dicts = []
            for pred in predecessors[stmt_no]:
                pred_ptr_dicts.append(ptr_dicts[pred])

            set_pin(ptr_dict_out, pred_ptr_dicts)
            # save_points_to_graph(ptr_dict_out, result_dest+'pta/iter_'+str(iter)+'stmt_'+str(stmt_no)+'_in')
            # save_dict_to_json(ptr_dict_out, result_dest+'pta/iter_'+str(iter)+'stmt_'+str(stmt_no)+'_in.json')

            if stmt.is_is_stmt_type(stmt_types.CAL):
                if not change:
                    funcID = stmt.get_uid()
                    found = False
                    for sa_context in startedAnalysis[funcID]:
                        if is_equal(sa_context, ptr_dict_out):
                            found = True
                            break
                    if found:
                        break
                    found = False
                    for ca_context in completedAnalysis[funcID]:
                        if is_equal(ca_context[0], ptr_dict_out):
                            ptr_dicts[stmt_no] = copy.deepcopy(ca_context[1])
                            found = True
                    if not found:
                        ptr_dicts[stmt_no] = copy.deepcopy(vasco_pta_proc(struct_dict, func_dict, (funcID, ptr_dict_out, stmt.), result_dest, startedAnalysis, completedAnalysis))
                stmt_no += 1
                continue

            set_pout(ptr_dict_out, stmt)
            # save_points_to_graph(ptr_dict_out, result_dest+'pta/iter_'+str(iter)+'stmt_'+str(stmt_no)+'_out')
            # save_dict_to_json(ptr_dict_out, result_dest+'pta/iter_'+str(iter)+'stmt_'+str(stmt_no)+'_out.json')

            change = change or (old_len != nested_len_pt(ptr_dict_out))

            stmt_no += 1

    # print("VASCO PTA Iteration -", iter, "(confirmation)")

    # infoDict['iters'] = iter
    # save_dict_to_json(infoDict, result_dest+'info.json')

    # TODO - remove extra PT information
    # if check:

    del startedAnalysis[context[0]][sa_ind]
    completedAnalysis[context[0]].append((startedAnalysis[context[0]].pop(sa_ind), ptr_dicts[-1]))
    return ptr_dicts[-1]
