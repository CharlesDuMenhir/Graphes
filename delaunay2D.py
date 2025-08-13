import utils # prédicats
    
class Del_Tri:
    def __init__(self, inftyPoint):
        self.points = []
        self.faces = []
        self.inftyPoint = inftyPoint

    def creates_Tri(self, points):
        for new_point in points:
            self.add_point(new_point)

    def add_point(self, p):
        """
        Ajoute un point à la triangulation et met à jour les triangles.
        """
        self.points.append(p)

        if len(self.points) < 3:
            return

        if len(self.points) == 3:
            a, b, c = self.points
            if not utils.isClockwise(a,b,c): #le triangles internes sont clockwise
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
                if utils.isClockwise(a, b, p):
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
        boundary = self._find_boundary(edges)

        # Créer de nouveaux triangles avec p et chaque arête du contour
        for edge in boundary:
            a, b = edge
            if a == self.inftyPoint:
                self.faces.append((b, p, a))
            elif b == self.inftyPoint:
                self.faces.append((p, a, b))
            else:
                self.faces.append((p, a, b))

    def _find_boundary(self, edges):
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


if __name__ == "__main__":
    D = Del_Tri("INF")
    points=[(0,0), (2,2), (4,0), (-1,-1), (1,0)]
    D.creates_Tri(points)
    print("points:", D.points)
    print(D.faces)