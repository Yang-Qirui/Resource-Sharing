import time
import re
from pyverilog.vparser.parser import BlockingSubstitution, Times, Identifier
from pyverilog.vparser.parser import parse

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


def remove_brackets(filename):
    ast, _ = parse([filename])
    ast.show()
    get_assignments(ast)
    linenos = []
    for assign in assignments:
        linenos.append(assign.lineno)
    assignments.clear()
    with open(filename, 'r') as f:
        lines = f.readlines()
        for lineno in linenos:
            print(lines[lineno-1])


def share_mul(times):
    left = times.left
    right = times.right
    if type(left) is not Identifier:
        pass
    elif type(right) is not Identifier:
        pass
    else:
        pass


def share(list):

    pass


def main():
    remove_brackets('test1.v')
    ast, _ = parse(['test1.v'])
    start = time.time()
    get_assignments(ast)
    end = time.time()
    print(f"Get assignments finished. Spent {end-start} seconds")
    # print(assignments)
    start = time.time()
    init_assign_dict()
    end = time.time()
    print(f"Init dict finished. Spent {end-start} seconds")
    print(assign_dict)


if __name__ == "__main__":
    main()
