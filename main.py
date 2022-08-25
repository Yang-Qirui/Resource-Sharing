import numpy as np
from divide_ope import Binary, Unary, divide_ope
import argparse
from copy import copy
from gen_verilog import gen_verilog
from share_graph import Graph
from src import gen_decision
from pyverilog.vparser.parser import *
from pyverilog.vparser.parser import parse

from store_share import SavedSharing
# from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
storage = SavedSharing()


def reverse_condition(node):
    reverse_map = {
        Eq: NotEq,
        GreaterEq: LessThan,
        GreaterThan: LessEq,
        LessEq: GreaterThan,
        LessThan: GreaterEq
    }
    return reverse_map.get(type(node))(node.left, node.right, node.lineno)


def get_assignments(assignments, parent, conditions, output=None):
    for c in parent.children():
        if type(c) is Assign:
            output = c.left.var
        elif type(c) is Cond:
            # print(type(c.children()[0]))
            print("false", c.false_value, type(c.false_value))
            print("true", c.true_value)
            print("cond", c.cond)

            if c.true_value:
                new_cond = copy(conditions)
                new_cond.append(c.cond)
                assignments.append((c.true_value, new_cond, output))
                # get_assignments(assignments, c.true_value, new_cond)
            if type(c.false_value) is not Cond:
                new_cond = copy(conditions)
                new_cond.append(reverse_condition(c.cond))
                assignments.append((c.false_value, new_cond, output))
                # get_assignments(assignments, c.false_value, new_cond)
            else:
                conditions.append(reverse_condition(c.cond))
        get_assignments(assignments, c, conditions, output)


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

    ast.show()
    assignments = []
    get_assignments(assignments, ast, [])
    print(assignments)
    # get_condition(ast)

    linenos = []
    opes = []
    for assign, condition, output in assignments:

        # assign.right.show()
        # for cond in condition:
        #     cond.show()
        # print("\n")

        # node = rm_brackets(assign.right)
        # new_node = assign.left.children(
        # )[0].name + " = " + gen_code(node) + ";"
        print(gen_code(assign))
        opes.append(divide_ope(gen_code(assign), condition))
        # linenos.append((assign.lineno, new_node))

    """ TODO: share cascade mul and div: a * b / c -> tmp / c. 
        def share_cascade()
    """
    ope_div = [ope.div for ope in opes]
    ope_mul = [ope.mul for ope in opes]
    share_cascade(ope_div, args, "div")
    for id, div in enumerate(ope_div):
        opes[id].div = div
    share_cascade(ope_mul, args, "mul")
    for id, mul in enumerate(ope_mul):
        opes[id].mul = mul
    print("ope.div", [[(x.identifier) if type(x) is Unary else (
        x.left, x.right) for x in y]for y in ope_div])
    print("ope.mul", [[(x.identifier) if type(x) is Unary else (
        x.left, x.right) for x in y]for y in ope_mul])
    for ope in opes:
        for add in ope.add:
            if type(add.identifier) is Binary:
                category = ope.mul if add.identifier.type == "mul" else ope.div
                add.identifier = category[add.identifier.num].identifier
        for minus in ope.minus:
            if type(minus.identifier) is Binary:
                category = ope.mul if minus.identifier.type == "mul" else ope.div
                minus.identifier = category[minus.identifier.num].identifier

    # print(storage.blocks.blocks)
    # share_bin([ope.div for ope in opes], "DIV", args)
    # share_bin([ope.mul for ope in opes], "MUL", args)
    share_unary([ope.add for ope in opes], args, "add")
    share_unary([ope.minus for ope in opes], args, "minus")
    gen_verilog(ast, storage.blocks.blocks)
    # assignments.clear()
    # with open(filename, 'r') as input:
    #     with open(filename[:-2]+"_convert.v", 'w') as output:
    #         lines = input.readlines()
    #         for lineno, new_code in linenos:
    #             space = len(lines[lineno - 1]) - \
    #                 len(lines[lineno - 1].lstrip())
    #             lines[lineno -
    #                   1] = new_code.rjust(space + len(new_code)) + "\n"
    #         output.writelines(lines)


