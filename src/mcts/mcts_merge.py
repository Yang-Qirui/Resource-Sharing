import numpy as np
from copy import deepcopy
from math import sqrt, log
import random
import time
import sys
sys.path.append("..")
from column import Column  # NOQA: E402


class MCTSStateNode:
    def __init__(self):
        self.columns = []
        self.cost = 0
        self.chosen_columns = []
        self.parent = None
        self.children = []
        self.visit = 0
        self.expanded = []

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


class MCTSStateTree:
    def __init__(self, root, m, c, time_limit, random, visit, weight=0.3):
        self.root = root
        self.m = m
        self.c = c
        self.time_limit = time_limit
        self.is_random = random
        self.is_visit = visit
        self.weight = weight
        self.min_dict = {'min_cost': np.inf, 'min_state': None}

    def selection(self):
        node = self.root
        while node.children:
            # print([x.prefix for x in node.columns])
            node.visit += 1
            prob = len(node.expanded) == len(node.columns) * \
                (len(node.columns) - 1) / 2
            if self.is_random:
                possibility = random.random()
                prob = prob or (possibility > 0.5)
            if prob:
                def cal_func(x):
                    if x.cost == 0:
                        return np.inf
                    else:
                        # print((1 / x.cost) / (1 / x.cost + self.weight *
                        #       sqrt(2*log(self.visit) / x.visit)))
                        return 1 / x.cost + self.weight * sqrt(2*log(node.visit) / x.visit)
                node.children.sort(key=lambda x: cal_func(x))
                node = node.children[-1]
            else:

                break
        return node

    def expansion(self, node):
        if len(node.columns) == 0:
            return None
        indexes = random.sample(range(0, len(node.columns)), 2)
        while (indexes[0], indexes[1]) in node.expanded:
            indexes = random.sample(range(0, len(node.columns)), 2)
        new_node = MCTSStateNode()
        new_node.parent = node
        new_node.columns = deepcopy(node.columns)
        new_node.chosen_columns = deepcopy(node.chosen_columns)
        new_node.merge(
            new_node.columns[indexes[0]], new_node.columns[indexes[1]])

        if not new_node.columns:
            cost = 0
            for item in new_node.chosen_columns:
                cost += len(item.keys()) - 1
            if cost < self.min_dict['min_cost']:
                self.min_dict['min_cost'] = cost
                self.min_dict['min_state'] = new_node

        node.children.append(new_node)
        node.expanded.append((indexes[0], indexes[1]))
        return new_node

    def simulation(self, node):
        new_node = MCTSStateNode()
        new_node.columns = deepcopy(node.columns)
        # for _ in range(self.c * (self.m - 1)):
        while True:
            if len(new_node.columns) == 0:
                break
            max_1 = 0
            for c in new_node.columns:
                count_1 = c.prefix.count('1')
                if count_1 > max_1:
                    max_1 = count_1
                    max_col = c
            for c in new_node.columns:
                if int(c.prefix, 2) | int(
                        max_col.prefix, 2) != int(
                        max_col.prefix, 2):
                    new_node.merge(max_col, c)
                    break
            new_node.cost += 1

        # while True:
        #     if len(new_node.columns) == 0:
        #         break
        #     indexes = random.sample(range(0, len(new_node.columns)), 2)
        #     new_node.merge(
        #         new_node.columns[indexes[0]], new_node.columns[indexes[1]])
        #     new_node.cost += 1
        node.cost = new_node.cost

    def backpropagation(self, node, value):
        '''
            parent's cost equal to the minimum cost of its children
        '''
        node.visit += 1
        while node:
            # print([x.prefix for x in node.columns])
            if node.cost > value:
                node.cost = value
            value += 1
            node = node.parent

    def make_decision(self):
        node = self.root
        while node.children:
            if self.is_visit:
                node.children.sort(key=lambda x: x.cost + node.visit / x.visit)
            else:
                node.children.sort(key=lambda x: x.cost)
            node = node.children[0]
        if node.columns:
            print('Need merge')
            while len(node.columns) > 0:
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

        cost = 0
        for item in node.chosen_columns:
            cost += len(item.keys()) - 1

        self.min_dict['min_cost'] = cost
        self.min_dict['min_state'] = node
        return True

    def debug(self):
        l = [self.root]
        print(len(self.root.children))
        head = 0
        tail = 1
        while head < tail:
            for c in l[head].children:
                l.append(c)
                tail += 1
            head += 1
        print(head)
        for node in l:
            print([x.prefix for x in node.columns], node.visit, node.cost)

    def generate_tree(self):
        start = time.time()
        end = start
        while end - start < self.time_limit:
            node = self.selection()
            print(node.cost, [x.prefix for x in node.columns])
            expand_node = self.expansion(node)
            if expand_node:
                self.simulation(expand_node)
                self.backpropagation(expand_node, expand_node.cost)
            end = time.time()
        node = self.min_dict['min_state']
        if not node:
            self.make_decision()
