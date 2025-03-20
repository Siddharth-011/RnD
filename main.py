from parser import parse_file
from fi_pta import perform_andersens_analysis, perform_steensgaards_analysis
from fs_pta import perform_fspta, get_fspta_stmts
from lfcpa  import perform_lfcpa
import os, shutil

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

    results_dir = './results'
    if os.path.exists(results_dir):
        for filename in os.listdir(results_dir):
            file_path = os.path.join(results_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        os.mkdir(results_dir)
    

    # perform_andersens_analysis(struct_dict, func_dict['main'][1], func_dict['main'][2])
    # perform_steensgaards_analysis(struct_dict, func_dict['main'][1], func_dict['main'][2])

    os.mkdir(results_dir+'/fspta')
    os.mkdir(results_dir+'/fspta/pta')
    perform_fspta(struct_dict, func_dict['main'][1], func_dict['main'][2],  results_dir+'/fspta/')

    # os.mkdir(results_dir+'/lfcpa')
    # os.mkdir(results_dir+'/lfcpa/la')
    # os.mkdir(results_dir+'/lfcpa/pta')
    # perform_lfcpa(struct_dict, func_dict['main'][1], func_dict['main'][2], results_dir+'/lfcpa/')