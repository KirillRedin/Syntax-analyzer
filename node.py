class Node:
    def __init__(self, data, depth):
        self.children = []
        self.data = data
        self.depth = depth

    def add_child(self, node):
        self.children.append(node)
        return node

    def print(self):
        for i in range(0, self.depth):
            print('..', end='')

        print(self.data)

        for child in self.children:
            child.print()
