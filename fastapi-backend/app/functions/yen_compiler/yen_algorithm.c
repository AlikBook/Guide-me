#include "yen_algorithm.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define MAX_NODES 1000
#define INF INT_MAX

typedef struct Edge {
    int to, cost;
    struct Edge* next;
} Edge;

typedef struct Path {
    int nodes[MAX_NODES];
    int length;
    int cost;
} Path;

Edge* graph[MAX_NODES];

void reset_graph() {
    for (int i = 0; i < MAX_NODES; ++i) {
        while (graph[i]) {
            Edge* temp = graph[i];
            graph[i] = graph[i]->next;
            free(temp);
        }
        graph[i] = NULL;
    }
}

void add_edge(int u, int v, int cost) {
    Edge* edge = (Edge*)malloc(sizeof(Edge));
    edge->to = v;
    edge->cost = cost;
    edge->next = graph[u];
    graph[u] = edge;
}

int dijkstra(int start, int end, int path[], int *pathCost) {
    int dist[MAX_NODES];
    int prev[MAX_NODES];
    int visited[MAX_NODES] = {0};

    for (int i = 0; i < MAX_NODES; ++i) {
        dist[i] = INF;
        prev[i] = -1;
    }

    dist[start] = 0;

    for (int i = 0; i < MAX_NODES; ++i) {
        int u = -1;
        for (int j = 0; j < MAX_NODES; ++j) {
            if (!visited[j] && (u == -1 || dist[j] < dist[u]))
                u = j;
        }

        if (dist[u] == INF) break;

        visited[u] = 1;

        for (Edge* e = graph[u]; e; e = e->next) {
            int v = e->to;
            int cost = e->cost;
            if (dist[u] + cost < dist[v]) {
                dist[v] = dist[u] + cost;
                prev[v] = u;
            }
        }
    }

    if (dist[end] == INF) return 0;

    int len = 0;
    int u = end;
    while (u != -1) {
        path[len++] = u;
        u = prev[u];
    }

    for (int i = 0; i < len / 2; ++i) {
        int temp = path[i];
        path[i] = path[len - 1 - i];
        path[len - 1 - i] = temp;
    }

    *pathCost = dist[end];
    return len;
}

int yen_k_shortest_paths(int start, int end, int k, int result_paths[][MAX_NODES], int* lengths, int* costs) {
    if (k <= 0) return 0;

   
    Path* A = (Path*)malloc(sizeof(Path) * k);
    int aSize = 0;

    // Increase B size to handle more candidates
    Path* B = (Path*)malloc(sizeof(Path) * k * 100);
    int bSize = 0;

    // Find the shortest path first
    int basePath[MAX_NODES];
    int cost;
    int len = dijkstra(start, end, basePath, &cost);
    if (len == 0) {
        free(A);
        free(B);
        return 0;
    }

   

    // Store the first shortest path
    memcpy(A[0].nodes, basePath, sizeof(int) * len);
    A[0].length = len;
    A[0].cost = cost;
    aSize = 1;

    for (int k_index = 1; k_index < k; ++k_index) {
        
        // Generate spur paths for each node in the (k-1)th shortest path
        for (int i = 0; i < A[k_index - 1].length - 1; ++i) {
            int spurNode = A[k_index - 1].nodes[i];
            
            // Root path is the portion from start to spur node
            int rootPath[MAX_NODES];
            memcpy(rootPath, A[k_index - 1].nodes, sizeof(int) * (i + 1));

            // Track removed edges for restoration
            Edge* removedEdges[MAX_NODES] = {NULL};

            // Remove edges that are part of the root path for all paths in A
            for (int j = 0; j < aSize; ++j) {
                // Check if this path shares the same root path
                int match = 1;
                for (int m = 0; m <= i; ++m) {
                    if (A[j].nodes[m] != rootPath[m]) {
                        match = 0;
                        break;
                    }
                }

                // If it matches and has more nodes, remove the edge from spur node
                if (match && A[j].length > i + 1) {
                    int u = A[j].nodes[i];
                    int v = A[j].nodes[i + 1];

                    // Remove edge u -> v temporarily
                    Edge** prev = &graph[u];
                    while (*prev) {
                        if ((*prev)->to == v) {
                            Edge* temp = *prev;
                            *prev = temp->next;
                            temp->next = removedEdges[u];
                            removedEdges[u] = temp;
                            break;
                        }
                        prev = &((*prev)->next);
                    }
                }
            }

            // Find spur path from spur node to destination
            int spurPath[MAX_NODES];
            int spurCost;
            int spurLen = dijkstra(spurNode, end, spurPath, &spurCost);

            // Calculate cost more carefully
            if (spurLen > 0) {
                Path newPath;
                // Copy root path
                memcpy(newPath.nodes, rootPath, sizeof(int) * (i + 1));
                // Copy spur path (excluding the starting node which is already in root)
                memcpy(newPath.nodes + i + 1, spurPath + 1, sizeof(int) * (spurLen - 1));
                newPath.length = i + spurLen;
                
                // Calculate total cost properly
                newPath.cost = 0;
                
                // Cost from start to spur node (already calculated)
                for (int m = 0; m < i; ++m) {
                    int u = newPath.nodes[m];
                    int v = newPath.nodes[m + 1];
                    for (Edge* e = graph[u]; e; e = e->next) {
                        if (e->to == v) {
                            newPath.cost += e->cost;
                            break;
                        }
                    }
                }
                
                // Add spur path cost
                newPath.cost += spurCost;

                // Improved duplicate detection
                int duplicate = 0;
                
                // Check against paths already in A
                for (int a = 0; a < aSize; ++a) {
                    if (A[a].length == newPath.length) {
                        duplicate = 1;
                        for (int x = 0; x < newPath.length; ++x) {
                            if (A[a].nodes[x] != newPath.nodes[x]) {
                                duplicate = 0;
                                break;
                            }
                        }
                        if (duplicate) break;
                    }
                }
                
                // Check against paths in B
                if (!duplicate) {
                    for (int b = 0; b < bSize; ++b) {
                        if (B[b].length == newPath.length) {
                            duplicate = 1;
                            for (int x = 0; x < newPath.length; ++x) {
                                if (B[b].nodes[x] != newPath.nodes[x]) {
                                    duplicate = 0;
                                    break;
                                }
                            }
                            if (duplicate) break;
                        }
                    }
                }

                // Add to B if not duplicate and there's space
                if (!duplicate && bSize < k * 100) {
                    B[bSize++] = newPath;
                }
            }

            for (int u = 0; u < MAX_NODES; ++u) {
                while (removedEdges[u]) {
                    Edge* temp = removedEdges[u];
                    removedEdges[u] = temp->next;
                    temp->next = graph[u];
                    graph[u] = temp;
                }
            }
        }

        if (bSize == 0) {
            break;
        }

        // Find the path with minimum cost from B
        int minIndex = 0;
        for (int i = 1; i < bSize; ++i) {
            if (B[i].cost < B[minIndex].cost)
                minIndex = i;
        }


        A[aSize++] = B[minIndex];

        // Remove the selected path from B
        for (int i = minIndex; i < bSize - 1; ++i)
            B[i] = B[i + 1];
        bSize--;
    }


    for (int i = 0; i < aSize; ++i) {
        for (int j = 0; j < A[i].length; ++j)
            result_paths[i][j] = A[i].nodes[j];
        lengths[i] = A[i].length;
        costs[i] = A[i].cost;
    }

    free(A);
    free(B);
    return aSize;
}
