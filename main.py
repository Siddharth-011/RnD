from parser import parse_file
from fi_pta import perform_andersens_analysis, perform_steensgaards_analysis
from fs_pta import perform_fspta, get_fspta_stmts
from lfcpa  import perform_lfcpa

file_name = "test.txt"

(struct_dict, func_dict) = parse_file(file_name)

if func_dict['main'] == 'error':
    print('Resolve the errors in', file_name, 'and try again')

else:
    # print(struct_dict)
    # print(func_dict['main'])
    # for d in func_dict.values():
        # for stmt in d[2]:
        #     print(stmt)
        # get_fspta_stmts(d[1], d[2])
        # break
    perform_andersens_analysis(struct_dict, func_dict['main'][1], func_dict['main'][2])
    perform_steensgaards_analysis(struct_dict, func_dict['main'][1], func_dict['main'][2])
    perform_fspta(struct_dict, func_dict['main'][1], func_dict['main'][2])
    perform_lfcpa(struct_dict, func_dict['main'][1], func_dict['main'][2])
    pass