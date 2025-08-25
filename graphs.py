import random
import union_find as uf # pour le MST

import geom # prédicats

class Vertex:
    def __init__(self, point):
        self.point = point # Coordonnées du sommet
        self.ref_dart = None  # Dart de référence du sommet, initialisé à l'ajout du premier dart sur ce point, et mis à jour aux flip
        
    def __repr__(self):
        return f"Vertex at ({self.point})"
    
    @property    
    def incident_darts(self):       # Brin sortants
        return self.ref_dart.neighbors
    
    
class Dart:
    # https://fr.wikipedia.org/wiki/Carte_combinatoire
    def __init__(self, origin, visited = False):
        self.origin = origin  # Sommet de départ
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
        if self.origin.point == geom.INF_P or self.twin.origin.point == geom.INF_P:
            return True
        return False
    
    @property    
    def vertices(self):
        # Renvoie tous les sommets du dart
        a = self.origin
        b = self.target
        return (a, b)
    
    @property    
    def points(self):
        # Renvoie tous les sommets du dart
        p = self.origin.point
        q = self.target.point
        return (p, q)
    
    @property
    def cycle(self):
        # Renvoie tous les darts du cycle
        darts = [self]
        current_d = self.next
        while current_d is not self:
            darts.append(current_d)
            current_d = current_d.next
        return darts

    @property
    def cycle_vertices(self):
        # Renvoie tous les sommets du cycle
        return [d.origin for d in self.cycle]
    
    @property
    def cycle_points(self):
        # Renvoie tous les sommets du cycle
        return [d.origin.point for d in self.cycle]
    
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
        d_ab, d_bp, d_pa = self.cycle
        # les 3 darts de aqb
        d_ba, d_aq, d_qb = self.twin.cycle
        #On met à jour les darts de reference des sommets si besoin
        for d in (d_ab, d_ba):
            if d.origin.ref_dart == d:
                d.origin.ref_dart = d.alpha1 # on choisit alors d.alpha1 car il n'est pas modifié par le flip en cours
        # flip des sommets
        d_ab.origin = d_qb.origin
        d_ba.origin = d_pa.origin
        d_qp, d_pq = d_ab, d_ba # on renomme juste pour la lisibilité
        # maj des pointages next
        tri_aqp = [d_aq, d_qp, d_pa]
        Dart.set_next_each_other(tri_aqp)
        tri_bpq = [d_bp, d_pq, d_qb]
        Dart.set_next_each_other(tri_bpq)
    

#-----------------------------------------------------GRAPHES---------------
class Graph:
    def reset(self):
        self.__init__()

