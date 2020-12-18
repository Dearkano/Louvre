from csv import reader
from flow import FlowEdge, FlowNetwork, max_flow
from flow2 import Graph as Graph2
from flow1 import Graph as Graph1
import datetime
import random
import numpy as np

# import maxflow
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.flow import (
    edmonds_karp,
    shortest_augmenting_path,
    preflow_push,
    dinitz,
    boykov_kolmogorov,
)

FloorF1 = "./data/louvre_fF1.txt"
Floor0 = "./data/louvre_f0.txt"
Floor1 = "./data/louvre_f1.txt"
Floor2 = "./data/louvre_f2.txt"
Stairs = "./data/stair.txt"


def load_data(fp):
    with open(fp) as f:
        r = reader(f, delimiter=" ")
        # f.close()
        return list(r)


def build_origin_graph():
    fps = [FloorF1, Floor0, Floor1, Floor2, Stairs]
    g = FlowNetwork()
    s = set()
    nodes = {}
    _s = 0
    for i, fp in enumerate(fps):
        data = load_data(fp)
        nodes[i] = set()
        for u, v, c, t in data:
            s.add(int(u))
            s.add(int(v))
            nodes[i].add(int(u))
            nodes[i].add(int(v))
            e = FlowEdge(int(u), int(v), int(c), int(t) / 5)
            g.add_edge(e)
            _s += 1
    g.set_N(len(s))
    mapping = {}
    mapping_back = {}
    i = 0
    for v in s:
        mapping[v] = i
        mapping_back[i] = v
        i += 1
    print(_s)
    return g, mapping, mapping_back, nodes


def expand_time_graph(g, mapping, sources, t):
    etg = FlowNetwork()
    etg.set_N(g.N * t + 2)
    super_source = g.N * t
    super_sink = g.N * t + 1
    etg.set_super_source(super_source)
    etg.set_super_sink(super_sink)
    for i in range(t):
        for e_set in g.adj.values():
            for e in e_set:
                e1 = FlowEdge(
                    mapping[e.u] + i * g.N,
                    mapping[e.v] + i * g.N + e.t * g.N,
                    e.capacity,
                    e.t,
                )
                if e1.u < g.N * t and e1.v < g.N * t:
                    etg.add_edge(e1)
                e2 = FlowEdge(
                    mapping[e.v] + i * g.N,
                    mapping[e.u] + i * g.N + e.t * g.N,
                    e.capacity,
                    e.t,
                )
                if e2.u < g.N * t and e2.v < g.N * t:
                    etg.add_edge(e2)
    for source in sources:
        etg.add_source(mapping[source])
    etg.add_sink(mapping[999] + (t - 1) * g.N)
    return etg


def expand_time_graph1(g, mapping, sources, t):
    N = g.N * t + 2
    graph = [[0 for i in range(N)] for i in range(N)]
    super_source = g.N * t
    super_sink = g.N * t + 1
    for i in range(t):
        for e_set in g.adj.values():
            for e in e_set:
                u1 = int(mapping[e.u] + i * g.N)
                v1 = int(mapping[e.v] + i * g.N + e.t * g.N)
                if u1 < g.N * t and v1 < g.N * t:
                    graph[u1][v1] = e.capacity
                u2 = int(mapping[e.v] + i * g.N)
                v2 = int(mapping[e.u] + i * g.N + e.t * g.N)
                if u2 < g.N * t and v2 < g.N * t:
                    graph[u2][v2] = e.capacity
    eg = Graph2(graph, super_source, super_sink)
    for source in sources:
        eg.add_source(mapping[source])
    eg.add_sink(mapping[999] + (t - 1) * g.N)
    return eg


