from pyverilog.vparser.parser import Identifier, Times, Divide, Plus, Minus


def get_privilege(node) -> bool:
    pri_left = False
    pri_right = False
    if type(node) is Times or type(node) is Divide:
        if type(node.right) is not Times and type(node.right) is not Divide and type(node.right) is not Identifier:
            pri_right = True
        if type(node.left) is not Times and type(node.left) is not Divide and type(node.left) is not Identifier:
            pri_left = True
    return pri_left, pri_right


def convert(node):
    if type(node) is Identifier:
        return node
    if type(node.left) is Identifier and type(node.right) is Identifier:
        return node
    pri_left, pri_right = get_privilege(node)
    if pri_left:
        if type(node) is Times:
            new_left = Times(node.left.left, node.right, node.left.lineno)
            new_right = Times(node.left.right, node.right, node.left.lineno)
        else:
            new_left = Divide(node.left.left, node.right, node.left.lineno)
            new_right = Divide(node.left.right, node.right, node.left.lineno)
        new_left = convert(new_left)
        new_right = convert(new_right)
        if type(node.left) is Plus:
            new_node = Plus(new_left, new_right, node.lineno)
        else:
            new_node = Minus(new_left, new_right, node.lineno)
        return new_node
    elif pri_right:
        if type(node) is Times:
            new_left = Times(node.right.left, node.left, node.right.lineno)
            new_right = Times(node.right.right, node.left, node.right.lineno)
        else:
            new_left = Divide(node.right.left, node.left, node.right.lineno)
            new_right = Divide(node.right.right, node.left, node.right.lineno)
        new_left = convert(new_left)
        new_right = convert(new_right)
        if type(node.right) is Plus:
            new_node = Plus(new_left, new_right, node.lineno)
        else:
            new_node = Minus(new_left, new_right, node.lineno)
        return new_node
    else:
        node.left = convert(node.left)
        node.right = convert(node.right)
        pri_left, pri_right = get_privilege(node)
        if pri_left or pri_right:
            node = convert(node)
        return node


def rm_brackets(node):
    """node is Rvalue"""
    return convert(node.children()[0])
