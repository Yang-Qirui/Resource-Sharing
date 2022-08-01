import argparse
from copy import copy
from src import gen_decision
from pyverilog.vparser.parser import *
from pyverilog.vparser.parser import parse
from divide_ope import divide_ope
from remove_brackets import rm_brackets
import numpy as np


def reverse_condition(node):
    reverse_map = {
        Eq: NotEq,
        GreaterEq: LessThan,
        GreaterThan: LessEq,
        LessEq: GreaterThan,
        LessThan: GreaterEq
    }
    return reverse_map.get(type(node))(node.left, node.right, node.lineno)


def get_assignments(assignments, parent, conditions):
    for c in parent.children():
        if type(c) is BlockingSubstitution:
            assignments.append((c, conditions))
            return
        elif type(c) is IfStatement:
            # print(type(c.children()[0]))
            if c.true_statement:
                new_cond = copy(conditions)
                new_cond.append(c.children()[0])
                get_assignments(assignments, c.true_statement, new_cond)
            if c.false_statement:
                new_cond = copy(conditions)
                new_cond.append(reverse_condition(c.children()[0]))
                get_assignments(assignments, c.false_statement, new_cond)
        else:
            get_assignments(assignments, c, conditions)


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
    assignments = []
    get_assignments(assignments, ast, [])

    # get_condition(ast)

    linenos = []
    opes = []
    for assign, condition in assignments:

        assign.right.show()
        for cond in condition:
            cond.show()
        print("\n")

        node = rm_brackets(assign.right)
        new_node = assign.left.children(
        )[0].name + " = " + gen_code(node) + ";"
        opes.append(divide_ope(gen_code(node)))
        linenos.append((assign.lineno, new_node))

    # share_bin([ope.div for ope in opes], "DIV", args)
    # share_bin([ope.mul for ope in opes], "MUL", args)
    # share_unary([ope.add for ope in opes], args)

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


def share_bin(bins, type, args):
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
                inputs.add(item.right)
                if type == 'MUL':
                    inputs.add(item.left)
        print("inputs", inputs)
        arr = []
        for _bin in share_bins:
            row = []
            _set = set()
            '''TODO: duplicated inputs. eg.a + a'''
            for item in _bin:
                _set.add(item.right)
                if type == "MUL":
                    _set.add(item.left)
            for input in inputs:
                if input in _set:
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
