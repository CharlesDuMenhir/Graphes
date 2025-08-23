class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))  # Chaque élément est son propre parent
        self.rank = [0] * n           # Rangs pour optimiser les unions

    def find(self, x):
        # Compression de chemin : raccourcit les branches
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        # Trouver les racines
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # Déjà connectés

        # Union par rang : attache l’arbre le plus petit sous le plus grand
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        else:
            self.parent[ry] = rx
            if self.rank[rx] == self.rank[ry]:
                self.rank[rx] += 1
        return True
