import time
from pyverilog.vparser.parser import BlockingSubstitution, Times, Identifier, Plus, Minus, Divide
from pyverilog.vparser.parser import parse
from divide_ope import divide_ope
from remove_brackets import rm_brackets

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


def remove_brackets(filename):
    ast, _ = parse([filename])
    # ast.show()
    get_assignments(ast)
    linenos = []
    for assign in assignments:
        node = rm_brackets(assign.right)
        new_node = assign.left.children(
        )[0].name + " = " + gen_code(node) + ";"
        divide_ope(gen_code(node))
        linenos.append((assign.lineno, new_node))
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
    ast, _ = parse(['test1_convert.v'])
    ast.show()
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
