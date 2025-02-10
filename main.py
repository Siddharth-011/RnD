from parser import parse_file
from andersen import perform_andersens_analysis

file_name = "test.txt"

(struct_dict, func_dict) = parse_file(file_name)

if func_dict['main'] == 'error':
    print('Resolve the errors in', file_name, 'and try again')

else:
    # print(struct_dict)
    # print(func_dict['main'])
    perform_andersens_analysis(struct_dict, func_dict['main'][1], func_dict['main'][2])
    pass