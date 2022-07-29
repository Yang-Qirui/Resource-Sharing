from .enumerate.enum_merge import *
from .baseline.random_merge import *
from .baseline.greedy_merge import *
from .mcts.mcts_merge import *
from colorama import init, Fore
import numpy
init(autoreset=True)


def gen_decision_from_file(file, args):
    if args.m == 'ENUM':
        root = EnumStateNode()
    elif args.m == 'RANDOM':
        root = RandomStateNode()
    elif args.m == 'GREEDY':
        root = GreedyStateNode()
    elif args.m == 'MCTS':
        root = MCTSStateNode()
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
            m = len(column)
            # print(f"Col{i}: {column}")
            if '1' in column and '0' in column:
                root.columns.append(
                    Column(prefix=column, formation={column: i}))
            elif '0' not in column:
                all_1_vector.append({''.rjust(len(column), '1'): i})
                constant -= 1
        f.close()
    if len(root.columns) > 0:
        if args.m == 'ENUM':
            state_tree = EnumStateTree(root)
        elif args.m == 'RANDOM':
            state_tree = RandomStateTree(root)
        elif args.m == 'GREEDY':
            state_tree = GreedyStateTree(root)
        elif args.m == 'MCTS':
            state_tree = MCTSStateTree(
                root, m, constant, float(args.t), args.r, args.v)
        state_tree.generate_tree()
        chosen_columns = state_tree.min_dict['min_state'].chosen_columns
        chosen_columns.extend(all_1_vector)
        min_cost = state_tree.min_dict['min_cost'] + len(all_1_vector)
    else:
        chosen_columns = all_1_vector
        min_cost = len(all_1_vector)
    return min_cost, chosen_columns


def gen_decision(A, args):
    if args.m == 'ENUM':
        root = EnumStateNode()
    elif args.m == 'RANDOM':
        root = RandomStateNode()
    elif args.m == 'GREEDY':
        root = GreedyStateNode()
    elif args.m == 'MCTS':
        root = MCTSStateNode()
    column_size = A.shape[1]
    all_1_vector = []
    constant = str(A[0]).count('1')
    for i in range(column_size):
        column_string = A[:, i]
        column = ''
        for c in column_string:
            column += c
        m = len(column)
        # print(f"Col{i}: {column}")
        if '1' in column and '0' in column:
            root.columns.append(
                Column(prefix=column, formation={column: i}))
        elif '0' not in column:
            all_1_vector.append({''.rjust(len(column), '1'): i})
            constant -= 1

    if len(root.columns) > 0:
        if args.m == 'ENUM':
            state_tree = EnumStateTree(root)
        elif args.m == 'RANDOM':
            state_tree = RandomStateTree(root)
        elif args.m == 'GREEDY':
            state_tree = GreedyStateTree(root)
        elif args.m == 'MCTS':
            state_tree = MCTSStateTree(
                root, m, constant, float(args.t), args.r, args.v)
        state_tree.generate_tree()
        chosen_columns = state_tree.min_dict['min_state'].chosen_columns
        chosen_columns.extend(all_1_vector)
        min_cost = state_tree.min_dict['min_cost'] + len(all_1_vector)
    else:
        chosen_columns = all_1_vector
        min_cost = len(all_1_vector)
    return min_cost, chosen_columns
