from collections import deque
import numpy as np


class FlowEdge:
    def __init__(self, u, v, c, t):
        self.u = u
        self.v = v
        self.capacity = c
        self.t = t
        self.flow = 0

    def __repr__(self):
        return "|u={}, v={}, c={}, t={}, f={}|".format(
            self.u, self.v, self.capacity, self.t, self.flow
        )

    def residual_capacity(self, to):
        if self.u == to:
            return self.flow
        elif self.v == to:
            return self.capacity - self.flow
        else:
            raise Exception("Illegal vertex")

    def add_residual_flow(self, to, val):
        if self.u == to:
            self.flow -= val
        elif self.v == to:
            self.flow += val
        else:
            raise Exception("Illegal vertex")


class FlowNetwork:
    def __init__(self):
        self.N = 0
        self.adj = {}
        self.occupancy = {}
        self.super_source = None
        self.super_sink = None
        self.target = 0
        self.sources = set()
        self.sinks = set()

    def add_edge(self, e):
        if e.u not in self.adj:
            self.adj[e.u] = list([])
        if e.v not in self.adj:
            self.adj[e.v] = list([])
        self.adj[e.u].append(e)
        self.adj[e.v].append(e)

    def set_N(self, N):
        self.N = N

    def set_super_source(self, source):
        self.super_source = source

    def add_source(self, source):
        self.sources.add(source)
        self.set_occupancy(source, 10)
        self.add_edge(FlowEdge(self.super_source, source, 10, 0))

    def set_super_sink(self, sink):
        self.super_sink = sink
        self.occupancy[sink] = 0

    def add_sink(self, sink):
        self.sinks.add(sink)
        self.add_edge(FlowEdge(sink, self.super_sink, float('inf'), 0))

    def delete_edge(self, u, v):
        for e in self.adj[u]:
            if e.v == v:
                self.adj[u].remove(e)

    def delete_source(self, source):
        self.sources.remove(source)
        self.delete_edge(self.super_source, source)

    def set_occupancy(self, v, occupancy):
        self.occupancy[v] = occupancy
        self.target += occupancy

    def add_occupancy(self, v, occupancy):
        self.occupancy[v] += occupancy

    def evacuation_complete(self):
        return self.occupancy[self.super_sink] == self.target

    def generate_graph(self):
        graph = np.zeros((self.N, self.N))
        for edges in self.adj.values():
            for e in edges:
                graph[e.u][e.v] = e.capacity
        return graph


def max_flow(G):
    E = {}
    value = 0
    s = G.super_source
    t = G.super_sink
    p = G.adj[G.super_source]

    def find_augment_path(u, v):
        E.clear()
        marked = [False for i in range(G.N)]
        queue = deque([])
        queue.append(u)
        marked[u] = True

        while len(queue) > 0:
            cur = queue.popleft()
            for e in G.adj[cur]:
                w = e.u if cur == e.v else e.v
                w = int(w)
                if e.residual_capacity(w) > 0 and marked[w] is False:
                    E[w] = e
                    marked[w] = True
                    queue.append(w)

        return marked[v]

    while find_augment_path(s, t) is True:
        bottle = float("inf")
        cur = t
        while cur != s:
            bottle = min(bottle, E[cur].residual_capacity(cur))
            # if cur in G.sources and E[cur].u == s or E[cur].v == s:
            #     bottle = min(bottle, G.occupancy[cur])
            cur = E[cur].u if cur == E[cur].v else E[cur].v
        cur = t
        while cur != s:
            E[cur].add_residual_flow(cur, bottle)
            # if cur in G.sources and E[cur].u == s or E[cur].v == s:
            #     G.add_occupancy(cur, -bottle)
            #     if G.occupancy[cur] <= 0:
            #         G.delete_source(cur)
            cur = E[cur].u if cur == E[cur].v else E[cur].v
        value += bottle
        # G.add_occupancy(t, bottle)

    return value