#----------------------------------------------------Delaunay triangulation
class Delaunay_Triangulation(Graph):
    def __init__(self):
        self.vertices = []
        self.inf_vertex = Vertex(geom.INF_P)  
        self.darts = []

    @property
    def edges(self): # utilisé pour l'affichage
        edges = []
        for dart in self.darts:
            edge = geom.Oriented_Edge(dart.points) 
            if not edge.is_infinite and edge.has_0_on_left: # on écarte les aretes infinies et les doublons
                edges.append(edge)
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
        v = Vertex(p)
        self.vertices.append(v)
        if len(self.vertices) == 1:
            return
        if len(self.vertices) == 2:
            if p == self.vertices[0]:
                self.vertices.pop() # pour éviter les points doubles (doubles clics)
            return
        if len(self.vertices) == 3:
            if p == self.vertices[0] or p == self.vertices[1]:
                self.vertices.pop()
            else:
                self._init_first_triangle(self.vertices)
            return
        # si la triangulation est déjà créee, on insert le point
        self._insert_in_Delaunay(v)


    def _init_first_triangle(self, triangle): # triangle est tuple de 3 Vertex
        """
            Crée et initialise les darts du premier triangle
        """ 
        a, b, c = triangle
        if not geom.are_clockwise(a.point, b.point, c.point): # les triangles internes DOIVENT etre clockwise
            b, c = c, b
        # on crée les 12 nouveaux darts du premier triangles (6 finis, 6 infinis)
        internal_darts = [Dart(a), Dart(b), Dart(c)]
        self.darts.extend(internal_darts)
        for i,v in enumerate((a, b, c)):
            v.ref_dart = internal_darts[i]
        external_darts = [Dart(b), Dart(c), Dart(a)]
        self.darts.extend(external_darts)
        infinite_darts_to_inf = [Dart(a), Dart(b), Dart(c)]
        self.darts.extend(infinite_darts_to_inf)
        self.inf_vertex.ref_dart = infinite_darts_to_inf[0]
        infinite_darts_from_inf = [Dart(self.inf_vertex), Dart(self.inf_vertex), Dart(self.inf_vertex)]
        self.darts.extend(infinite_darts_from_inf)
        # on met à jour leurs liens
        Dart.set_next_each_other(internal_darts)
        for i in range(3):
            Dart.set_twin_each_other(internal_darts[i], external_darts[i])
            Dart.set_twin_each_other(infinite_darts_to_inf[i], infinite_darts_from_inf[i])
            external_darts[i].next = infinite_darts_to_inf[i]
            infinite_darts_to_inf[i].next = infinite_darts_from_inf[(i+1)%3]
            infinite_darts_from_inf[i].next = external_darts[i-1]        


    def _insert_in_Delaunay(self, v):
        """
        Insert point p. Met à jour les darts
        """
        dart = self.find_triangle_of(v.point) # On trouve une face en conflit
        if dart == "Point deja existant":
            self.vertices.pop()
            print("Point non ajouté")
            return
        darts_to_flip = self._init_new_darts(dart, v) # On relie la triangualtion avec les nouveaux darts
        for dart in darts_to_flip: # Et on rétablit recursivement la propriété de Delanuay
            Delaunay_Triangulation._flip_until_Del(dart)


    def find_triangle_of(self, target):
        """
            target: le point inséré, dont il on cherche le triangle qui le contient
            Recherche par segment walk
            Renvoie un dart dont la face contient p ou est visible par p si infinie
        """ 
        # choix de la source aléatoire, mais il faut éviter les triangles infinis
        dart = random.choice(self.darts) # On part d'un dart random
        triangle = geom.Oriented_Triangle(dart.cycle_points)
        if triangle.is_infinite: # si c'est une face infinie, on change de dart pour rentrer dans l'enveloppe convexe
            while dart.is_infinite: # on cherche le dart fini
                dart = dart.next
            dart = dart.twin # puis on switch à l'intérieur de l'enveloppe convexe
            triangle = geom.Oriented_Triangle(dart.cycle_points)
        source = geom.gravity_center(dart.cycle_points) # on part du centre du triangle choisi

        # Recherche du triangle contenant p
        while not triangle.contains(target):
            crossing_d = Delaunay_Triangulation._find_crossing_dart(dart, source, target) # identification du segment du triangle qui coupe [sp] 
            dart = crossing_d.twin # on passe à la face suivante
            triangle = geom.Oriented_Triangle(dart.cycle_points)
            if triangle.is_infinite:
                break # dans ce cas, target est hors de l'enveloppe convexe, comme on en vient, dart est visible par target
        
        # Si le point est un sommet du triangle, on ne l'ajoutera pas
        if target in triangle.points:
            return "Point deja existant"
        return dart
    

    @staticmethod
    def _find_crossing_dart(d, source, target):
        """
        d : un dart de la face.
        Renvoie le dart de la face qui intersect source-target
        par construction, on ne peut pas retomber sur le dart de départ
        """
        found = False
        while not found:
            d = d.next # donc on teste deja d.next
            a = d.origin.point  
            b = d.target.point
            found = geom.segments_intersect(source, target, a, b)
        return d


    def _init_new_darts(self, dart, v):
        """
            Crée et initialise les darts liés à l'ajout du point p. On n'a temporairement plus une triangulation de Delaunay.
            Renvoie les darts qu'il faut tester et flipper si necessaires 
        """ 
        triangle_darts = dart.cycle
        # création et ajout des 6 nouveaux darts
        new_darts_from_v = [Dart(v), Dart(v), Dart(v)]
        v.ref_dart = new_darts_from_v[0]
        new_darts_to_v = [Dart(d.origin) for d in triangle_darts]
        self.darts.extend(new_darts_from_v)
        self.darts.extend(new_darts_to_v)
        # mise à jour des alpha 0
        for i in range(3):
            Dart.set_twin_each_other(new_darts_from_v[i], new_darts_to_v[i])
        # mise à jour des alpha 2
        for i in range(3):
            new_darts_from_v[i].next = triangle_darts[i]
            triangle_darts[i].next = new_darts_to_v[(i+1)%3]
            new_darts_to_v[i].next = new_darts_from_v[(i+2)%3]   
        return triangle_darts


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
        triangle = geom.Oriented_Triangle(d_ab.cycle_points)
        if triangle.is_in_conflict(d_qb.origin.point):
            d_ab.flip()
            Delaunay_Triangulation._flip_until_Del(d_aq)
            Delaunay_Triangulation._flip_until_Del(d_qb)