def expand_time_graph2(g, mapping, t):
    N = g.N * t
    graph = maxflow.GraphInt()
    graph.add_nodes(N)
    for i in range(t):
        for e_set in g.adj.values():
            for e in e_set:
                u1 = int(mapping[e.u] + i * g.N)
                v1 = int(mapping[e.v] + i * g.N + e.t * g.N)
                if u1 < g.N * t and v1 < g.N * t:
                    graph.add_edge(u1, v1, e.capacity, 0)
                u2 = int(mapping[e.v] + i * g.N)
                v2 = int(mapping[e.u] + i * g.N + e.t * g.N)
                if u2 < g.N * t and v2 < g.N * t:
                    graph.add_edge(u2, v2, e.capacity, 0)

    # for source in sources:
    #     graph.add_tedge(mapping[source], 100, 0)
    #     for i in range(1, t):
    #         graph.add_edge(mapping[source], mapping[source] + i * g.N, pow(2, 16), 0)
    for i in range(t):
        graph.add_tedge(mapping[999] + i * g.N, 0, pow(2, 16))
    return graph


def binary_search_min_time():
    g, mapping, mapping_back, nodes = build_origin_graph()
    x = []
    y = []
    with open("./result.txt", "w") as f:
        for size in range(1, 101, 1):
            l = 0
            r = 300
            while l < r:
                t = int((l + r) / 2.0)
                expanded_time_graph = expand_time_graph2(g, mapping, t)
                total = 0
                for level in range(len(nodes)):
                    if level < 4:
                        for source in nodes[level]:
                            n = size
                            total += n
                            expanded_time_graph.add_tedge(mapping[source], n, 0)
                            for j in range(5, t, 5):
                                expanded_time_graph.add_edge(
                                    mapping[source],
                                    mapping[source] + j * g.N,
                                    pow(2, 16),
                                    0,
                                )
                value = expanded_time_graph.maxflow()
                print(value)
                print(total)
                if value >= total * 0.9:
                    r = t
                else:
                    l = t + 1
                print("size={}, t={}, value={}".format(size, t, value))
            f.write("size={}, min T={}\n".format(size, l))
            x.append(total)
            y.append(l * 30)
        plt.plot(x, y, "ro")
        plt.xlabel("volume of tourists")
        plt.ylabel("min time")
        plt.show()


def sample_tourists(nodes, ff1, f0, f1, f2):
    sources = random.sample(nodes[0], ff1)
    sources += random.sample(nodes[1], f0)
    sources += random.sample(nodes[2], f1)
    sources += random.sample(nodes[3], f2)
    return sources


def test():
    g, mapping, mapping_back, nodes = build_origin_graph()
    sources = sample_tourists(nodes, 8, 8, 8, 8)
    print(sources)
    expanded_time_graph = expand_time_graph(g, mapping, sources, 80)
    value = max_flow(expanded_time_graph)
    print(value)


def test1():
    g, mapping, mapping_back, nodes = build_origin_graph()
    # sources = sample_tourists(nodes, 8, 8, 8, 8)
    sources = [
        183,
        338,
        105,
        101,
        212,
        400,
        418,
        328,
        715,
        601,
        718,
        663,
        830,
        811,
        845,
        843,
    ]
    print(sources)
    expanded_time_graph = expand_time_graph(g, mapping, sources, 20)
    graph = expanded_time_graph.generate_graph()
    e_g = Graph1(
        graph, expanded_time_graph.super_source, expanded_time_graph.super_sink
    )
    flow = e_g._max_flow_search_FF()
    print(flow)


def test2():
    g, mapping, mapping_back, nodes = build_origin_graph()
    sources = sample_tourists(nodes, 12, 2, 2, 2)
    print(sources)
    expanded_time_graph = expand_time_graph1(g, mapping, sources, 50)
    flow = expanded_time_graph.FordFulkerson()
    print(flow)


def test3():
    g, mapping, mapping_back, nodes = build_origin_graph()
    t = 10
    size = 1
    expanded_time_graph = expand_time_graph2(g, mapping, t)
    for level in range(len(nodes)):
        if level < 4:
            for source in nodes[level]:
                expanded_time_graph.add_tedge(mapping[source], size, 0)
                # for j in range(1, t):
                #     expanded_time_graph.add_edge(
                #         mapping[source],
                #         mapping[source] + j * g.N,
                #         pow(2, 16),
                #         0,
                #     )
    flow = expanded_time_graph.maxflow()
    print(147 * size)
    print(flow)


