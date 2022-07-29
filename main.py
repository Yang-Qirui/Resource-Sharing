import argparse
from src import gen_decision
from pyverilog.vparser.parser import BlockingSubstitution, Times, Identifier, Plus, Minus, Divide
from pyverilog.vparser.parser import parse
from divide_ope import divide_ope
from remove_brackets import rm_brackets
import numpy as np


assignments = []
assign_dict = {}


def get_assignments(parent):
    for c in parent.children():
        if type(c) is BlockingSubstitution:
            assignments.append(c)
            return
        get_assignments(c)


def init_assign_dict():
    for assign in assignments:
        lvalue = getattr(assign.left.var, 'name')
        if lvalue in assign_dict.keys():
            assign_dict[lvalue].append(assign.right.var)
        else:
            assign_dict[lvalue] = [assign.right.var]


def gen_code(node):
    if type(node) is Identifier:
        return node.name
    types = {
        Times: "*",
        Divide: "/",
        Plus: "+",
        Minus: "-"
    }
    ope = types.get(type(node))
    left = gen_code(node.left)
    right = gen_code(node.right)
    if ope == "-":
        right = right.replace("+", "-")
    return f"{left} {ope} {right}"


def share(filename, args):
    ast, _ = parse([filename])
    # ast.show()
    get_assignments(ast)
    linenos = []
    opes = []
    for assign in assignments:
        node = rm_brackets(assign.right)
        new_node = assign.left.children(
        )[0].name + " = " + gen_code(node) + ";"
        opes.append(divide_ope(gen_code(node)))
        linenos.append((assign.lineno, new_node))

    share_bin([ope.div for ope in opes], args)
    share_bin([ope.mul for ope in opes], args)
    share_unary([ope.add for ope in opes], args)

    assignments.clear()
    with open(filename, 'r') as input:
        with open(filename[:-2]+"_convert.v", 'w') as output:
            lines = input.readlines()
            for lineno, new_code in linenos:
                space = len(lines[lineno - 1]) - \
                    len(lines[lineno - 1].lstrip())
                lines[lineno -
                      1] = new_code.rjust(space + len(new_code)) + "\n"
            output.writelines(lines)


def get_max_sharing_part(opes):
    max_ope = np.inf
    for ope in opes:
        if len(ope) < max_ope != 0:
            max_ope = len(ope)
    return max_ope


def share_bin(bins, args):
    bins = list(filter(lambda x: len(x) > 0, bins))
    # print([[(x.left, x.right) for x in _bin] for _bin in bins])

    while len(bins) > 1:
        length = get_max_sharing_part(bins)
        share_bins = []
        # print(divs)
        for i in range(len(bins)):
            '''TODO: not randomly choose'''
            share_bins.append(bins[i][:length])
            bins[i] = bins[i][length:]
        # print([[(x.left, x.right) for x in _bin] for _bin in bins])
        inputs = set()
        for _bin in share_bins:
            for item in _bin:
                '''Count all inputs without counting duplicated inputs'''
                inputs.add(item.left)
        print("inputs", inputs)
        arr = []
        for _bin in share_bins:
            row = []
            left_set = set()
            '''TODO: duplicated inputs. eg.a + a'''
            for item in _bin:
                left_set.add(item.left)
            for input in inputs:
                if input in left_set:
                    row.append('1')
                else:
                    row.append('0')
            arr.append(row)
        np_arr = np.array(arr)
        print(np_arr)
        min_cost, chosen_columns = gen_decision.gen_decision(np_arr, args)
        print(min_cost, chosen_columns)
        """TODO: save results"""
        bins = list(filter(lambda x: len(x) > 0, bins))


def share_unary(unarys, args):
    unarys = list(filter(lambda x: len(x) > 0, unarys))

    while len(unarys) > 1:
        length = get_max_sharing_part(unarys)
        share_unarys = []
        for i in range(len(unarys)):
            '''TODO: not randomly choose'''
            share_unarys.append(unarys[i][:length])
            unarys[i] = unarys[i][length:]
        inputs = set()
        for unary in share_unarys:
            for item in unary:
                inputs.add(item.identifier)
        arr = []
        for unary in share_unarys:
            row = []
            single_input = set()
            '''TODO: duplicated inputs. eg.a + a'''
            for item in unary:
                single_input.add(item.identifier)
            for input in inputs:
                if input in single_input:
                    row.append('1')
                else:
                    row.append('0')
            arr.append(row)
        np_arr = np.array(arr)
        print(np_arr)
        min_cost, chosen_columns = gen_decision.gen_decision(np_arr, args)
        print(min_cost, chosen_columns)
        '''TODO: save results'''
        unarys = list(filter(lambda x: len(x) > 0, unarys))


def main(args):
    share('test1.v', args)
    # ast, _ = parse(['test1_convert.v'])
    # # ast.show()
    # start = time.time()
    # get_assignments(ast)
    # end = time.time()
    # print(f"Get assignments finished. Spent {end-start} seconds")
    # # print(assignments)
    # start = time.time()
    # init_assign_dict()
    # end = time.time()
    # print(f"Init dict finished. Spent {end-start} seconds")
    # print(assign_dict)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-m', help='Resource sharing method. [ENUM, RANDOM, GREEDY, MCTS]', default='GREEDY')
    arg_parser.add_argument('-t', help='Time limit for MCTS', default=1)
    arg_parser.add_argument(
        '-r', help='Random exploration for MCTS', action='store_true')
    arg_parser.add_argument(
        '-v', help='Add visit time into MCTS make_decision consideration', action='store_true')

    args = arg_parser.parse_args()
    main(args)