def share_cascade(shares, args, _type):
    if len(shares) == 0:
        return
    elif len(shares) == 1:
        print("len1", [(x.left, x.right) for x in shares[0]])
        storage.assign_extra(shares)
        print("_len1", [x.identifier for x in shares[0]])
        return
    new_shares_mul = []
    share_mul_id = []
    new_shares_div = []
    share_div_id = []
    for i, branch_share in enumerate(shares):
        cascade_mul = []
        id_mul = []
        cascade_div = []
        id_div = []
        for id, share in enumerate(branch_share):
            if type(share.left) is Binary:
                if share.left.type == "div":
                    cascade_div.append(share.left)
                    id_div.append((i, id))
                else:
                    cascade_mul.append(share.left)
                    id_mul.append((i, id))
        if cascade_mul:
            new_shares_mul.append(cascade_mul)
            share_mul_id.append(id_mul)
        if cascade_div:
            new_shares_div.append(cascade_div)
            share_div_id.append(id_div)
    share_cascade(new_shares_div, args, "div")
    share_cascade(new_shares_mul, args, "mul")
    print("new_shares_mul", [[x.identifier for x in y]for y in new_shares_mul])
    print("share_mul_id", [[x for x in y]for y in share_mul_id])
    print("new_shares_div", [[x.identifier for x in y]for y in new_shares_div])
    print("share_div_id", [[x for x in y]for y in share_div_id])
    for j, ids in enumerate(share_mul_id):
        for i, id in ids:
            shares[i][id].left = new_shares_mul[j][id].identifier
    for j, ids in enumerate(share_div_id):
        for i, id in ids:
            shares[i][id].left = new_shares_div[j][id].identifier
    if _type == "mul":
        share_mul(shares, args)
    else:
        print("_divs", [[(x.identifier) if type(x) is Unary else (
            x.left, x.right) for x in y]for y in shares])
        share_div(shares, args)
    print("after_shares", [[(x.left, x.right) if type(
        x) is Binary else (x.identifier) for x in y] for y in shares])


def share_mul(muls, args):
    print("muls", [[(x.left, x.right, x.branch)
                    for x in y] for y in muls])
    muls = list(filter(lambda x: len(x) > 0, muls))
    if len(muls) == 1:
        storage.assign_extra(muls, '*')
        return
    if not muls:
        return
    chains = []
    for i in range(len(muls) - 1):
        share_edges = set()
        input_dict = {}
        for j in range(len(muls[i])):
            if muls[i][j].left in input_dict.keys():
                input_dict[muls[i][j].left].append(
                    i * len(muls[i]) + j)
            else:
                input_dict[muls[i][j].left] = [
                    i * len(muls[i]) + j]
            if muls[i][j].right in input_dict.keys():
                input_dict[muls[i][j].right].append(
                    i * len(muls[i]) + j)
            else:
                input_dict[muls[i][j].right] = [
                    i * len(muls[i]) + j]
        for j in range(len(muls[i + 1])):
            if muls[i + 1][j].left in input_dict.keys():
                for v in input_dict[muls[i + 1][j].left]:
                    share_edges.add((v, j))
            if muls[i + 1][j].right in input_dict.keys():
                for v in input_dict[muls[i + 1][j].right]:
                    share_edges.add((v, j))
        g = Graph(len(muls[i]), len(muls[i + 1]))
        for edge in share_edges:
            g.add_edge(edge)
        chain = g.choose_chain()
        chains.append(chain)

    # print(chains)
    while len(chains) > 1:
        chains[0].sort(key=lambda x: x[-1])
        chains[1].sort(key=lambda x: x[0])
        i = j = 0
        while i < len(chains[0]) and j < len(chains[1]):
            if chains[0][i][-1] == chains[1][j][0]:
                chains[0][i] += (chains[1][j][-1],)
                i += 1
                j += 1
            elif chains[0][i][-1] < chains[1][j][0]:
                i += 1
            else:
                j += 1
        chains.pop(1)
    print('chain', chains)
    for chain in chains[0]:
        input_set = set()
        for i, index in enumerate(chain):
            input_set.add(muls[i][index].left)
            input_set.add(muls[i][index].right)
        print("input_set", input_set)
        arr = []
        for i, index in enumerate(chain):
            row = []
            for input in input_set:
                if input == muls[i][index].left or input == muls[i][index].right:
                    row.append('1')
                else:
                    row.append('0')
            arr.append(row)
        np_arr = np.array(arr)
        # print(np_arr)
        min_cost, chosen_columns, rest_columns = gen_decision.gen_decision(
            np_arr, args)
        storage.save_binary(muls, chosen_columns,
                            list(input_set), "mul", chain)
        # print(min_cost, chosen_columns, rest_columns)


