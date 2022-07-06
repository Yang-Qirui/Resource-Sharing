from copy import copy, deepcopy
from colorama import Fore
import numpy as np


class Similarity:
    def __init__(self, v1, v2, sim):
        self.v1 = v1
        self.v2 = v2
        self.sim = sim


class Column:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


class StateNode:
    def __init__(self):
        self.columns = []
        self.similarities = []
        self.next = []
        self.cost = 0
        self.cnt = 0
        self.chosen_columns = []

    def delete(self, prefix):
        self.columns = list(
            filter(lambda x: x.prefix != prefix, self.columns))

    def cal_cos_similarity(self):
        self.similarities.clear()
        for i in range(len(self.columns)):
            v1_arr = list(self.columns[i].prefix)
            v1 = np.array(v1_arr)
            v1 = [int(x) for x in v1]
            v1_value = int(self.columns[i].prefix, 2)
            for j in range(i + 1, len(self.columns)):
                v2_arr = list(self.columns[j].prefix)
                v2 = np.array(v2_arr)
                v2 = [int(x) for x in v2]
                v2_value = int(self.columns[j].prefix, 2)
                if (v1_value | v2_value) == v1_value or (v1_value | v2_value) == v2_value:
                    continue
                sim = np.dot(v1, v2)/(np.linalg.norm(v1) * np.linalg.norm(v2))
                self.similarities.append(Similarity(i, j, sim))
        self.similarities.sort(key=lambda x: x.sim, reverse=True)

    def merge(self, col1, col2):
        '''merge col2 to col1'''
        print(f"\nmerge {col1.prefix} & {col2.prefix}")

        def gen_extend_vec(v1, v2):
            extend_vec = ''
            for i in range(len(v1)):
                if int(v1[i]) + int(v2[i]) > 1:
                    extend_vec += '1'
                else:
                    extend_vec += '0'
            return extend_vec

        # columns = [c.prefix for c in self.columns]
        # print(Fore.GREEN + f"Before columns: {columns}")
        self.columns.remove(col1)
        self.columns.remove(col2)
        or_vec = bin(int(col1.prefix, 2) | int(
            col2.prefix, 2))[2:].zfill(len(col1.prefix))
        # print(f"col1.formation:{col1.formation}")
        # print(f"col2.formation:{col2.formation}")
        extend_vec = gen_extend_vec(col1.prefix, col2.prefix)
        # print(
        # f"col1:{col1.prefix}, col2:{col2.prefix}, or_vec:{or_vec}, extend_vec:{extend_vec}")
        '''it means col1 & col2 have duplicate part. eg. 1100 & 1010. extend_vec is 1000'''
        col1_copy = copy(col1)
        col2_copy = copy(col2)
        # print(Fore.BLUE+f'Point0: {e-s}')
        if '1' in extend_vec:
            if extend_vec in col2.formation.keys():
                num = col2_copy.formation.pop(extend_vec)
            else:
                for k in col2_copy.formation.keys():
                    contribute_vec = gen_extend_vec(k, extend_vec)
                    '''
                        find a key to contribute to extend_vec. eg. extend_vec is 1000
                        key is 1010,so it can divide the vector from 1010 to 1000 + 0010
                    '''
                    if '1' in contribute_vec:
                        new_key = bin(int(k, 2) - int(
                            contribute_vec, 2))[2:].zfill(len(k))
                        num = col2_copy.formation.pop(k)
                        if '1' in new_key:
                            col2_copy.formation[new_key] = num
                        break
            self.columns.append(
                Column(prefix=extend_vec, formation={extend_vec: num}))
        col1_copy.formation.update(col2_copy.formation)
        # print(f"col1.formation:{col1_copy.formation}")
        # print(f"col2.formation:{col2_copy.formation}")
        # print(col1_copy.formation)
        # print(Fore.GREEN+f'Point1: {e-s}')
        if '0' in or_vec:
            self.columns.append(
                Column(prefix=or_vec, formation=col1_copy.formation))
        else:
            self.cnt += 1
            self.chosen_columns.append(col1_copy.formation)
        # print(Fore.YELLOW+f'Point2: {e-s}')

        # columns = [c.prefix for c in self.columns]
        # print(Fore.GREEN + f"After columns: {columns}\n")


class StateTree:
    def __init__(self, root):
        self.root = root
        self.min_dict = {'min_cost': np.inf, 'min_state': None}

    def _generate_tree(self, node):
        node.cal_cos_similarity()
        # print(Fore.RED + f"Cal SIM: {e-s}")
        while len(node.similarities) > 0:
            new_node = StateNode()
            new_node.chosen_columns = copy(node.chosen_columns)
            new_node.columns = deepcopy(node.columns)
            new_node.cnt = copy(node.cnt)
            new_node.cost = copy(node.cost)
            min_sim = node.similarities.pop()
            col1 = new_node.columns[min_sim.v1]
            col2 = new_node.columns[min_sim.v2]
            new_node.merge(col1, col2)
            new_node.cost += 1
            # if new_node.cost < self.min_dict['min_cost']:
            #     color = Fore.GREEN
            # else:
            #     color = Fore.WHITE
            # print(
            #     color + f'columns_count: {len(new_node.columns)}, cost: {new_node.cost}')
            if new_node.cost < self.min_dict['min_cost']:
                if len(new_node.columns) > 0:
                    self._generate_tree(new_node)
                else:
                    if new_node.cost < self.min_dict['min_cost']:
                        # print(Fore.RED + f'min_cost: {new_node.cost}')
                        self.min_dict['min_cost'] = new_node.cost
                        self.min_dict['min_state'] = new_node
                node.next.append(new_node)

    def generate_tree(self):
        self._generate_tree(self.root)
