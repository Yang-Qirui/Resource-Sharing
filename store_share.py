
from divide_ope import Unary


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
        self.blocks = Blocks()

    def clear(self):
        self.add_reg_stacks.regs.clear()
        self.mul_reg_stacks.regs.clear()
        self.div_reg_stacks.regs.clear()

    def save_result(self, shared, chosen_columns, inputs, _type, chain):
        ''' {input:[condition]}'''
        for column in chosen_columns:
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
            reg_dict = {
                "+": self.add_reg_stacks,
                "*": self.mul_reg_stacks,
                "/": self.div_reg_stacks
            }
            reg_stacks = reg_dict.get(_type)
            reg_stacks.assign_reg(assign_strategy)
            for reg in reg_stacks.regs:
                pass
        new_key = self.blocks.add_block(reg_stacks.regs, _type)
        for id, item in enumerate(chain):
            shared[id][item] = Unary(
                shared[id][item].branch, shared[id][item].branch, None, new_key)
        print([[x.identifier if type(x) is Unary else (x.left)
              for x in y]for y in shared])
        # shared.
        # print(self.blocks.blocks)
        self.clear()
