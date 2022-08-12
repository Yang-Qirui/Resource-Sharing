import numpy as np
from ..column import Column


class GreedyStateNode:
    def __init__(self):
        self.columns = []
        self.cost = 0
        self.chosen_columns = []

    def stop(self):
        if not self.columns:
            return True
        for i in range(len(self.columns[0].prefix)):
            zero_line = True
            for c in self.columns:
                if c.prefix[i] != '0':
                    zero_line = False
                    break
            if zero_line:
                return True
        return False

    def merge(self, col1, col2):
        '''merge col2 to col1'''
        self.columns.remove(col1)
        self.columns.remove(col2)
        or_vec = bin(int(col1.prefix, 2) | int(
            col2.prefix, 2))[2:].zfill(len(col1.prefix))
        and_vec = bin(int(col1.prefix, 2) & int(
            col2.prefix, 2))[2:].zfill(len(col1.prefix))
        '''it means col1 & col2 have duplicate part. eg. 1100 & 1010. extend_vec is 1000'''
        if '1' in and_vec:
            if and_vec in col2.formation.keys():
                num = col2.formation.pop(and_vec)
                self.columns.append(
                    Column(prefix=and_vec, formation={and_vec: num}))
            else:
                pop_list = []
                push_list = []
                for k in col2.formation.keys():
                    contribute = int(k, 2) & int(
                        and_vec, 2)
                    if contribute != 0:
                        new_key = bin(int(k, 2) - contribute)[2:].zfill(len(k))
                        pop_list.append(k)
                        if '1' in new_key:
                            push_list.append((new_key, col2.formation[k]))
                        new_prefix = bin(contribute)[2:].zfill(len(k))
                        self.columns.append(
                            Column(prefix=new_prefix, formation={new_prefix: col2.formation[k]}))
                        and_vec = bin(int(and_vec, 2) -
                                      contribute)[2:].zfill(len(k))
                    if '1' not in and_vec:
                        break
                for item in pop_list:
                    col2.formation.pop(item)
                for item in push_list:
                    col2.formation[item[0]] = item[1]
        col1.formation.update(col2.formation)
        if '0' in or_vec:
            self.columns.append(
                Column(prefix=or_vec, formation=col1.formation))
        else:
            self.chosen_columns.append(col1.formation)


class GreedyStateTree:
    def __init__(self, root):
        self.root = root
        self.min_dict = {'min_cost': np.inf, 'min_state': None}

    def _generate_tree(self, node):
        while not node.stop():
            max_1 = 0
            for c in node.columns:
                one_count = c.prefix.count('1')
                # print(c.prefix, one_count)
                if one_count > max_1:
                    max_1 = one_count
                    max_col = c
            for c in node.columns:
                if int(c.prefix, 2) | int(
                        max_col.prefix, 2) != int(
                        max_col.prefix, 2):
                    node.merge(max_col, c)
                    break
            node.cost += 1
        self.min_dict['min_cost'] = node.cost
        self.min_dict['min_state'] = node

    def generate_tree(self):
        self._generate_tree(self.root)
