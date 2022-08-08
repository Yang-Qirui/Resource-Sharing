class Registers:
    def __init__(self):
        self.regs = []

    def assign_reg(self, ope):
        self.regs.append(ope.get_str())


class SavedSharing:
    def __init__(self, ope):
        self.ope = ope
        self.share = {}

    def save_result(self, shared, chosen_columns, inputs):
        reg_dict = {
            "+": "a",
            "*": "m",
            "/": "d"
        }
        new_reg = reg_dict.get(self.ope) + str(len(self.share.keys()))
        self.share[new_reg] = {}
        if self.ope == "/":
            for column in chosen_columns:
                for k, v in column:
                    for c in k:
                        if c == '1':
                            pass
