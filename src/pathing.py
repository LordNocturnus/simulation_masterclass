import numpy as np


class PathGrid:

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.id_counter = 0

    def add_node(self, pos):
        self.nodes.append(PathNode(pos, self.id_counter))
        self.id_counter += 1

    def add_edge(self, nodeid_0, nodeid_1, bidirectional=True):
        self.edges.append(PathEdge(self.nodes[nodeid_0], self.nodes[nodeid_1]))
        if bidirectional:
            self.edges.append(PathEdge(self.nodes[nodeid_1], self.nodes[nodeid_0]))

    def scale(self, old, new):
        for node in self.nodes:
            node.scale(old, new)



class PathNode(object):

    def __init__(self, pos, unid):
        self.pos = pos
        self.unid = unid # unique node id

        self.connected_to = []

    def scale(self, old, new):
        self.pos = self.pos / old * new


class PathEdge:

    def __init__(self, start, end):
        self.start = start
        self.end = end

        if end.unid not in start.connected_to:
            start.connected_to.append(end.unid)

    @property
    def length(self):
        return np.linalg.norm(self.start.pos - self.end.pos)