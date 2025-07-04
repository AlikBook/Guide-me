#ifndef YEN_ALGORITHM_H
#define YEN_ALGORITHM_H

#define MAX_NODES 1000
#define MAX_K 10

void reset_graph();
void add_edge(int u, int v, int cost);
int yen_k_shortest_paths(int start, int end, int k, int result_paths[][MAX_NODES], int* lengths, int* costs);

#endif
