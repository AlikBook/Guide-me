# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True

cdef extern from "yen_algorithm.h":
    void reset_graph()
    void add_edge(int u, int v, int cost)
    int yen_k_shortest_paths(int start, int end, int k,
                             int result_paths[][1000], int* lengths, int* costs)

def get_k_shortest_paths(edges, int start, int end, int k):
    reset_graph()
    for u, v, cost in edges:
        add_edge(u, v, cost)

    cdef int result_paths[10][1000]  # max k = 10, max nodes = 1000
    cdef int lengths[10]
    cdef int costs[10]

    cdef int found = yen_k_shortest_paths(start, end, k, result_paths, lengths, costs)

    paths = []
    for i in range(found):
        path = [result_paths[i][j] for j in range(lengths[i])]
        paths.append((costs[i], path))
    return paths
