import numpy as np
import heapq


class PathGrid:

    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, pos):
        self.nodes.append(PathNode(pos, len(self.nodes)))

    def add_edge(self, nodeid_0, nodeid_1, bidirectional=True):
        self.edges.append(PathEdge(self.nodes[nodeid_0], self.nodes[nodeid_1], bidirectional))

    def scale(self, old, new):
        for node in self.nodes:
            node.scale(old, new)

    def dijkstra(self, start, goal):
        matrix = np.zeros((len(self.nodes) + 2, len(self.nodes) + 2))
        for edge in self.edges:
            matrix[edge.start.unid, edge.end.unid] = edge.length
            if edge.bidirectional:
                matrix[edge.end.unid, edge.start.unid] = edge.length

        if isinstance(start, int):
            start_id = start
        else:
            edge = self.get_closest_edge(start)
            matrix[-2, edge.end.unid] = np.linalg.norm(edge.end.pos - start)
            if edge.bidirectional:
                matrix[-2, edge.start.unid] = np.linalg.norm(edge.start.pos - start)
            start_id = len(matrix) - 2

        if isinstance(goal, int):
            start_id = goal
        else:
            edge = self.get_closest_edge(goal)
            matrix[edge.start.unid, -1] = np.linalg.norm(edge.start.pos - goal)
            if edge.bidirectional:
                matrix[edge.end.unid, -1] = np.linalg.norm(edge.end.pos - goal)
            end_id = len(matrix) - 1


    def get_closest_edge(self, point):
        dist = np.zeros(len(self.edges), np.float64)
        for e, edge in enumerate(self.edges):
            proj = np.dot(point - edge.start.pos, edge.vec)
            if proj < 0.0 or proj > edge.length:
                dist[e] = 1e10
                continue
            dist[e] = np.linalg.norm(point - edge.start.pos) / edge.length
        if len(dist[dist < 1e9]) == 0:
            raise ValueError("Something is very wrong")
        return self.edges[np.argmin(dist)]

class PathNode(object):

    def __init__(self, pos, unid):
        self.pos = pos
        self.unid = unid # unique node id

        self.connected_to = []
        self.incoming_edges = []
        self.outgoing_edges = []

    def scale(self, old, new):
        self.pos = self.pos / old * new


class PathEdge:

    def __init__(self, start, end, bidirectional=True):
        self.start = start
        self.end = end
        self.bidirectional = bidirectional

        if end.unid not in start.connected_to:
            start.connected_to.append(end.unid)
        self.start.outgoing_edges.append(self)
        self.end.incoming_edges.append(self)

    @property
    def vec(self):
        return self.end.pos - self.start.pos

    @property
    def length(self):
        return np.linalg.norm(self.vec)

    @property
    def direction(self):
        return self.vec / self.length


class DijkstraNode:

    def __init__(self, unid):
        self.unid = unid
        self.dist = np.inf
        self.prev = None

    def path(self):
        if self.prev is not None:
            return self.prev.path() + [self.unid]
        return [self.unid]

    def __lt__(self, other):
        if self.dist == other.dist:
            return self.unid < other.unid
        return self.dist < other.dist
