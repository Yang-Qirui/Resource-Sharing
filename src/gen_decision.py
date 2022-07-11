from enumerate.enum_merge import *
from baseline.random_merge import *
from baseline.greedy_merge import *
from colorama import init
import numpy
init(autoreset=True)


def gen_decision(file, method):
    if method == 'ENUM':
        root = EnumStateNode()
    elif method == 'RANDOM':
        root = RandomStateNode()
    elif method == 'GREEDY':
        root = GreedyStateNode()
    with open(file, 'r') as f:
        # print(Fore.CYAN + f"Processing {file}")
        cnt = 0
        line = f.readline().replace(" ", '')
        constant = len(line.split('1')) - 1
        # print(Fore.RED + f'Number of all \'1\' vector: {constant}')
        arr = []
        while line:
            try:
                int(line, 2)
            except:
                raise Exception(f"Line {cnt} is not a pure 01 string")
            row = list(line.strip())
            arr.append(row)
            line = f.readline()
        A = numpy.array(arr)
        column_size = A.shape[1]
        all_1_vector = []
        for i in range(column_size):
            column_string = A[:, i]
            column = ''
            for c in column_string:
                column += c
            # print(f"Col{i}: {column}")
            if '1' in column and '0' in column:
                if method == 'ENUM':
                    root.columns.append(
                        EnumColumn(prefix=column, formation={column: i}))
                elif method == 'RANDOM':
                    root.columns.append(
                        RandomColumn(prefix=column, formation={column: i}))
                elif method == 'GREEDY':
                    root.columns.append(
                        GreedyColumn(prefix=column, formation={column: i})
                    )
            elif '0' not in column:
                all_1_vector.append({''.rjust(len(column), '1'): i})
                constant -= 1
        f.close()
    if len(root.columns) > 0:
        if method == 'ENUM':
            state_tree = EnumStateTree(root)
        elif method == 'RANDOM':
            state_tree = RandomStateTree(root)
        elif method == 'GREEDY':
            state_tree = GreedyStateTree(root)
        state_tree.generate_tree()
        chosen_columns = state_tree.min_dict['min_state'].chosen_columns
        chosen_columns.extend(all_1_vector)
        min_cost = state_tree.min_dict['min_cost'] + len(all_1_vector)
    else:
        chosen_columns = all_1_vector
        min_cost = 0
    return min_cost, chosen_columns
