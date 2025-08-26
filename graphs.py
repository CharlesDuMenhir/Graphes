import random
import union_find as uf # pour le MST

import geom # prédicats et objets géométriques

class Vertex(geom.Point):
    def __init__(self, x, y, w = 1):
        super().__init__(x, y, w) # geom.Point
        self.ref_dart = None  # dartde référence du sommet, initialisée à l'ajout du premier dart sur ce point, et mise à jour aux flip
        
    def __repr__(self):
        return f"Graph point at ({self.coord})"
    
    @property    
    def incident_darts(self):
        # Renvoie les brins incidents à self
        dart_0 = self.ref_dart 
        darts = [dart_0]
        current_d = dart_0.rotate
        while current_d is not dart_0:
            darts.append(current_d)
            current_d = current_d.rotate
        return darts


class Dart:
    # https://fr.wikipedia.org/wiki/Carte_combinatoire
    def __init__(self, origin, visited = False):
        self.origin = origin  # Sommet de départ, Vertex
        self.twin = None    # Brin opposé (même arête, sens inverse), alpha0
        self.next = None    # Brin suivant cw dans la face, alpha2

    def __repr__(self):
        return f"Dart from ({self.origin}) to ({self.target})"

    @property
    def target(self):
        # Brin suivant cw-autour du sommet
        return self.next.origin

    @property
    def rotate(self):
        # Brin suivant cw-autour du sommet, alpha1
        return self.twin.next
    
    @property
    def edge(self):
        a, b = self.origin, self.target
        return geom.Edge(a, b)
    
    @property
    def face(self):
        a = self.origin
        b = self.target
        c = self.next.target
        return geom.Triangle(a, b, c)
    
    @property
    def cycle(self):
        # Renvoie tous les darts du cycle
        darts = [self]
        current_d = self.next
        while current_d is not self:
            darts.append(current_d)
            current_d = current_d.next
        return darts
    
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

    def choose_unique_finite(self):
        # Renvoie False si le dart est infini ainsi que pour un dart des 2 twins
        a = self.origin
        b = self.target
        inf_V = geom.Point(0, 0, 0)
        if a == inf_V or b == inf_V or geom.are_clockwise(a.coord, b.coord, (0, 0)):
            return False
        return True
        
    def flip(self): 
        """
        Dans un quadrilatere paqb, flip ab (self) en pq
        """
        d_ab, d_bp, d_pa = self.cycle
        # les 3 darts de aqb
        d_ba, d_aq, d_qb = self.twin.cycle
        #On met à jour les darts de reference des sommets si besoin
        for d in (d_ab, d_ba):
            if d.origin.ref_dart == d:
                d.origin.ref_dart = d.rotate # on choisit alors d.rotate car il n'est pas modifié par le flip en cours
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
        self.vertices = [Vertex(0, 0, 0)] # initialement on considère le sommet à l'infini
        self.darts = []

    def reset(self):
        self.__init__()

    @property
    def unique_finite_darts(self):
        return [dart for dart in self.darts if dart.choose_unique_finite()]

    @property
    def edges(self): # utilisé pour l'affichage
        return [dart.edge for dart in self.unique_finite_darts]

    @property
    def is_triangulation(self):
        for d in self.darts:
            if not d.is_cycle(3):
                return False
        return True

    def build(self, points):
        self.reset()
        for p in points:
            self.insert_point(p)

    def insert_point(self, p):
        x, y = p
        v = Vertex(x, y)
        self.vertices.append(v)
        if len(self.vertices) == 2:
            return
        if len(self.vertices) == 3:
            if p == self.vertices[1]:
                self.vertices.pop() # pour éviter les points doubles (doubles clics)
                return
            else:
                self._init_first_faces()
            return
        # si la triangulation est déjà créée, on insert le point
        self._insert_in_Delaunay(v)

    def _init_first_faces(self):
        """
        Crée et initialise les 6 premiers darts (4 infinis et 2 finis)
        """ 
        a, b, c = self.vertices
        # initialisation des darts
        darts_A = [Dart(a), Dart(b), Dart(c)]
        darts_B = [Dart(b), Dart(c), Dart(a)]
        # maj des refs, twin, next
        for i in range(3):
            self.vertices[i].ref_dart = darts_A[i]   # chaque sommet est reférencé par un dart, mis à jour aux flips
            Dart.set_twin_each_other(darts_A[i], darts_B[i])
        Dart.set_next_each_other(darts_A)
        Dart.set_next_each_other(darts_B[::-1])
        # ajout dans la liste
        self.darts.extend(darts_A)
        self.darts.extend(darts_B)

    def _insert_in_Delaunay(self, v):
        """
        Insert graph point v (Vertex). Met à jour les darts
        """
        dart = self.segment_walk_to(v) # On trouve une face en conflit
        if dart == "Point deja existant":
            self.vertices.pop()
            return
        darts_to_flip = self._init_new_darts(dart, v) # On relie la triangualtion avec les nouveaux darts
        for dart in darts_to_flip: # Et on rétablit recursivement la propriété de Delanuay
            Delaunay_Triangulation._flip_until_Del(dart)


    def segment_walk_to(self, target):
        """
            target: le point inséré, dont il on cherche le triangle qui le contient
            Recherche par segment walk
            Renvoie un dart dont la face contient p ou est visible par p si infinie
        """ 
        # choix de la source aléatoire, mais il faut éviter les triangles infinis
        # Au premier appel, il n'y a pas de triangle fini mais ce n'est pas grave car on tombe assez vite dans la
        dart = random.choice(self.darts) # On part d'un dart random
        triangle = dart.face
        found = target.is_in_triangle(triangle)
        if not found:
            if triangle.is_infinite: # si c'est une face infinie, on change de dart pour rentrer dans l'enveloppe convexe
                while dart.edge.is_infinite: # on cherche le dart fini
                    dart = dart.next
                dart = dart.twin # puis on switch à l'intérieur de l'enveloppe convexe
                triangle = dart.face # 2 cas possibles: Soit target est dans triangle, soit triangle est fini
                found = target.is_in_triangle(triangle)
            source = triangle.centroid # on part du centre du triangle choisi
            segment = geom.Edge(source, target)
        # Recherche du triangle contenant p
        while not found:
            dart = Delaunay_Triangulation._find_crossing_dart(dart, segment) # identification du segment du triangle qui coupe [sp] 
            triangle = dart.face
            found = target.is_in_triangle(triangle)
            if triangle.is_infinite:
                break # dans ce cas, target est hors de l'enveloppe convexe, comme on en vient, dart est visible par target
        # Si le point est un sommet du triangle, on ne l'ajoutera pas
        if target in triangle.vertices:
            return "Point deja existant"
        return dart

    @staticmethod
    def _find_crossing_dart(d, segment):
        """
        d : un dart de la face.
        Renvoie le dart de la face qui intersect le segment
        par construction, on ne peut pas retomber sur le dart de départ
        """
        found = False
        while not found:
            d = d.next # donc on teste deja d.next
            edge = d.edge
            found = edge.intersects(segment)
        return d.twin

    def _init_new_darts(self, dart, v):
        """
            dart : un dart de la face qui contient v: Vertex à ajouter
            Crée et initialise les darts liés à l'ajout du sommet v. On n'a temporairement plus une triangulation de Delaunay.
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
        d_aq = d_ab.rotate
        d_qb = d_aq.next
        triangle = d_ab.face
        p = d_qb.origin
        if p.is_in_circumcircle(triangle):
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
        self.reset()
        vertices = DT.vertices[1:]
        if len(vertices) <= 1:
            return
        for v1 in vertices:  # pour chaque sommet fini
            cell_edges = []
            d = v1.incident_darts[0]
            triangle = d.face
            first_center = triangle.circumcenter
            for d in v1.incident_darts:
                v2 = d.target
                next_d = d.rotate
                next_triangle = next_d.face
                second_center = next_triangle.circumcenter
                new_edge = geom.Edge(first_center, second_center, geom.Point.midpoint(v1, v2))
                first_center = second_center
                if v2.is_infinite:
                    continue
                cell_edges.append(new_edge)
            self.cells.append(geom.Cell(cell_edges))


#-------------------------Graphe de Gabriel-----------------------

class Gabriel_Graph(Graph):
    def __init__(self):
        self.edges = []

    def extract_from_Del(self, DT):
        # Extrait le graphe de Gabriel à partir des aretess de Delaunay
        self.reset()
        for d in DT.unique_finite_darts:
            edge = d.edge
            p = d.next.target
            q = d.twin.next.target             
            if not(p.is_in_Gab_circle(edge) or q.is_in_Gab_circle(edge)):
                self.edges.append(edge)

#-------------------------Relative neighbors graph-----------------------

class Rel_Neighbor_Graph(Graph):
    def __init__(self):
        self.edges = []

    def extract_from_Del(self, DT):
        # Extrait le RNG à partir des aretes de Delaunay
        # Pour chaque arete finie, on teste si sa RNG-Moon est vide
        self.reset()
        for d in DT.unique_finite_darts:
            edge = d.edge          
            if Rel_Neighbor_Graph.empty_right_RNG_moon(d) and Rel_Neighbor_Graph.empty_right_RNG_moon(d.twin):
                self.edges.append(edge)

    @staticmethod
    def empty_right_RNG_moon(dart):
        """
            Renvoie un dart dont la face contient p ou est visible par p si infinie
        """ 
        # On construit t (target), l'extremité droite de la Moon de ab
        edge = dart.edge
        a, b = edge.vertices
        m = geom.Point((a.x + b.x) / 2, (a.y + b.y) / 2)
        t_x = m.x + (b.y - a.y)
        t_y = m.y - (b.x - a.x)
        t = geom.Point(t_x, t_y)
        segment = geom.Edge(m, t)                      
        triangle = dart.face
        # On marche de triangle en triangle en suivant l'axe (mt) et testant le sommet p du triangle jusqu'atteindre t
        # Si on atteint t, les circumcircles des triangles recouvrent (je crois....) Right-RNG-Moon qui est donc vide 
        while not t.is_in_triangle(triangle):
            p = dart.next.target
            if p.is_in_RNG_moon(edge):
                return False
            dart = Delaunay_Triangulation._find_crossing_dart(dart, segment)
            triangle = dart.face
        return True
    
#-------------------------Minimal spanning tree-----------------------

class Minimal_Spanning_Tree(Graph):
    def __init__(self):
        self.edges = []

    def extract_from_Del(self, DT):
        self.reset()
        edges = DT.edges
        edges.sort(key = lambda edge: edge.square_length)

        for v in DT.vertices:
            uf.make_set(v)

        for edge in edges:
            a, b = edge.vertices # paire de Point
            if uf.union(a, b):
                self.edges.append(edge)



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