#-------------------------Diagramme de Voronoi-----------------------

class Voronoi_Diagram(Graph):
    def __init__(self):
        self.cells = []

    @property
    def edges(self):
        edges = []
        for cell in self.cells:
            edges.extend(cell.edges)
        return edges

    def extract_from_Del(self, DT):
        """
            Détermine les cellules de voronoï.
            Leur sommets sont les circumcentres des triangles de Delaunay 
        """
        self.cells = []
        vertices = DT.vertices
        if len(vertices) <= 2:
            return
        for v1 in vertices:
            cell_edges = []
            d = v1.incident_darts[0]
            triangle = geom.Oriented_Triangle(d.cycle_points)
            first_center = triangle.circumcenter
            for d in v1.incident_darts:
                next_triangle = geom.Oriented_Triangle(d.alpha1.cycle_points)
                second_center = next_triangle.circumcenter
                if first_center == geom.INF_P and second_center != geom.INF_P:
                    x_v1, y_v1 = d.origin.point
                    x_v2, y_v2 = d.target.point
                    dir = ((y_v2 - y_v1), -(x_v2 - x_v1))
                    new_edge = geom.Ray(second_center, dir)
                elif first_center != geom.INF_P and second_center == geom.INF_P:
                    x_v1, y_v1 = d.origin.point
                    x_v2, y_v2 = d.target.point
                    dir = (-(y_v2 - y_v1), (x_v2 - x_v1))
                    new_edge = geom.Ray(first_center, dir)
                else:
                    new_edge = geom.Oriented_Edge((first_center, second_center))
                first_center = second_center
                cell_edges.append(new_edge)
            self.cells.append(geom.Cell(cell_edges))

"""
# médiatrice de ab
a, b = vertices
x_a, y_a = a.point
x_b, y_b = b.point
x_m, y_m = geom.gravity_center((a.point, b.point))
x_dir, y_dir = -(y_b - y_a), x_b - x_a
p = (x_m + x_dir, y_m + y_dir)
q = (x_m - x_dir, y_m - y_dir)
new_cell = geom.Oriented_Polygone((p, q))

"""

        



#-------------------------Graphe de Gabriel-----------------------

class Gabriel_Graph(Graph):
    def __init__(self):
        self.edges = []

    def extract_from_Del(self, DT):
        # Extrait le graphe de Gabriel à partir des aretess de Delaunay
        self.edges = []
        for dart in DT.darts:
            edge = geom.Oriented_Edge(dart.points) 
            if not edge.is_infinite and edge.has_0_on_left: # on ne prend qu'une arete sur 2
                p = dart.next.target.point
                q = dart.twin.next.target.point              
                if not(edge.Gab_Circle_contains(p) or edge.Gab_Circle_contains(q)):
                    self.edges.append(edge)

