from functionsV1 import is_connected

# Exemple 1 : graphe connexe (3 sommets, tous reliés)
G1 = [
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0]
]

# Exemple 2 : graphe non connexe (3 sommets, 1 isolé)
G2 = [
    [0, 0, 0],
    [0, 0, 1],
    [0, 1, 0]
]

print("G1 connexe ?", is_connected(G1))   # ✅ Doit afficher True
print("G2 connexe ?", is_connected(G2))   # ❌ Doit afficher False
