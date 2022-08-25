from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import pyverilog.vparser.ast as vast
from pyverilog.vparser.parser import parse

from divide_ope import Binary


class UncoverNode:
    def __init__(self, v, conditions) -> None:
        self.v = v
        self.conditions


def gen_verilog(ast, blocks):
    # ast, _ = parse(["test.v"])

    # ast.show()
    assignments = []
    for _, _type, branch_assign in blocks:
        for id, (sub_name, branches) in enumerate(branch_assign):
            l_sub = vast.Lvalue(vast.Identifier(sub_name))
            for v, branch in branches.items():
                for i, b in enumerate(branch):
                    while len(b) > 1:
                        rand = b.pop()
                        land = b.pop()
                        and_cond = vast.Land(land, rand)
                        b.append(and_cond)
                    b = b[0]
                    branch[i] = b
                while len(branch) > 1:
                    ror = branch.pop()
                    lor = branch.pop()
                    or_cond = vast.Lor(lor, ror)
                    branch.append(or_cond)
                branch = branch[0]
                branches[v] = branch
            if len(branches.keys()) == 1:
                for k, v in branches.items():
                    if _type != "div" and _type != "mul":
                        branch_assign[id] = (k, v)
                    else:
                        branch_assign[id] = k
            else:
                parent_cond = None
                for k, v in branches.items():
                    if not parent_cond:
                        parent_cond = vast.Cond(v, vast.Identifier(k), None)
                        prev = parent_cond
                    else:
                        new_cond = vast.Cond(v, vast.Identifier(k), None)
                        parent_cond.false_value = new_cond
                        parent_cond = new_cond
                r_sub = vast.Rvalue(prev)
                assignments.append(vast.Assign(l_sub, r_sub))
                branch_assign[id] = sub_name

    print(blocks)
    # print([assignments])

    def cascade_assign(_blocks):
        for left, _type, rvalues in _blocks:
            for id, rvalue in enumerate(rvalues):
                if type(rvalue) is Binary:
                    rvalues[id] = rvalue.get_str()
    cascade_assign(blocks)
    print(blocks)
    # for left, _type, rvalues in blocks:
    # lvalue = vast.Lvalue(vast.Identifier(left))
    # if _type == "div":
    # assignments.append(vast.Assign(lvalue, vast.Rvalue(
    # vast.Divide(rvalues[0], rvalues[1]))))
    # elif _type == "mul":
    # assignments.append(vast.Assign(lvalue, vast.Rvalue(
    # vast.Times(rvalues[0], rvalues[1]))))
    # elif _type == "add":
    # while len(rvalues) > 1:
    # r = rvalues.pop()
    # l = rvalues.pop()
    # rvalues.append(vast.Plus(l, r))
    # assignments.append(vast.Assign(lvalue, vast.Rvalue(rvalues[0])))
    # else:
    # pass


if __name__ == "__main__":
    ast, _ = parse(["test.v"])

    ast.show()
    gen_verilog()
