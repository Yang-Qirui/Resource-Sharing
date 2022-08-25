
import enum
from divide_ope import Binary, Unary


class Blocks:
    def __init__(self) -> None:
        self.counter = 0
        self.blocks = []

    def add_block(self, block, _type):
        new_key = f"o{self.counter}"
        self.blocks.append((new_key, _type, block))
        self.counter += 1
        return new_key


class Registers:
    def __init__(self, prefix):
        self.counter = 0
        self.regs = []
        self.prefix = prefix

    def assign_reg(self, assign_strategy):
        new_key = f"{self.prefix}{self.counter}"
        new_reg = (new_key, {})
        for input, conditions in assign_strategy.items():
            new_reg[-1][input] = conditions
        self.regs.append(new_reg)
        self.counter += 1


class SavedSharing:
    def __init__(self):
        self.add_reg_stacks = Registers('a')
        self.mul_reg_stacks = Registers('m')
        self.div_reg_stacks = Registers('d')
        self.minus_reg_stacks = Registers('n')
        self.blocks = Blocks()

    def clear(self):
        self.add_reg_stacks.regs = []
        self.mul_reg_stacks.regs = []
        self.div_reg_stacks.regs = []

    def save_binary(self, shared, chosen_columns, inputs, _type, chain=None):
        ''' {input:[condition]}'''
        print("save_shared", [[(x.left, x.right) if type(
            x) is Binary else (x.identifier) for x in y]for y in shared])
        print("input_set", inputs)
        for column in chosen_columns:
            div_left = {}
            assign_strategy = {}
            for branches, input_id in column.items():
                for id, c in enumerate(branches):
                    if c == '1':
                        if inputs[input_id] in assign_strategy.keys():
                            assign_strategy[inputs[input_id]].append(
                                shared[id][0].branch)
                        else:
                            assign_strategy[inputs[input_id]] = [
                                shared[id][0].branch]
                        if _type == "div":
                            if shared[id][0].left in div_left.keys():
                                div_left[shared[id][0].left].append(
                                    shared[id][0].branch)
                            else:
                                div_left[shared[id][0].left] = [
                                    shared[id][0].branch]
            reg_dict = {
                "add": self.add_reg_stacks,
                "mul": self.mul_reg_stacks,
                "div": self.div_reg_stacks,
                "minus": self.minus_reg_stacks
            }
            reg_stacks = reg_dict.get(_type)
            print("assign", assign_strategy)
            if _type == "div":
                reg_stacks.assign_reg(div_left)
            reg_stacks.assign_reg(assign_strategy)
        print("reg_stacks", reg_stacks.regs)
        new_key = self.blocks.add_block(reg_stacks.regs, _type)
        if chain:
            for id, item in enumerate(chain):
                shared[id][item] = Unary(
                    shared[id][item].branch, shared[id][item].num, None, new_key)
        print([[x.identifier if type(x) is Unary else (x.left)
              for x in y]for y in shared])
        # shared.
        print("blocks", self.blocks.blocks)
        self.clear()

    def save_unary(self, shared, chosen_columns, rest_columns, inputs, _type):
        for column in chosen_columns:
            assign_strategy = {}
            for branch, input_id in column.items():
                for id, c in enumerate(branch):
                    if c == '1':
                        if inputs[input_id] in assign_strategy.keys():
                            assign_strategy[inputs[input_id]].append(
                                shared[id][0].branch)
                        else:
                            assign_strategy[inputs[input_id]] = [
                                shared[id][0].branch]
            reg_stacks = self.add_reg_stacks if _type == "add" else self.minus_reg_stacks
            reg_stacks.assign_reg(assign_strategy)
        for column in rest_columns:
            assign_strategy = {}
            for branch, input_id in column.formation.items():
                for id, c in enumerate(branch):
                    if c == '1':
                        if inputs[input_id] in assign_strategy.keys():
                            assign_strategy[inputs[input_id]].append(
                                shared[id][0].branch)
                        else:
                            assign_strategy[inputs[input_id]] = [
                                shared[id][0].branch]
            reg_stacks.assign_reg(assign_strategy)
        new_key = self.blocks.add_block(reg_stacks.regs, _type)
        print("blocks", self.blocks.blocks)

    def assign_extra(self, shared):
        for id, share in enumerate(shared[0]):
            reg_dict = {
                "add": self.add_reg_stacks,
                "mul": self.mul_reg_stacks,
                "div": self.div_reg_stacks,
                "minus": self.minus_reg_stacks
            }
            reg_stacks = reg_dict.get(share.type)
            assign_strategy = {share.left: [share.branch]}
            reg_stacks.assign_reg(assign_strategy)
            assign_strategy = {share.right: [share.branch]}
            reg_stacks.assign_reg(assign_strategy)
            new_key = self.blocks.add_block(reg_stacks.regs, share.type)
            shared[0][id] = Unary(share.branch, share.num, None, new_key)
            self.clear()
