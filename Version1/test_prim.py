from functionsV1 import read_metro_data, prim_mst

# Lire les données depuis le fichier texte
filepath = "Version1/metro.txt"
adjency_matrix, vertices, _ = read_metro_data(filepath)

# Exécuter l'algorithme de Prim
cost, edges = prim_mst(adjency_matrix)

# Affichage des résultats
if cost is not None:
    print(f"\n🌳 Coût total du MST : {cost}")
    print("🔗 Arêtes sélectionnées :")
    for u, v, w in edges:
        print(f"  - {vertices[u][2]} ⇄ {vertices[v][2]} (poids: {w})")
else:
    print("❌ Le graphe n'est pas connexe. Aucun MST possible.")
