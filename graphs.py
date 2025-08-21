import random

import geom # prédicats

class Dart:
    # https://fr.wikipedia.org/wiki/Carte_combinatoire
    def __init__(self, vertex):
        self.vertex = vertex  # Coordonnées du sommet de départ
        self.twin = None    # Brin opposé (même arête, sens inverse)
        self.next = None    # Brin suivant cw dans la face

    def __repr__(self):
        return f"Dart from ({self.vertex}) to ({self.twin.vertex})"

    @property
    def alpha1(self):
        # Brin suivant cw-autour du sommet
        return self.twin.next
    
    @property
    def is_infinite(self):
        if self.vertex == geom.INF_P or self.twin.vertex == geom.INF_P:
            return True
        return False
    
    @property    
    def get_dart_vertices(self):
        # Renvoie tous les sommets du dart
        a = self.vertex
        b = self.twin.vertex
        return (a, b)
    
    @property
    def get_cycle(self):
        # Renvoie tous les darts du cycle
        darts = [self]
        current_d = self.next
        while current_d is not self:
            darts.append(current_d)
            current_d = current_d.next
        return darts

    @property
    def get_cycle_vertices(self):
        # Renvoie tous les sommets du cycle
        return [d.vertex for d in self.get_cycle]
    
    def is_cycle(self,n):
        i = 1
        d = self.next
        while d is not self and i <= n:
            i += 1
            d = d.next
        return i == n

    @staticmethod
    def set_twin_each_other(d_ab, d_ba):
        d_ab.twin, d_ba.twin = d_ba, d_ab

    @staticmethod
    def set_next_each_other(darts):
        for i in range(len(darts)):
            darts[i-1].next = darts[i]

    def flip(self): #
        # dans une face aqbp flip d_ab en d_qp
        d_ab, d_bp, d_pa = self.get_cycle
        # les 3 darts de aqb
        d_ba, d_aq, d_qb = self.twin.get_cycle
        # flip des sommets
        d_ab.vertex = d_qb.vertex
        d_ba.vertex = d_pa.vertex
        d_qp, d_pq = d_ab, d_ba # on renomme juste pour la lisibilité
        # maj des pointages next
        tri_aqp = [d_aq, d_qp, d_pa]
        Dart.set_next_each_other(tri_aqp)
        tri_bpq = [d_bp, d_pq, d_qb]
        Dart.set_next_each_other(tri_bpq)
    

