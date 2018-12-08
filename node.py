class Node:
    def __init__(self, data, depth):
        self.children = []
        self.data = data
        self.depth = depth

    def add_child(self, data):
        node = Node(data, self.depth + 1)
        self.children.append(node)
        return node
