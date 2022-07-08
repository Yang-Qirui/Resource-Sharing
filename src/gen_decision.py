import os
import sys
import time
from colorama import Fore, init
import numpy
import argparse
from merge import *
init(autoreset=True)


def gen_decision(file):
    root = StateNode()
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
                root.columns.append(
                    Column(prefix=column, formation={column: i}))
            elif '0' not in column:
                all_1_vector.append({'1111': i})
                constant -= 1
        f.close()
    if len(root.columns) > 0:
        state_tree = StateTree(root)
        state_tree.generate_tree()
        chosen_columns = state_tree.min_dict['min_state'].chosen_columns
        chosen_columns.extend(all_1_vector)
        min_cost = state_tree.min_dict['min_cost'] + len(all_1_vector)
    else:
        chosen_columns = all_1_vector
        min_cost = 0
    return min_cost, chosen_columns


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-debug', help="Print debug info", action='store_true')
    arg_parser.add_argument(
        '-d', help="Directory path that need to resource sharing", default="", required=True, type=str)
    arg_parser.add_argument(
        '-log', help="Generate log file for each file in directory", action='store_true')
    args = arg_parser.parse_args()
    file_list = []
    if args.d:
        for root, dirs, files in os.walk(args.d):
            print(Fore.YELLOW + f'Loading files: {files}')
            file_list = [args.d + '/' + file for file in files]
    t_start = time.time()
    for file in file_list:
        start = time.time()
        if not args.debug:
            sys.stdout = open(os.devnull, 'w')
        if args.log:
            with open(file + ".log", 'w') as log_file:
                sys.stdout = log_file
                min_cost, min_steps = gen_decision(file)
                log_file.close()
        else:
            min_cost, min_steps = gen_decision(file)
        sys.stdout = sys.__stdout__
        # print(Fore.GREEN + f'\nTOTAL_PLUS_COUNT: {len(min_steps)}')
        print(Fore.GREEN + f'TOTAL_MIN_COST: {min_cost}')
        print(Fore.GREEN + f'TOTAL_MIN_STEPS: {min_steps}')
        end = time.time()
        print(Fore.BLUE + f"SPEND: {end - start} second.\n")
    t_end = time.time()
    print(Fore.MAGENTA + f"TOTAL: {t_end - t_start} second.")
