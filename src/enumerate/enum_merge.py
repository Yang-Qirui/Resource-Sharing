import numpy as np
from copy import copy, deepcopy
import math
from ..column import Column


class Similarity:
    def __init__(self, v1, v2, sim):
        self.v1 = v1
        self.v2 = v2
        self.sim = sim


class EnumStateNode:
    def __init__(self):
        self.columns = []
        self.similarities = []
        self.avg_sim = 0
        self.cost = 0
        self.chosen_columns = []

    def cal_cos_similarity(self):
        self.similarities.clear()
        for i in range(len(self.columns)):
            v1_value = int(self.columns[i].prefix, 2)
            for j in range(i + 1, len(self.columns)):
                v2_value = int(self.columns[j].prefix, 2)
                if (v1_value | v2_value) == v1_value or (v1_value | v2_value) == v2_value:
                    continue
                v1_arr = list(self.columns[i].prefix)
                v2_arr = list(self.columns[j].prefix)
                v1 = np.array(v1_arr)
                v1 = [int(x) for x in v1]
                v2 = np.array(v2_arr)
                v2 = [int(x) for x in v2]
                sim = np.dot(v1, v2)/(np.linalg.norm(v1) * np.linalg.norm(v2))
                self.similarities.append(Similarity(i, j, sim))
                self.similarities.append(Similarity(j, i, sim))
                self.avg_sim += sim
        self.similarities.sort(key=lambda x: x.sim)
        self.avg_sim /= len(self.similarities)

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
                        if '1' not in new_key:
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


class EnumStateTree:
    def __init__(self, root):
        self.root = root
        self.min_dict = {'min_cost': np.inf, 'min_state': None}

    def _generate_tree(self, node):
        node.cal_cos_similarity()

        # if node.avg_sim == 0:
        #     # print(Fore.BLUE + f'sims are all zero')
        #     if node.cost + len(node.columns) - 1 < self.min_dict['min_cost']:
        #         formation = {}
        #         for c in node.columns:
        #             formation.update(c.formation)
        #         node.chosen_columns.append(formation)
        #         self.min_dict['min_cost'] = node.cost + len(node.columns) - 1
        #         self.min_dict['min_state'] = node
        #         return

        while len(node.similarities) > 0:
            new_node = EnumStateNode()
            new_node.chosen_columns = copy(node.chosen_columns)
            new_node.columns = deepcopy(node.columns)
            new_node.cost = node.cost

            min_sim = node.similarities.pop()
            col1 = new_node.columns[min_sim.v1]
            col2 = new_node.columns[min_sim.v2]
            new_node.merge(col1, col2)
            new_node.cost += 1
            # if new_node.cost + len(new_node.columns) / 2 < self.min_dict['min_cost']:
            # print(
            # f'columns_count: {[(c.prefix,c.formation) for c in new_node.columns]}, cost: {new_node.cost}', f"min_cost: {self.min_dict['min_cost']}")
            if new_node.cost + math.ceil(len(new_node.columns) / 2) < self.min_dict['min_cost']:
                if len(new_node.columns) > 0:
                    self._generate_tree(new_node)
                else:
                    if new_node.cost < self.min_dict['min_cost']:
                        # print(Fore.RED + f'min_cost: {new_node.cost}')
                        self.min_dict['min_cost'] = new_node.cost
                        self.min_dict['min_state'] = new_node
                # node.next.append(new_node)

    def generate_tree(self):
        self._generate_tree(self.root)
