class Node:
    def __init__(self, prev, trie, cost):
        self.prev = prev
        self.trie = trie
        self.cost = cost


class DecisionTree:
    def __init__(self, root):
        self.root = root
