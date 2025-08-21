import utils # prédicats
    
class Del_Tri:
    def __init__(self, inftyPoint):
        self.points = []
        self.faces = []
        self.inftyPoint = inftyPoint

    def creates_Tri(self, points):
        self.points = []
        self.faces = []
        for new_point in points:
            self.add_point(new_point)

    def add_point(self, p):
        # Ajoute un point à la triangulation et met à jour les triangles.
        self.points.append(p)

        if len(self.points) < 3:
            return

        if len(self.points) == 3:
            a, b, c = self.points
            if not utils.is_clockwise(a,b,c): # les triangles internes sont clockwise
                b, c = c, b
            self.faces.append((a, b, c))
            self.faces.append((c, b, self.inftyPoint)) # les triangles exterieurs sont orientés dans le même sens 
            self.faces.append((a, c, self.inftyPoint)) # le point a l'infini est toujours le 3eme sommet
            self.faces.append((b, a, self.inftyPoint))
            return
        
        # Étape d'incrémentation : mise à jour des triangles
        self._update_triangulation(p)

    def _update_triangulation(self, p):
        """
        Met à jour la triangulation en ajoutant le point p.
        """
        conflict_zone = []
        # Trouver tous les triangles dont le cercle circonscrit contient p
        for triangle in self.faces:
            a, b, c = triangle
            if c == self.inftyPoint:
                if utils.is_clockwise(a, b, p):
                    conflict_zone.append(triangle)
            else :
                if utils.in_circle(a, b, c, p):
                    conflict_zone.append(triangle)        
    
        # Trouver les aretes de la conflict zone
        edges = []
        for triangle in conflict_zone:
            a, b, c = triangle
            edges += [(a, b), (b, c), (c, a)]        

        # Supprimer les triangles "mauvais"
        for triangle in conflict_zone:
            self.faces.remove(triangle)
        
        # Trouver les arêtes du contour (celles qui ne sont pas partagées)
        boundary = Del_Tri.find_boundary(edges)

        # Créer de nouveaux triangles avec p et chaque arête du contour
        for edge in boundary:
            a, b = edge
            if a == self.inftyPoint:
                self.faces.append((b, p, a))
            elif b == self.inftyPoint:
                self.faces.append((p, a, b))
            else:
                self.faces.append((p, a, b))

    @staticmethod
    def find_boundary(edges):
        """
        Trouve les arêtes du contour : celles qui apparaissent une seule fois.
        """
        boundary = []
        n = len(edges)
        for i in range(n):
            is_unique = True
            for j in range(n):
                a, b = edges[i]
                c, d = edges[j]
                if a == d and b == c:
                    is_unique = False
                    break
            if is_unique:
                boundary.append(edges[i])
        return boundary

class Gabriel:
    def __init__(self, inftyPoint):
        self.points = []
        self.Gab_edges = []
        self.inftyPoint = inftyPoint # on en a besoin car on utilise la tri de Delaunay

    def extract_Gab_from_Del(self, points, Del_Faces):
        # crée le graphe à partir des faces de Delaunay

        # on réinitialise
        self.points = points
        self.Gab_edges = []

        # On extrait les aretes
        # les aretes seront en doubles, mais retirer les doublons serait quadratique...

        Del_edges = []
        for triangle in Del_Faces:
            a, b, c = triangle
            if c == self.inftyPoint:
                continue
            else :
                for i in range(3):
                   Del_edges.append((triangle[i-1], triangle[i]))

        # on extrait les bonnes aretes parmi celle de delaunay
        # à optimiser, là c'est O(n^2)
        for edge in Del_edges:
            good_edge = True
            for p in points:
                # si il existe un point p dans le cercle, on n'ajoute pas l'arete
                if p not in edge:
                    if utils.in_Gab_Circle(edge, p):
                        good_edge = False
                        break
            if good_edge:
                self.Gab_edges.append(edge)

    # non utilisé car plus couteux
    def add_point(self, new_p):
        self.points.append(new_p)
        if len(self.points) < 2:
            return
        if len(self.points) == 2:
            a, b = self.points
            self.Gab_edges.append((a, b))
            return
        self._update_Gabriel(new_p)

    def _update_Gabriel(self, new_p):
        # On supprimer les aretes en conflit
        self.Gab_edges = [edge for edge in self.Gab_edges if not utils.in_Gab_Circle(edge, new_p)]
        # et ajoute les nouvelles aretes (a, p)
        for a in self.points: # on teste si Gab(a,p) contient un point b
            if a != new_p:
                good_edge = True
                for b in self.points:
                    if a != b and b != new_p:
                        # si il existe un point p dans le cercle, on n'ajoute pas l'arete
                        if utils.in_Gab_Circle((a, new_p), b):
                            good_edge = False
                            break
                if good_edge:
                    self.Gab_edges.append((a, new_p))    


if __name__ == "__main__":
    D = Del_Tri("INF")
    points=[(0,0), (1,1), (1,0), (0,1)] #points cocycliques
    D.creates_Tri(points)
    print("points:", D.points)
    
    print(D.faces)