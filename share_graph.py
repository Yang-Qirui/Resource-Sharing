class Node:
    def __init__(self):
        self.neighbors = []
        self.deleted = False

    def add_neighbor(self, id):
        self.neighbors.append(id)

    def remove_neighbor(self, id):
        self.neighbors.remove(id)


class Graph:
    def __init__(self, num):
        self.nodes = []
        for _ in range(num):
            self.nodes.append(Node())
        # self.nodes = [Node()] * num
        # self.deleted = [False] * num
        self.choosen = []

    def add_edge(self, edge):
        self.nodes[edge[0]].add_neighbor(edge[1])
        self.nodes[edge[1]].add_neighbor(edge[0])

    def print_neigh(self):
        for node in self.nodes:
            print(node.neighbors)

    def delete_edge(self, edge):
        # print(edge)
        for neighbor in self.nodes[edge[0]].neighbors:
            self.nodes[neighbor].remove_neighbor(edge[0])
        for neighbor in self.nodes[edge[1]].neighbors:
            self.nodes[neighbor].remove_neighbor(edge[1])
        self.nodes[edge[0]].deleted = True
        self.nodes[edge[1]].deleted = True

    def choose_chain(self):
        while list(filter(lambda x: len(x.neighbors) > 0 and not x.deleted, self.nodes)):
            while list(filter(lambda x: len(x.neighbors) == 1 and not x.deleted, self.nodes)):
                for i in range(len(self.nodes)):
                    if len(self.nodes[i].neighbors) == 1 and not self.nodes[i].deleted:
                        self.choosen.append((i, self.nodes[i].neighbors[0]))
                        self.delete_edge((i, self.nodes[i].neighbors[0]))
            while list(filter(lambda x: len(x.neighbors) > 1 and not x.deleted, self.nodes)):
                for i in range(len(self.nodes)):
                    if len(self.nodes[i].neighbors) > 1 and not self.nodes[i].deleted:
                        self.choosen.append((i, self.nodes[i].neighbors[0]))
                        self.delete_edge((i, self.nodes[i].neighbors[0]))
        '''only node without a neighbor was last. TODO: cost function'''
        v = False
        first = None
        for i in range(len(self.nodes)):
            if not self.nodes[i].deleted:
                if not v:
                    first = i
                    v = True
                else:
                    self.choosen.append((first, i))
                    v = False
        return self.choosen


def test():
    g = Graph(6)
    g.add_edge((0, 3))
    g.add_edge((0, 4))
    g.add_edge((0, 5))
    g.add_edge((1, 3))
    g.add_edge((2, 3))
    g.add_edge((2, 4))
    # g.print_neigh()
    print(g.choose_chain())
