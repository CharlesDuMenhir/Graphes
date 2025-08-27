
# Faire un make_set par objet dont on veut faire des unions

def make_set(x):
    x.parent = x  # Chaque élément est son propre parent
    x.rank = 0    # Rangs pour optimiser les unions

def find(x):    # usuel find
    # renvoie le représentant. + Compression de chemin : raccourcit les branches
    if x.parent != x:
        x.parent = find(x.parent)
    return x.parent

def union(x, y):
    # Trouver les racines
    rx, ry = find(x), find(y)
    if rx == ry:
        return False  # Déjà connectés

    # Union par rang : attache l’arbre le plus petit sous le plus grand
    if rx.rank < ry.rank:
        rx.parent = ry
    else:
        ry.parent = rx
        if rx.rank == ry.rank:
            rx.rank += 1
    return True
