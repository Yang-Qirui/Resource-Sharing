class Node:
    def __init__(self):
        self.neighbors = []
        self.deleted = False

    def add_neighbor(self, id):
        self.neighbors.append(id)

    def remove_neighbor(self, id):
        self.neighbors.remove(id)


class Graph:
    def __init__(self, num0, num1):
        self.nodes0 = [Node() for _ in range(num0)]
        self.nodes1 = [Node() for _ in range(num1)]
        self.choosen = []

    def add_edge(self, edge):
        self.nodes0[edge[0]].add_neighbor(edge[1])
        self.nodes1[edge[1]].add_neighbor(edge[0])

    def print_neigh(self):
        print('node0')
        for node in self.nodes0:
            print(node.neighbors)
        print('node1')
        for node in self.nodes1:
            print(node.neighbors)

    def delete_edge(self, edge):
        # print(edge)
        for neighbor in self.nodes0[edge[0]].neighbors:
            self.nodes1[neighbor].remove_neighbor(edge[0])
        for neighbor in self.nodes1[edge[1]].neighbors:
            self.nodes0[neighbor].remove_neighbor(edge[1])
        self.nodes0[edge[0]].deleted = True
        self.nodes1[edge[1]].deleted = True

    def choose_chain(self):

        while list(filter(lambda x: len(x.neighbors) > 0 and not x.deleted, self.nodes0)):
            while list(filter(lambda x: len(x.neighbors) == 1 and not x.deleted, self.nodes0)):
                for i in range(len(self.nodes0)):
                    if len(self.nodes0[i].neighbors) == 1 and not self.nodes0[i].deleted:
                        self.choosen.append((i, self.nodes0[i].neighbors[0]))
                        self.delete_edge((i, self.nodes0[i].neighbors[0]))
            while list(filter(lambda x: len(x.neighbors) > 1 and not x.deleted, self.nodes0)):
                for i in range(len(self.nodes)):
                    if len(self.nodes0[i].neighbors) > 1 and not self.nodes0[i].deleted:
                        self.choosen.append((i, self.nodes0[i].neighbors[0]))
                        self.delete_edge((i, self.nodes0[i].neighbors[0]))
        '''only node without a neighbor was last. TODO: cost function'''
        i = j = 0
        while i < len(self.nodes0) and j < len(self.nodes1):
            if self.nodes0[i].deleted:
                i += 1
            else:
                if self.nodes1[j].deleted:
                    j += 1
                else:
                    self.choosen.append((i, j))
                    i += 1
                    j += 1

        # v = False
        # first = None
        # for i in range(len(self.nodes)):
        #     if not self.nodes[i].deleted:
        #         if not v:
        #             first = i
        #             v = True
        #         else:
        #             self.choosen.append((first, i))
        #             v = False
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
