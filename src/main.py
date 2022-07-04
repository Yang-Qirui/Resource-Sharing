import numpy
from trie import Trie
from decision_tree import DecisionTree, Node


def main():
    tree = Trie()
    with open("../matrix.txt", 'r') as f:
        cnt = 0
        line = f.readline().replace(" ", '')
        arr = []
        while line:
            try:
                int(line, 2)
            except:
                raise Exception(f"Line {cnt} is not a pure 01 string")
            row = list(line.strip())
            arr.append(row)
            line = f.readline()
        # print(arr)
        A = numpy.array(arr)
        # print(A.shape)
        column_size = A.shape[1]
        # print(A)
        for i in range(column_size):
            column_string = A[:, i]
            tree.insert(column_string, i)
        f.close()
    tree.print_node()
    d_root = Node(None, tree, 0)
    d_root.get_next()
    d_tree = DecisionTree(d_root)
    # d_tree.generate()


if __name__ == "__main__":
    main()
