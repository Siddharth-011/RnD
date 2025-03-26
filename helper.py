import graphviz
import json
from math import ceil, floor

num_colors = 9
colorscheme = 'set19'

def update_count(count):
    # count = (((count+3)%num_colors)%(num_colors-1) + num_colors-3)%num_colors + 1
    # count = ((count+3)%num_colors)%(num_colors-1)+1
    count = 1 + (count == 5) + (count!=num_colors)*count
    return count


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

def save_dict_to_json(dict, result_dest):
    with open(result_dest, 'w') as result_file:
        json.dump(dict, result_file, cls = SetEncoder, indent='\t')

def nested_len_pt(ptr_dict):
    return sum(sum(len(val2) for val2 in val.values()) for val in ptr_dict.values())

def nested_len_l(liveness_dict):
    return sum(len(val) for val in liveness_dict.values())

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
        # case 'INP':
        #     return 'read '+stmt[1]
        case 'USE':
            return 'use '+stmt[1]
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
        
def get_stmt_graph(stmt_lst, successors, result_file):
    # dot = graphviz.Digraph(comment="stmt_graph", node_attr={'shape':'box'}, graph_attr={'dpi':'256'}, engine='dot')
    dot = graphviz.Digraph(comment="stmt_graph", node_attr={'shape':'box'}, graph_attr={'bgcolor':'transparent'}, engine='dot')
    
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

    dot.render(result_file, format='svg', cleanup=True, engine='dot')
    # dot.render(result_file, format='json0', cleanup=True, engine='dot')

    dpi = 72
    dot.render('./code', format='svg', cleanup=True, engine='dot')

    pos_dicts = {}
    for obj in json.loads(dot.pipe(format='json0'))['objects']:
        pos_dict = {}
        pos_dict['h'] = ceil(float(obj['height'])*dpi)
        pos_dict['w'] = ceil(float(obj['width'])*dpi)
        pos = obj['pos'].split(',')
        pos_dict['x'] = floor(((float(pos[0])+4)*dpi)/72 - pos_dict['w']/2)
        pos_dict['y'] = ceil(((float(pos[1])+4)*dpi)/72 + pos_dict['h']/2)
        pos_dicts[obj['name']] = pos_dict

    # print(pos_dicts)
    save_dict_to_json(pos_dicts, './position_dict.json')

    # raise Exception('Line 105 of helper.py (Testing)')
    return dot

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

def get_next_counter(ind, counter_lst):
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

# def get_color_dict(ptr_dict):
#     count = 0
#     color_dict = {}

#     for node in ptr_dict:
#         count = update_count(count)
#         color_dict[node] = str(count)

#     return color_dict

def save_points_to_graph(ptr_dict, filename):
    count = 0
    dot = graphviz.Digraph(node_attr={'colorscheme':colorscheme, 'style':'filled'}, edge_attr={'colorscheme':colorscheme}, graph_attr={'rankdir':'LR', 'bgcolor':'transparent'}, engine='dot')
    color_dict = {}

    for node in ptr_dict:
        count = update_count(count)
        color_dict[node] = str(count)
        dot.node(node, color = str(count))

    for key, val in ptr_dict.items():
        # print(key,":")
        for key2, val2 in val.items():
            # print('\t',key2, '-', val2)
            if key2 == '*':
                key2 = '⁎'
            for v in val2:
                dot.edge(key, v, label = key2, color = color_dict[key])
    # dot.unflatten(stagger=1)
    dot.render(filename, format='svg', cleanup=True, engine='dot')
    # f = open(filename+'.gv', 'w')
    # f.write(dot.source)
    # f.close()
