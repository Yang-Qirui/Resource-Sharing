from copy import deepcopy
from colorama import Fore, init
import numpy

from trie import match
init(autoreset=True)


class Node:
    def __init__(self, prev, trie, cost):
        self.prev = prev
        self.trie = trie
        self.cost = cost
        self.next = []

    def get_next(self):
        for i in range(len(self.trie.leaf_list)):
            new_trie = deepcopy(self.trie)
            number_list = []
            match(new_trie, new_trie.leaf_list[i].prefix, number_list)
            # print('NEW_TRIE')
            # new_trie.print_node()
            new_trie.leaf_list[i].column_no.pop()
            if len(new_trie.leaf_list[i].column_no) == 0:
                new_trie.delete_column(new_trie.leaf_list[i].prefix)
            print(Fore.GREEN + f"Chosen columns:{number_list}")
            print(Fore.BLUE + f"Cost:{len(number_list)}\n")


class DecisionTree:
    def __init__(self, root):
        self.root = root
        self.minimum_cost = numpy.inf
