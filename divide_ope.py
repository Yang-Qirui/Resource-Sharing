import re


class Node:
    def __init__(self, branch, num=None, type=None):
        self.num = num
        self.type = type
        self.branch = branch


class Unary(Node):
    def __init__(self, branch, num=None, type=None, identifier=None):
        super().__init__(branch, num, type)
        self.identifier = identifier

    def get_str(self):
        return self.identifier


class Binary(Node):
    def __init__(self, branch, num=None, type=None, left=None, right=None):
        super().__init__(branch, num, type)
        self.left = left
        self.right = right

    def get_str(self):
        res = ''
        if self.left is Binary:
            res += self.left.get_str()
        else:
            res += 'left'
        if self.type == "div":
            return res + '/' + self.right
        else:
            return res + '*' + self.right


class DividedOpes:
    def __init__(self, add, minus, mul, div):
        self.add = add
        self.minus = minus
        self.mul = mul
        self.div = div


def get_privilege(curr, top):
    dict = {
        "#": 0,
        "+": 1,
        "-": 1,
        "/": 2,
        "*": 2
    }
    curr_w = dict.get(curr)
    top_w = dict.get(top)
    return curr_w > top_w


def divide_ope(equation, branch):
    equation = equation.replace(" ", '')
    # print(equation)
    add = []
    minus = []
    mul = []
    div = []
    num_stack = []
    ope_stack = ['#']
    split = re.split('(\W)', equation)
    opes = ['+', '-', '*', '/']

    def calculate():
        top = ope_stack.pop()
        if top == "*" or top == "/":
            r = num_stack.pop()
            l = num_stack.pop()
            type, category = (
                "mul", mul) if top == "*" else ("div", div)
            if r in category:
                category.pop(r.num)
                r.num = None
            if l in category:
                category.pop(l.num)
                l.num = None
            new_binary = Binary(branch, len(category), type,  l, r)
            category.append(new_binary)
            num_stack.append(new_binary)
        else:
            ident = num_stack.pop()
            type, category = (
                "add", add) if top == "+" else ("minus", minus)
            new_unary = Unary(branch, len(category), type, ident)
            category = add if top == "+" else minus
            category.append(new_unary)

    for i in split:
        if i in opes:
            top = ope_stack[-1]
            priv = get_privilege(i, top)
            while not priv:
                calculate()
                top = ope_stack[-1]
                priv = get_privilege(i, top)
            ope_stack.append(i)
        else:
            num_stack.append(i)
    while ope_stack[-1] != "#":
        calculate()
    while len(num_stack) != 0:
        add.append(Unary(len(add), "add", num_stack.pop()))
    return DividedOpes(add, minus, mul, div)
