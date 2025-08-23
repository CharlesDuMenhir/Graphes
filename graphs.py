import random
import heapq # pour le MST

import geom # prédicats

class Dart:
    # https://fr.wikipedia.org/wiki/Carte_combinatoire
    def __init__(self, origin):
        self.origin = origin  # Coordonnées du sommet de départ
        self.twin = None    # Brin opposé (même arête, sens inverse)
        self.next = None    # Brin suivant cw dans la face

    def __repr__(self):
        return f"Dart from ({self.origin}) to ({self.twin.origin})"

    @property
    def target(self):
        # Brin suivant cw-autour du sommet
        return self.next.origin

    @property
    def alpha1(self):
        # Brin suivant cw-autour du sommet
        return self.twin.next
    
    @property
    def is_infinite(self):
        if self.origin == geom.INF_P or self.twin.origin == geom.INF_P:
            return True
        return False
    
    @property    
    def vertices(self):
        # Renvoie tous les sommets du dart
        a = self.origin
        b = self.target
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
        return [d.origin for d in self.get_cycle]
    
    @property
    def neighbors(self):
        darts = [self]
        current_d = self.alpha1
        while current_d is not self:
            darts.append(current_d)
            current_d = current_d.alpha1
        return darts
    
    @property
    def neighbors_vertices(self):
        # Renvoie tous les sommets du cycle
        return [d.target for d in self.neighbors]
    
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
        d_ab.origin = d_qb.origin
        d_ba.origin = d_pa.origin
        d_qp, d_pq = d_ab, d_ba # on renomme juste pour la lisibilité
        # maj des pointages next
        tri_aqp = [d_aq, d_qp, d_pa]
        Dart.set_next_each_other(tri_aqp)
        tri_bpq = [d_bp, d_pq, d_qb]
        Dart.set_next_each_other(tri_bpq)
    
class Graph:
    def reset(self):
        self.__init__()

class Delaunay_Triangulation(Graph):
    def __init__(self):
        self.vertices = []
        self.darts = [] # chaque dart stocké correspond à une face

    @property
    def edges(self):
        edges = []
        for dart in self.darts:
            edge = geom.Oriented_Edge(dart.vertices) 
            if not edge.is_infinite and edge.has_0_on_left: # on écarte les aretes infinies et les doublons
                edges.append(edge.vertices)
        return edges

    @property
    def is_triangulation(self):
        for d in self.darts:
            if not d.is_cycle(3):
                return False
        return True

    def build(self, points):
        self.vertices = []
        self.darts = []
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
        Insert point p. Met à jour les darts
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
        """
        ReDelaunayise recursivement après l'ajout d'un point dans un face.
        Méthode de Lawson (je crois)
        """
        d_ab = dart
        # les 2 darts qu'il faudra aussi checker si flip
        d_aq = d_ab.alpha1
        d_qb = d_aq.next
        triangle = geom.Oriented_Triangle(d_ab.get_cycle_vertices)
        if triangle.is_in_conflict(d_qb.origin):
            d_ab.flip()
            Delaunay_Triangulation._flip_until_Del(d_aq)
            Delaunay_Triangulation._flip_until_Del(d_qb)

    def _init_triangle(self, triangle): # triangle est tuple de 3 sommets
        """
            Crée et initialise les darts du premier triangle
        """ 
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
        new_darts_to_p = [Dart(d.origin) for d in triangle_darts]
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
        while not triangle.contains(target):
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
            a = d.origin
            b = d.target
            found = geom.segments_intersect(source, target, a, b)
        return d
    

#-------------------------Graphe de Gabriel-----------------------

class Gabriel_Graph(Graph):
    def __init__(self):
        self.edges = []

    def extract_from_Del(self, DT):
        # Extrait le graphe de Gabriel à partir des aretess de Delaunay
        self.edges = []
        for dart in DT.darts:
            edge = geom.Oriented_Edge(dart.vertices) 
            if not edge.is_infinite and edge.has_0_on_left: # on ne prend qu'une arete sur 2
                p = dart.next.target
                q = dart.twin.next.target               
                if not(edge.Gab_Circle_contains(p) or edge.Gab_Circle_contains(q)):
                    self.edges.append(edge.vertices)

class Rel_Neighbor_Graph(Graph):
    def __init__(self):
        self.edges = []

    def extract_from_Del(self, DT):
        # Extrait le RNG à partir des aretes de Delaunay
        # Pour chaque arete finie, on teste si sa RNG-Moon est vide
        self.edges = []
        for dart in DT.darts:
            edge = geom.Oriented_Edge(dart.vertices)
            if not dart.is_infinite and edge.has_0_on_left:            
                if Rel_Neighbor_Graph.empty_right_RNG_Moon(dart) and Rel_Neighbor_Graph.empty_right_RNG_Moon(dart.twin):
                    self.edges.append(edge.vertices)

    @staticmethod
    def empty_right_RNG_Moon(dart):
        """
            Renvoie un dart dont la face contient p ou est visible par p si infinie
        """ 
        # On construit t (target), l'extremité droite de la Moon de ab
        a, b = dart.vertices
        ax, ay = a
        bx, by = b
        m = geom.gravity_center((a, b)) 
        mx, my = m
        tx = mx + (by - ay)
        ty = my - (bx - ax)
        target = (tx, ty)

        edge = geom.Oriented_Edge((a, b))                          
        triangle = geom.Oriented_Triangle(dart.get_cycle_vertices)

        # On marche de triangle en triangle en suivant l'axe mt et testant le sommet p du triangle jusqu'atteindre t
        # Si on atteint les circumcircles des rtinagles recouvrent (je crois....) Right-RNG-Moon qui est donc vide 
        while not triangle.contains(target):
            p = dart.next.target
            if edge.RNG_Moon_contains(p):
                return False
            crossing_d = Delaunay_Triangulation._find_crossing_dart(dart, m, target)
            dart = crossing_d.twin # on passe à la face suivante
            triangle = geom.Oriented_Triangle(dart.get_cycle_vertices)
        return True

        




if __name__ == "__main__":
    points = []
    for _ in range(3):
        x = random.random()
        y = random.random()
        points.append((x, y))
    DT = Delaunay_Triangulation()
    DT.build(points)
    print(DT.is_triangulation)
    RNG = Rel_Neighbor_Graph()
    RNG.extract_from_Del(DT)
    print("OK")