class Delaunay_Triangulation:
    def __init__(self):
        self.vertices = []
        self.darts = [] # chaque dart stocké correspond à une face

    @property
    def edges(self):
        edges = []
        for dart in self.darts:
            edge = geom.Oriented_Edge(dart.get_dart_vertices) 
            if not edge.is_infinite and edge.has_0_on_left: # on écrate les aretes infinies et les doublons
                edges.append(edge.vertices)
        return edges


    @property
    def is_triangulation(self):
        for d in self.darts:
            if not d.is_cycle(3):
                return False
        return True

    def build(self, points):
        for p in points:
            self.insert_point(p)

    def insert_point(self, p):
        self.vertices.append(p)
        if len(self.vertices) == 1:
            return
        if len(self.vertices) == 2:
            if p == self.vertices[0]:
                self.vertices.pop()
            return
        if len(self.vertices) == 3:
            if p == self.vertices[0] or p == self.vertices[1]:
                self.vertices.pop()
            else:
                self._init_triangle(self.vertices)
            return
        # si la triangulation est déjà créee, on insert le point
        self._insert_in_Delaunay(p)

    def _insert_in_Delaunay(self, p):
        """
        Insert point p
        Met à jour les darts
        """
        dart = self.find_face_of(p) # On trouve une face en conflit
        if dart == "Point deja existant":
            self.vertices.pop()
            print("Point non ajouté")
            return
        darts_to_flip = self._init_new_darts(dart, p) # On relie la triangualtion avec les nouveaux darts
        for dart in darts_to_flip: # Et on rétablit recursivement la propriété de Delanuay
            Delaunay_Triangulation._flip_until_Del(dart)

    @staticmethod
    def _flip_until_Del(dart): #O(1) en moyenne
        # recursivement ReDelaunayise après l'ajout d'un point dans un face
        d_ab = dart
        # les 2 darts qu'il faudra aussi checker si flip
        d_aq = d_ab.alpha1 
        d_qb = d_aq.next
        triangle = geom.Oriented_Triangle(d_ab.get_cycle_vertices)
        if triangle.is_in_conflict(d_qb.vertex):
            d_ab.flip()
            Delaunay_Triangulation._flip_until_Del(d_aq)
            Delaunay_Triangulation._flip_until_Del(d_qb)

    def _init_triangle(self, triangle): # triangle est tuple de 3 sommets
        a, b, c = triangle
        if not geom.are_clockwise(a, b, c): # les triangles internes sont clockwise
            b, c = c, b
        # on crée les 12 nouveaux darts du premier triangles (6 finis, 6 infinis)
        internal_darts = [Dart(a), Dart(b), Dart(c)]
        self.darts.extend(internal_darts)
        external_darts = [Dart(b), Dart(c), Dart(a)]
        self.darts.extend(external_darts)
        infinite_darts_to_inf = [Dart(a), Dart(b), Dart(c)]
        self.darts.extend(infinite_darts_to_inf)
        infinite_darts_from_inf = [Dart(geom.INF_P), Dart(geom.INF_P), Dart(geom.INF_P)]
        self.darts.extend(infinite_darts_from_inf)
        # on met à jour leurs liens
        Dart.set_next_each_other(internal_darts)
        for i in range(3):
            Dart.set_twin_each_other(internal_darts[i], external_darts[i])
            Dart.set_twin_each_other(infinite_darts_to_inf[i], infinite_darts_from_inf[i])
            external_darts[i].next = infinite_darts_to_inf[i]
            infinite_darts_to_inf[i].next = infinite_darts_from_inf[(i+1)%3]
            infinite_darts_from_inf[i].next = external_darts[i-1]


    def _init_new_darts(self, dart, p):
        """
            Crée et initialise les darts liés à l'ajout du point p. On n'a temporairement plus une triangulation de Delaunay.
            Renvoie les darts qu'il faut tester et flipper si necessaires 
        """ 
        triangle_darts = dart.get_cycle
        # création et ajout des 6 nouveaux darts
        new_darts_from_p = [Dart(p), Dart(p), Dart(p)]
        new_darts_to_p = [Dart(d.vertex) for d in triangle_darts]
        self.darts.extend(new_darts_from_p)
        self.darts.extend(new_darts_to_p)
        # mise à jour des alpha 0
        for i in range(3):
            Dart.set_twin_each_other(new_darts_from_p[i], new_darts_to_p[i])
        # mise à jour des alpha 2
        for i in range(3):
            new_darts_from_p[i].next = triangle_darts[i]
            triangle_darts[i].next = new_darts_to_p[(i+1)%3]
            new_darts_to_p[i].next = new_darts_from_p[(i+2)%3]
        return triangle_darts

    def find_face_of(self, target):
        """
            Renvoie un dart dont la face contient p ou est visible par p si infinie
        """ 
        dart = random.choice(self.darts) # On part d'un dart random
        triangle = geom.Oriented_Triangle(dart.get_cycle_vertices)
        if triangle.is_infinite: # si c'est une face infinie, on change de dart pou rentrer dans l'enveloppe convexe
            while dart.is_infinite:
                dart = dart.next
            dart = dart.twin # on switch à l'intérieur si on est tombé sur une face infinie
            triangle = geom.Oriented_Triangle(dart.get_cycle_vertices)
        source = geom.gravity_center(dart.get_cycle_vertices) # on part du centre du triangle choisi
        while not triangle.is_visible_from(target):
            crossing_d = Delaunay_Triangulation._find_crossing_dart(dart, source, target)
            dart = crossing_d.twin # on passe à la face suivante
            triangle = geom.Oriented_Triangle(dart.get_cycle_vertices)
            if triangle.is_infinite:
                break # dans ce cas, target est hors de l'enveloppe convexe, comme on en vient, dart est visible par target
        if target in triangle.vertices:
            return "Point deja existant"
        return dart
    
    @staticmethod
    def _find_crossing_dart(d, source, target):
        # d : un dart de la face, à part à l'initialisation, c'est le dart de depart.
        # renvoie le dart de la face qui intersect source-target
        found = False
        while not found:
            d = d.next # donc on teste deja d.next
            a = d.vertex
            b = d.twin.vertex
            found = geom.segments_intersect(source, target, a, b)
        return d
    

#-------------------------Graphe de Gabriel-----------------------

class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = []

    def extract_Gab_from_Del(self, DT):
        # Extrait le graphe de Gabriel à partir des faces de Delaunay
        self.vertices = DT.vertices
        for dart in DT.darts:
            edge = geom.Oriented_Edge(dart.get_dart_vertices) 
            if not edge.is_infinite and edge.has_0_on_left: # on ne prend qu'une arete sur 2
                p = dart.next.next.vertex
                q = dart.twin.next.next.vertex               
                if not(edge.Gab_Circle_contains(p) or edge.Gab_Circle_contains(q)):
                    self.edges.append(edge.vertices)

    def extract_RNG_from_Del(self, DT):
        # Extrait le RNG à partir des faces de Delaunay

        self.vertices = DT.vertices
        for dart in DT.darts:
            if not dart.is_infinite and dart.has_0_on_left: # on ne prend qu'un arete sur 2
                p = dart.next.next.vertex
                q = dart.twin.next.next.vertex
                edge = geom.Oriented_Edge(dart.get_dart_vertices)                
                if not(edge.Gab_Circle_contains(p) or edge.Gab_Circle_contains(q)):
                    self.darts.append(dart)





if __name__ == "__main__":
    points = []
    for _ in range(60):
        x = random.random()
        y = random.random()
        points.append((x, y))
    DT = Delaunay_Triangulation()
    DT.build(points)
    print(DT.is_triangulation)
