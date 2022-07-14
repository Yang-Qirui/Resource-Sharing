import numpy as np
import random
import sys
sys.path.append("..")
from column import Column  # NOQA: E402


class RandomStateNode:
    def __init__(self):
        self.columns = []
        self.cost = 0
        self.chosen_columns = []

    def merge(self, col1, col2):
        '''merge col2 to col1'''
        # print(f"\nmerge {col1.prefix} & {col2.prefix}")
        # columns = [c.prefix for c in self.columns]
        # print(Fore.GREEN + f"Before columns: {columns}")
        self.columns.remove(col1)
        self.columns.remove(col2)
        or_vec = bin(int(col1.prefix, 2) | int(
            col2.prefix, 2))[2:].zfill(len(col1.prefix))
        # print(f"col1.formation:{col1.formation}")
        # print(f"col2.formation:{col2.formation}")
        and_vec = bin(int(col1.prefix, 2) & int(
            col2.prefix, 2))[2:].zfill(len(col1.prefix))
        # print(f"col1:{col1.prefix}, col2:{col2.prefix}, or_vec:{or_vec}, extend_vec:{extend_vec}")
        '''it means col1 & col2 have duplicate part. eg. 1100 & 1010. extend_vec is 1000'''
        if '1' in and_vec:
            if and_vec in col2.formation.keys():
                num = col2.formation.pop(and_vec)
                self.columns.append(
                    Column(prefix=and_vec, formation={and_vec: num}))
            else:
                # print(col2.formation, and_vec)
                pop_list = []
                push_list = []
                for k in col2.formation.keys():
                    contribute = int(k, 2) & int(
                        and_vec, 2)
                    # print(k, and_vec)
                    if contribute != 0:
                        new_key = bin(int(k, 2) - contribute)[2:].zfill(len(k))
                        pop_list.append(k)
                        # num = col2.formation.pop(k)
                        push_list.append((new_key, col2.formation[k]))
                        # col2.formation[new_key] = num
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

        # columns = [c.prefix for c in self.columns]
        # print(Fore.GREEN + f"After columns: {columns}\n")


class RandomStateTree:
    def __init__(self, root):
        self.root = root
        self.min_dict = {'min_cost': np.inf, 'min_state': None}

    def _generate_tree(self, node):
        while len(node.columns) > 0:
            col_count = len(node.columns)
            indexes = random.sample(range(0, col_count), 2)
            # print(indexes)
            node.merge(node.columns[indexes[0]], node.columns[indexes[1]])
            node.cost += 1
        self.min_dict['min_cost'] = node.cost
        self.min_dict['min_state'] = node

    def generate_tree(self):
        self._generate_tree(self.root)
