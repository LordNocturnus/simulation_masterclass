import numpy as np
import heapq

from src.TracedResource import TracedResource


class PathGrid:

    def __init__(self, env):
        self.env = env
        self.nodes = []
        self.edges = []
        self.sorted_edges = dict()
        self.matrix = np.zeros((0, 0))

    def add_node(self, pos):
        self.nodes.append(PathNode(pos, len(self.nodes)))

    def add_edge(self, nodeid_0, nodeid_1, bidirectional=True, departments=None, narrow=False):
        self.edges.append(PathEdge(self.env, self.nodes[nodeid_0], self.nodes[nodeid_1], bidirectional, narrow))
        if departments is not None:
            for dep in departments:
                if dep not in self.sorted_edges:
                    self.sorted_edges[dep] = []
                self.sorted_edges[dep].append(self.edges[-1])


    def scale(self, old, new):
        for node in self.nodes:
            node.scale(old, new)
        for edge in self.edges:
            edge.scale()
        self.matrix = np.zeros((len(self.nodes), len(self.nodes)))
        for edge in self.edges:
            self.matrix[edge.start.unid, edge.end.unid] = edge.length
            if edge.bidirectional:
                self.matrix[edge.end.unid, edge.start.unid] = edge.length

    def dijkstra(self, start, goal, dep_0, dep_1):
        """
         Dijkstra algorithm for pathfinding on a graph. returns a list of node indices along which to travel for
         shortest path
        """
        matrix = np.zeros((len(self.nodes) + 2, len(self.nodes) + 2))
        matrix[:-2, :-2] = self.matrix

        if isinstance(start, int):
            start_id = start
        else:
            edge = self.get_closest_edge(start, dep_0)
            matrix[-2, edge.end.unid] = np.linalg.norm(edge.end.pos - start)
            if edge.bidirectional:
                matrix[-2, edge.start.unid] = np.linalg.norm(edge.start.pos - start)
            start_id = len(matrix) - 2

        if isinstance(goal, int):
            goal_id = goal
        else:
            edge = self.get_closest_edge(goal, dep_1)
            matrix[edge.start.unid, -1] = np.linalg.norm(edge.start.pos - goal)
            if edge.bidirectional:
                matrix[edge.end.unid, -1] = np.linalg.norm(edge.end.pos - goal)
            goal_id = len(matrix) - 1

        nodes = []
        for node in range(len(matrix)):
            nodes.append(DijkstraNode(node))

        nodes[start_id].dist = 0.0
        open_list = []
        heapq.heappush(open_list, nodes[start_id])
        while len(open_list) > 0:
            current_node = heapq.heappop(open_list)
            if current_node.unid == goal_id:
                return current_node.path()
            for node_id, dist in enumerate(matrix[current_node.unid]):
                if dist == 0.0:
                    continue
                if nodes[node_id].dist > current_node.dist + dist:
                    nodes[node_id].dist = current_node.dist + dist
                    nodes[node_id].prev = current_node
                    heapq.heappush(open_list, nodes[node_id])


    def get_closest_edge(self, point, dep):
        # find physically closest edge to a given point
        if dep is None:
            edges = self.edges
        else:
            edges = self.sorted_edges[dep]
        dist = np.zeros(len(edges), np.float64) # technically dist^2 for calculation efficiency
        proj = np.zeros(len(edges), np.float64)
        for e, edge in enumerate(edges):
            proj[e] = np.dot(point - edge.start.pos, edge.vec) / edge.length
            if proj[e] < 0.0 or proj[e] > edge.length:
                # anchorpoint for normal between point and edge lies outside of edge change calculation to distance from
                # start or end point whichever is shorter
                dist[e] = min(np.sum(np.square(point - edge.start.pos)), np.sum(np.square(point - edge.end.pos)))
                continue
            dist[e] = np.sum(np.square(np.cross(point - edge.start.pos, edge.vec))) / edge.length ** 2

        return edges[np.argmin(dist)]

class PathNode(object):

    def __init__(self, pos, unid):
        self.pos = pos
        self.unid = unid # unique node id

        self.incoming_edges = {}
        self.outgoing_edges = {}

    def scale(self, old, new):
        self.pos = self.pos / old * new


class PathEdge:

    def __init__(self, env, start, end, bidirectional, narrow):
        self.env = env
        self.start = start
        self.end = end
        self.bidirectional = bidirectional
        if narrow:
            self.blockage = TracedResource(env, 1, f"{start.unid}-{end.unid}")
        else:
            self.blockage = None

        self.vec = self.end.pos - self.start.pos
        self.length = np.linalg.norm(self.vec)
        self.direction = self.vec / self.length

        self.start.outgoing_edges[end.unid] = self
        self.end.incoming_edges[start.unid] = self
        if self.bidirectional:
            self.end.outgoing_edges[start.unid] = self
            self.start.incoming_edges[end.unid] = self

    def scale(self):
        self.vec = self.end.pos - self.start.pos
        self.length = np.linalg.norm(self.vec)
        self.direction = self.vec / self.length


class DijkstraNode:

    def __init__(self, unid):
        self.unid = unid
        self.dist = np.inf
        self.prev = None

    def path(self):
        if self.prev is not None:
            return self.prev.path() + [self.unid]
        return []

    def __lt__(self, other):
        if self.dist == other.dist:
            return self.unid < other.unid
        return self.dist < other.dist
