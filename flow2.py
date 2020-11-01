# Python program for implementation of Ford Fulkerson algorithm

from collections import defaultdict

# This class represents a directed graph using adjacency matrix representation


class Graph:

    def __init__(self, graph, source, sink):
        self.source = source
        self.sink = sink
        self.graph = graph  # residual graph
        self.ROW = len(graph)
        self.occupancy = {}
        self.target = 0
        self.sources = set()
        # self.COL = len(gr[0])
        self.occupancy[self.sink] = 0

    def add_source(self, source):
        self.sources.add(source)
        self.graph[self.source][source] = 10
        self.occupancy[source] = 10
        self.target += 10

    def add_sink(self, sink):
        self.graph[sink][self.sink] = float('inf')

    def add_occupancy(self, v, occupancy):
        self.occupancy[v] += occupancy

    def complete_evacuation(self):
        return self.occupancy[self.sink] == self.target

    '''Returns true if there is a path from source 's' to sink 't' in 
	residual graph. Also fills parent[] to store the path '''

    def BFS(self, s, t, parent):

        # Mark all the vertices as not visited
        visited = [False]*(self.ROW)

        # Create a queue for BFS
        queue = []

        # Mark the source node as visited and enqueue it
        queue.append(s)
        visited[s] = True

        # Standard BFS Loop
        while queue:

            # Dequeue a vertex from queue and print it
            u = queue.pop(0)

            # Get all adjacent vertices of the dequeued vertex u
            # If a adjacent has not been visited, then mark it
            # visited and enqueue it
            for ind, val in enumerate(self.graph[u]):
                if visited[ind] == False and val > 0:
                    queue.append(ind)
                    visited[ind] = True
                    parent[ind] = u

        # If we reached sink in BFS starting from source, then return
        # true, else false
        return True if visited[t] else False

    # Returns tne maximum flow from s to t in the given graph

    def FordFulkerson(self):
        source = self.source
        sink = self.sink

        # This array is filled by BFS and to store path
        parent = [-1] * (self.ROW)

        max_flow = 0  # There is no flow initially

        # Augment the flow while there is path from source to sink
        while self.BFS(source, sink, parent):

            # Find minimum residual capacity of the edges along the
            # path filled by BFS. Or we can say find the maximum flow
            # through the path found.
            path_flow = float("Inf")
            s = sink
            while(s != source):
                path_flow = min(path_flow, self.graph[parent[s]][s])
                # if s in self.sources and parent[s] == source:
                #     path_flow = min(path_flow, self.occupancy[s])
                s = parent[s]

            # Add path flow to overall flow
            max_flow += path_flow
            # self.occupancy[self.sink] += path_flow

            # update residual capacities of the edges and reverse edges
            # along the path
            v = sink
            while(v != source):
                u = parent[v]
                self.graph[u][v] -= path_flow
                self.graph[v][u] += path_flow
                # if v in self.sources and u == source:
                #     self.add_occupancy(v, -path_flow)
                #     if self.occupancy[v] <= 0:
                #         self.sources.remove(v)
                #         self.graph[self.source][v] = 0
                v = parent[v]

        return max_flow