def build_nx_digraph(g, mapping, people1, people2, t):
    G = nx.DiGraph()
    for i in range(g.N):
        G.add_node(i)
    for i in range(g.N, g.N * t):
        G.add_node(i)
    G.add_node(g.N * t)

    source = g.N * t
    sink = g.N * t + 1

    # add source
    for i in range(g.N):
        G.add_edge(source, i, capacity=random.randint(people1, people2))

    # add sink
    G.add_edge(mapping[999] + (t - 1) * g.N, sink, capacity=1e10)

    for i in range(g.N):
        for j in range(t - 1):
            G.add_edge(i + j * g.N, i + (j + 1) * g.N, capacity=1e10)

    for i in range(t):
        for e_set in g.adj.values():
            for e in e_set:
                e1 = FlowEdge(
                    mapping[e.u] + i * g.N,
                    mapping[e.v] + i * g.N + e.t * g.N,
                    e.capacity,
                    e.t,
                )
                if e1.u < g.N * t and e1.v < g.N * t:
                    G.add_edge(e1.u, e1.v, capacity=e1.capacity)
                e2 = FlowEdge(
                    mapping[e.v] + i * g.N,
                    mapping[e.u] + i * g.N + e.t * g.N,
                    e.capacity,
                    e.t,
                )
                if e2.u < g.N * t and e2.v < g.N * t:
                    G.add_edge(e2.u, e2.v, capacity=e2.capacity)

    return G, source, sink


def test_nx():
    g, mapping, _, _ = build_origin_graph()
    x = []
    y = []
    for p in range(5, 100, 5):
        l = 0
        r = 300
        v = g.N * p
        while l < r:
            t = int((l + r) / 2)
            G, source, sink = build_nx_digraph(g, mapping, p, p, t)
            flowValue, flowDict = nx.maximum_flow(G, source, sink)
            if flowValue >= v * 0.9:
                r = t
            else:
                l = t + 1
        x.append(v)
        y.append(l)
        print("{} in a room, evcuate time = {}".format(p, l))
    plt.plot(x, y, "ro")
    plt.xlabel("volume of tourists")
    plt.ylabel("min evacuation time")
    plt.show()


def test_algos():
    g, mapping, _, _ = build_origin_graph()
    x = []
    y = [[], [], [], [], []]
    algos = [
        preflow_push,
        shortest_augmenting_path,
        dinitz,
        boykov_kolmogorov,
        edmonds_karp,
    ]
    colors = ["red", "black", "green", "blue", "yellow"]
    algo_names = [
        "preflow_push",
        "shortest_augmenting_path",
        "dinitz",
        "boykov_kolmogorov",
        "edmonds_karp",
    ]
    for ind, algo in enumerate(algos):
        for p in range(5, 105, 5):
            l = 0
            r = 150
            v = g.N * p
            start_time = datetime.datetime.now()
            while l < r:
                t = int((l + r) / 2)
                G, source, sink = build_nx_digraph(g, mapping, p, p, t)
                flowValue, flowDict = nx.maximum_flow(G, source, sink, flow_func=algo)
                if flowValue >= v * 0.9:
                    r = t
                else:
                    l = t + 1
            end_time = datetime.datetime.now()
            if ind == 0:
                x.append(v)
            duration = (end_time - start_time).seconds
            y[ind].append(duration)
            print(
                "{} in a room, using {}, run time = {}, evacuation time = {}".format(
                    p, algo_names[ind], duration, l
                )
            )

    for i, line in enumerate(y):
        plt.plot(x, line, "ro", color=colors[i], label=algo_names[i])
    plt.xlabel("volume of tourists")
    plt.ylabel("algo run time")
    plt.show()


def test5():
    G = nx.DiGraph()
    G.add_node("a", demand=-14)
    G.add_node("d", demand=14)
    G.add_edge("a", "b", weight=3, capacity=4)
    G.add_edge("a", "c", weight=6, capacity=10)
    G.add_edge("b", "d", weight=1, capacity=9)
    G.add_edge("c", "d", weight=2, capacity=5)
    flowCost, flowDict = nx.capacity_scaling(G)
    print(flowCost)
    print(flowDict)


if __name__ == "__main__":
    # binary_search_min_time()
    # test_nx()
    # test_algos()
    build_origin_graph()