#-------------------------Relative neighbors graph-----------------------

class Rel_Neighbor_Graph(Graph):
    def __init__(self):
        self.edges = []

    def extract_from_Del(self, DT):
        # Extrait le RNG à partir des aretes de Delaunay
        # Pour chaque arete finie, on teste si sa RNG-Moon est vide
        self.edges = []
        for dart in DT.darts:
            edge = geom.Oriented_Edge(dart.points)
            if not dart.is_infinite and edge.has_0_on_left:            
                if Rel_Neighbor_Graph.empty_right_RNG_Moon(dart) and Rel_Neighbor_Graph.empty_right_RNG_Moon(dart.twin):
                    self.edges.append(edge)

    @staticmethod
    def empty_right_RNG_Moon(dart):
        """
            Renvoie un dart dont la face contient p ou est visible par p si infinie
        """ 
        # On construit t (target), l'extremité droite de la Moon de ab
        a, b = dart.points
        ax, ay = a
        bx, by = b
        m = geom.gravity_center((a, b)) 
        mx, my = m
        tx = mx + (by - ay)
        ty = my - (bx - ax)
        target = (tx, ty)

        edge = geom.Oriented_Edge((a, b))                          
        triangle = geom.Oriented_Triangle(dart.cycle_points)

        # On marche de triangle en triangle en suivant l'axe (mt) et testant le sommet p du triangle jusqu'atteindre t
        # Si on atteint les circumcircles des rtinagles recouvrent (je crois....) Right-RNG-Moon qui est donc vide 
        while not triangle.contains(target):
            p = dart.next.target.point
            if edge.RNG_Moon_contains(p):
                return False
            crossing_d = Delaunay_Triangulation._find_crossing_dart(dart, m, target)
            dart = crossing_d.twin # on passe à la face suivante
            triangle = geom.Oriented_Triangle(dart.cycle_points)
        return True
    
#-------------------------Minimal spanning tree-----------------------

class Minimal_Spanning_Tree(Graph):
    def __init__(self):
        self.edges = []

    def extract_from_Del(self, DT):
        self.edges = []
        vertices = DT.vertices
        if len(vertices) == 2:
            a, b = vertices
            self.edges.append((a.point, b.point))
            return

        # a recoder avec une autre structure de données, trop d'aller retour point/vertex illisibles Edges de point, edge de tuple....

        edges = []
        for dart in DT.darts:
            edge = geom.Oriented_Edge(dart.points) 
            if not edge.is_infinite and edge.has_0_on_left: # on écarte les aretes infinies et les doublons
                edges.append(dart.vertices)

        edges.sort(key = lambda edge: geom.square_dist(edge[0].point, edge[1].point))

        for v in vertices:
            uf.make_set(v)

        for edge in edges:
            u, v = edge # pair de vertex
            if uf.union(u, v):
                new_edge = geom.Oriented_Edge((u.point,v.point))
                self.edges.append(new_edge)



if __name__ == "__main__":
    points = []
    for _ in range(40):
        x = random.random()
        y = random.random()
        points.append((x, y))
    DT = Delaunay_Triangulation()
    DT.build(points)
    print(DT.is_triangulation)
    for v in DT.vertices:
        for d in v.incident_darts:
            if d.origin != v:
                print(v,d.origin)
                print("Problem")
    RNG = Rel_Neighbor_Graph()
    RNG.extract_from_Del(DT)
    MST = Minimal_Spanning_Tree()
    MST.extract_from_Del(DT)
    VD = Voronoi_Diagram()
    VD.extract_from_Del(DT)
    print("OK")
