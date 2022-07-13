import numpy as np
from copy import copy, deepcopy
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
        self.visit = 1

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
            else:
                for k in col2.formation.keys():
                    new_key = bin(int(k, 2) - int(
                        and_vec, 2))[2:].zfill(len(k))
                    num = col2.formation.pop(k)
                    if '1' in new_key:
                        col2.formation[new_key] = num
                    break
            self.columns.append(
                Column(prefix=and_vec, formation={and_vec: num}))
        col1.formation.update(col2.formation)
        if '0' in or_vec:
            self.columns.append(
                Column(prefix=or_vec, formation=col1.formation))
        else:
            self.chosen_columns.append(col1.formation)
        # columns = [c.prefix for c in self.columns]
        # print(Fore.GREEN + f"After columns: {columns}\n")


class MCTSStateTree:
    def __init__(self, root, m, c, time_limit):
        self.root = root
        self.m = m
        self.c = c
        self.visit = 1
        self.time_limit = time_limit
        self.min_dict = {'min_cost': np.inf, 'min_state': None}

    def selection(self):
        node = self.root
        while node.children:
            node.children.sort(key=lambda x: x.cost +
                               sqrt(2 * log(self.visit) / x.visit))
            node.visit += 1
            self.visit += 1
            node = node.children[0]
        return node

    def expansion(self, node):
        if node.children:
            return
        for i in range(len(node.columns)):
            for j in range(i + 1, len(node.columns)):
                or_value = int(node.columns[i].prefix, 2) | int(
                    node.columns[j].prefix, 2)
                if or_value == int(node.columns[i].prefix, 2) or or_value == int(node.columns[j].prefix, 2):
                    continue
                new_node = MCTSStateNode()
                new_node.parent = node
                new_node.columns = deepcopy(node.columns)
                new_node.chosen_columns = copy(node.chosen_columns)
                new_node.merge(
                    new_node.columns[i], new_node.columns[j])
                if not new_node.columns:
                    cost = 0
                    for c in new_node.chosen_columns:
                        cost += (len(c.keys()) - 1)
                    if cost < self.min_dict['min_cost']:
                        # print(new_node.chosen_columns)
                        self.min_dict['min_cost'] = cost
                        self.min_dict['min_state'] = new_node
                node.children.append(new_node)

    def simulation(self, node):
        new_node = MCTSStateNode()
        new_node.columns = deepcopy(node.columns)
        for _ in range(self.c * (self.m - 1)):
            if len(new_node.columns) == 0:
                break
            indexes = random.sample(range(0, len(new_node.columns)), 2)
            or_value = int(new_node.columns[indexes[0]].prefix, 2) | int(
                new_node.columns[indexes[1]].prefix, 2)
            if or_value == int(new_node.columns[indexes[0]].prefix, 2) or or_value == int(new_node.columns[indexes[1]].prefix, 2):
                continue
            new_node.merge(
                new_node.columns[indexes[0]], new_node.columns[indexes[1]])
            new_node.cost += 1
        node.cost = new_node.cost

    def backpropagation(self, node):
        '''node param is the node which was expanded'''
        tot_cost = 0
        for c in node.children:
            tot_cost += (c.cost / len(node.children))
        while node:
            children_cnt = len(node.children)
            if children_cnt > 0:
                node.cost += tot_cost / children_cnt
            node = node.parent

    def generate_tree(self):
        start = time.time()
        end = start
        while end - start < self.time_limit:
            # print(end - start)
            node = self.selection()
            self.expansion(node)
            for c in node.children:
                self.simulation(c)
            self.backpropagation(node)
            end = time.time()