def share_div(divs, args):
    print("divs", [[(x.left, x.right, x.branch)
                   for x in y] for y in divs])
    divs = list(filter(lambda x: len(x) > 0, divs))
    if len(divs) == 1:
        storage.assign_extra(divs, '/')
        return
    if not divs:
        return
    chains = []
    for i in range(len(divs) - 1):
        share_edges = set()
        input_dict = {}
        for j in range(len(divs[i])):
            if divs[i][j].right in input_dict.keys():
                input_dict[divs[i][j].right].append(
                    i * len(divs[i]) + j)
            else:
                input_dict[divs[i][j].right] = [
                    i * len(divs[i]) + j]
        for j in range(len(divs[i + 1])):
            if divs[i + 1][j].right in input_dict.keys():
                for v in input_dict[divs[i + 1][j].right]:
                    share_edges.add((v, j))
        g = Graph(len(divs[i]), len(divs[i + 1]))
        for edge in share_edges:
            g.add_edge(edge)
        chain = g.choose_chain()
        chains.append(chain)

    # print(chains)
    while len(chains) > 1:
        chains[0].sort(key=lambda x: x[-1])
        chains[1].sort(key=lambda x: x[0])
        i = j = 0
        while i < len(chains[0]) and j < len(chains[1]):
            if chains[0][i][-1] == chains[1][j][0]:
                chains[0][i] += (chains[1][j][-1],)
                i += 1
                j += 1
            elif chains[0][i][-1] < chains[1][j][0]:
                i += 1
            else:
                j += 1
        chains.pop(1)
    print('chain', chains)
    for chain in chains[0]:
        input_set = set()
        for i, index in enumerate(chain):
            # input_set.add(divs[i][index].left)
            input_set.add(divs[i][index].right)
        print("input_set", input_set)
        arr = []
        for i, index in enumerate(chain):
            row = []
            for input in input_set:
                # if input == divs[i][index].left or input == divs[i][index].right:
                if input == divs[i][index].right:
                    row.append('1')
                else:
                    row.append('0')
            arr.append(row)
        np_arr = np.array(arr)
        # print(np_arr)
        min_cost, chosen_columns, rest_columns = gen_decision.gen_decision(
            np_arr, args)
        storage.save_binary(divs, chosen_columns,
                            list(input_set), "div", chain)
        # print(min_cost, chosen_columns, rest_columns)


def share_unary(unarys, args, _type):
    unarys = list(filter(lambda x: len(x) > 0, unarys))
    inputs = set()
    for unary in unarys:
        for item in unary:
            inputs.add(item.identifier)
    arr = []
    for unary in unarys:
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
    min_cost, chosen_columns, rest_columns = gen_decision.gen_decision(
        np_arr, args)
    # print(min_cost, chosen_columns)
    '''TODO: save results'''
    storage.save_unary(unarys, chosen_columns,
                       rest_columns, list(inputs), _type)


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
