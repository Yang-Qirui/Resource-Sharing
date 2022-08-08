import argparse
from audioop import mul
from copy import copy
from share_graph import Graph
from src import gen_decision
from pyverilog.vparser.parser import *
from pyverilog.vparser.parser import parse
from divide_ope import Binary, divide_ope
from remove_brackets import rm_brackets
import numpy as np
from store_share import Registers

regs = Registers()


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

        # assign.right.show()
        # for cond in condition:
        #     cond.show()
        # print("\n")

        node = rm_brackets(assign.right)
        new_node = assign.left.children(
        )[0].name + " = " + gen_code(node) + ";"
        opes.append(divide_ope(gen_code(node), condition))
        linenos.append((assign.lineno, new_node))

    """ TODO: share cascade mul and div: a * b / c -> tmp / c. 
        def share_cascade()
    """
    share_cascade([ope.div for ope in opes], [ope.mul for ope in opes], args)
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


def share_cascade(divs, muls, args):
    # print(divs, muls)
    new_mul = []
    new_div = []

    def add_cascade(ope, _type, branch_div, branch_mul):
        if type(ope.left) is Binary:
            if ope.left.type == "mul":
                branch_mul.append(ope.left)
            elif ope.left.type == "div":
                branch_div.append(ope.left)
        if _type == "MUL":
            if type(ope.right) is Binary:
                if ope.right.type == "mul":
                    branch_mul.append(ope.right)
                elif ope.right.type == "div":
                    branch_div.append(ope.riht)

    div_dict = {}
    mul_dict = {}
    branches = []

    for div in divs:
        for d in div:
            branch_div = []
            branch_mul = []
            add_cascade(d, "DIV", branch_div, branch_mul)
            # print(branch_div, branch_mul)
            if d.branch in branches:
                div_dict[branches.index(d.branch)].extend(branch_div)
                mul_dict[branches.index(d.branch)].extend(branch_mul)
            else:
                branches.append(d.branch)
                div_dict[len(branches) - 1] = branch_div
                mul_dict[len(branches) - 1] = branch_mul
    for mul in muls:
        for m in mul:
            branch_div = []
            branch_mul = []
            add_cascade(m, "MUL", branch_div, branch_mul)
            if m.branch in branches:
                div_dict[branches.index(m.branch)].extend(branch_div)
                mul_dict[branches.index(m.branch)].extend(branch_mul)
            else:
                branches.append(m.branch)
                div_dict[len(branches) - 1] = branch_div
                mul_dict[len(branches) - 1] = branch_mul

    for _, v in div_dict.items():
        if v:
            new_div.append(v)
    for _, v in mul_dict.items():
        if v:
            new_mul.append(v)

    if len(new_mul) >= 2 or len(new_div) >= 2:
        share_cascade(new_div, new_mul, args)
    else:
        print("No cascade")

    # print("divs", divs)
    # print("new_mul", new_mul)
    # print("new_div", new_div)
    share_mul(new_mul, args)
    # share_bin(new_mul, "MUL", args)
    # share_bin(new_div, "DIV", args)
    return


def share_mul(muls, args):
    print("muls", [[(x.left, x.right) for x in y] for y in muls])
    muls = list(filter(lambda x: len(x) > 0, muls))
    while len(muls) > 1:
        length = get_max_sharing_part(muls)
        share_muls = []
        for i in range(len(muls)):
            share_muls.append(muls[i][:length])
            muls[i] = muls[i][length:]
        share_edges = set()
        print("share_muls", [[(x.left, x.right)
              for x in y] for y in share_muls])
        for i in range(len(share_muls) - 1):
            input_dict = {}
            for j in range(len(share_muls[i])):
                if share_muls[i][j].left in input_dict.keys():
                    input_dict[share_muls[i][j].left].append(
                        i * len(share_muls[i]) + j)
                else:
                    input_dict[share_muls[i][j].left] = [
                        i * len(share_muls[i]) + j]
                if share_muls[i][j].right in input_dict.keys():
                    input_dict[share_muls[i][j].right].append(
                        i * len(share_muls[i]) + j)
                else:
                    input_dict[share_muls[i][j].right] = [
                        i * len(share_muls[i]) + j]
            for j in range(len(share_muls[i + 1])):
                if share_muls[i + 1][j].left in input_dict.keys():
                    for v in input_dict[share_muls[i + 1][j].left]:
                        share_edges.add((v, (i + 1) * len(share_muls[i]) + j))
                if share_muls[i + 1][j].right in input_dict.keys():
                    for v in input_dict[share_muls[i + 1][j].right]:
                        share_edges.add((v, (i + 1) * len(share_muls[i]) + j))
            # print(input_dict.keys())
            g = Graph(len(share_muls) * len(share_muls[0]))
            # print(share_edges)
            for edge in share_edges:
                g.add_edge(edge)
            chains = g.choose_chain()
            print(chains)
            for chain in chains:
                first = share_muls[i][chain[0]]
                last = share_muls[i + 1][chain[1] % len(share_muls[0])]
                print(((first.left, first.right), (last.left, last.right)))

        muls = list(filter(lambda x: len(x) > 0, muls))


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
        print([[(x.left, x.right) for x in y]for y in share_bins])
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
        # print(np_arr)
        min_cost, chosen_columns = gen_decision.gen_decision(np_arr, args)
        # print(min_cost, chosen_columns)
        '''TODO: save results'''
        unarys = list(filter(lambda x: len(x) > 0, unarys))


def main(args):
    share('test1.v', args)


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
