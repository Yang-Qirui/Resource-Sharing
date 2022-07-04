class Stem:
    def __init__(self, prefix, parent):
        self.parent = parent
        self.prefix = prefix
        self.left = None
        self.right = None

    def set_left(self, node):
        self.left = node

    def set_right(self, node):
        self.right = node


class Leaf:
    def __init__(self, prefix, parent):
        self.parent = parent
        self.prefix = prefix
        self.column_no = []

    def get_no(self):
        number = self.column_no.pop()
        print(f"  Pop column {number} from {self.prefix} node")
        return number

    def append_no(self, no):
        self.column_no.append(no)


class Trie:
    def __init__(self):
        self.root = Stem('', None)
        self.leaf_list = []

    def create_child(self, parent, prefix, is_leaf, is_left):
        if is_leaf:
            new_node = Leaf(prefix, parent)
            self.leaf_list.append(new_node)
        else:
            new_node = Stem(prefix, parent)
        if is_left:
            parent.left = new_node
        else:
            parent.right = new_node

    def insert(self, prefix, no):
        parent = self.root
        for i in range(len(prefix)):
            if prefix[i] == '1':
                if parent.left is None:
                    self.create_child(parent, parent.prefix + '1',
                                      i == (len(prefix) - 1), True)
                parent = parent.left
            else:
                if parent.right is None:
                    self.create_child(parent, parent.prefix + '0',
                                      i == (len(prefix) - 1), False)
                parent = parent.right
            if type(parent) is Leaf:
                parent.append_no(no)

    def delete_no(self, prefix, no):
        parent = self.root
        for i in range(len(prefix)):
            if parent is None:
                raise Exception('Delete a None object')
            if type(parent) is Leaf:
                parent.column_no.remove(no)
                return
            if prefix[i] == '1':
                parent = parent.left
            else:
                parent = parent.right

    def delete_column(self, prefix):
        print(f'  Delete:{prefix}')
        self.leaf_list = list(
            filter(lambda x: x.prefix != prefix, self.leaf_list))
        parent = self.root
        for i in range(len(prefix)):
            if parent is None:
                raise Exception('Delete a None object')
            if prefix[i] == '1':
                parent = parent.left
            else:
                parent = parent.right
        if type(parent) is not Leaf:
            raise Exception('Not arrive leaf node')
        child = parent
        while parent:
            parent = child.parent
            if parent.left == child:
                parent.left = None
            else:
                parent.right = None
            if parent.left is not None or parent.right is not None:
                break
            child = parent

    def find(self, prefix):
        parent = self.root
        for i in range(len(prefix)):
            if parent is None:
                raise Exception('Delete a None object')
            if type(parent) is Leaf:
                parent.get_no()
                if len(parent.column_no) == 0:
                    self.delete(prefix)
                return
            if prefix[i] == '1':
                parent = parent.left
            else:
                parent = parent.right

    def print_node(self):
        list = [self.root]
        cnt = 0
        while True:
            if cnt >= len(list):
                break
            if type(list[cnt]) is Stem:
                if list[cnt].left:
                    list.append(list[cnt].left)
                else:
                    list.append(None)
                if list[cnt].right:
                    list.append(list[cnt].right)
                else:
                    list.append(None)
            cnt += 1
        for node in list:
            if node:
                print(node.prefix)
            else:
                print('NULL')
        print(
            f"\nLeaves:{[(node.prefix,node.column_no) for node in self.leaf_list]}")


def match(trie, string, number_list):
    print(f"Matching {string}")

    def reverse(string):
        inv_string = string.replace('0', '2')
        inv_string = inv_string.replace('1', '0')
        inv_string = inv_string.replace('2', '1')
        return inv_string
    inv_prefix = reverse(string)
    parent = trie.root
    prefix = ''
    for c in inv_prefix:
        origin = parent
        if c == '0':
            parent = parent.right
        else:
            parent = parent.left
        if parent is None:
            if c == '0':
                parent = origin.left
            else:
                parent = origin.right
        prefix += c
        if type(parent) is Leaf:
            or_vec = bin(int(parent.prefix, 2) | int(
                string, 2))[2:].zfill(len(string))
            if '0' in or_vec:
                number = parent.get_no()
                number_list.append(number)
                if len(parent.column_no) == 0:
                    trie.delete_column(parent.prefix)
                xor_vec = bin(int(parent.prefix, 2) ^ int(
                    prefix, 2))[2:].zfill(len(string))
                match(trie, reverse(xor_vec), number_list)
            else:
                number = parent.get_no()
                number_list.append(number)
                if len(parent.column_no) == 0:
                    trie.delete_column(parent.prefix)
                bias = int(parent.prefix, 2)-int(prefix, 2)
                if bias != 0:
                    new_vec = bin(bias)[2:].zfill(len(string))
                    trie.insert(new_vec, number)
            return


def test():
    tree = Trie()
    tree.insert("1101", 0)
    tree.insert("1010", 1)
    tree.insert("0100", 2)
    tree.insert("0011", 3)
    tree.insert("1101", 4)
    # tree.insert("")

    tree.print_node()
    nums = []
    # match('0100', nums)
    match(tree, '0011', nums)
    match(tree, '0011', nums)
    match(tree, '0011', nums)
    print(nums)
    tree.print_node()


if __name__ == "__main__":
    test()
    # main()
