"""
Module de structures de graphes géométriques pour la triangulation de Delaunay, 
le diagramme de Voronoï, le graphe de Gabriel, le graphe des voisins relatifs et l'arbre couvrant minimal.

Ce module fournit des classes pour manipuler des graphes géométriques basés sur des objets du module geom.
Les principales classes sont :
    - Vertex : sommet du graphe, hérite de geom.Point
    - Dart : brin orienté pour la représentation combinatoire des arêtes
    - Delaunay_Triangulation : structure de triangulation de Delaunay
    - Voronoi_Diagram : structure pour le diagramme de Voronoï
    - Gabriel_Graph : graphe de Gabriel
    - Rel_Neighbor_Graph : graphe des voisins relatifs
    - Minimal_Spanning_Tree : arbre couvrant minimal

Chaque classe fournit des méthodes pour la construction, l'extraction et la manipulation des structures associées.
"""

import random
import union_find as uf  # pour le MST
import geom  # prédicats et objets géométriques
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Vertex(geom.Point):
    """
    Sommet du graphe, hérite de geom.Point.
    ref_dart : dart de référence du sommet, initialisé à l'ajout du premier dart sur ce point.
    """
    ref_dart: Optional["Dart"] = field(default=None, compare=False, repr=False)

    def __repr__(self) -> str:
        if self.is_infinite:
            return "Infinite point"
        return f"Vertex({self.x:.3f}, {self.y:.3f})"
    
    @property    
    def incident_darts(self) -> List["Dart"]:
        """Renvoie la liste des darts incidents à ce sommet."""
        dart_0 = self.ref_dart 
        darts = [dart_0]
        current_d = dart_0.rotate
        while current_d is not dart_0:
            darts.append(current_d)
            current_d = current_d.rotate
        return darts

@dataclass
class Dart:
    """
    Brin orienté pour la représentation combinatoire des arêtes (carte combinatoire).
    Attributs :
        origin (Vertex): Sommet de départ.
        twin (Dart): Brin opposé (même arête, sens inverse).
        next (Dart): Brin suivant dans la face.
    """
    origin: Vertex
    twin: Optional["Dart"] = field(default=None, compare=False, repr=False)
    next: Optional["Dart"] = field(default=None, compare=False, repr=False)

    def __repr__(self) -> str:
        return f"Dart from ({self.origin}) to ({self.target})"

    @property
    def target(self) -> Vertex:
        """Renvoie le sommet d'arrivée du brin."""
        return self.next.origin

    @property
    def rotate(self) -> "Dart":
        """Renvoie le brin suivant autour du sommet d'origine (rotation locale)."""
        return self.twin.next
    
    @property
    def edge(self) -> geom.Edge:
        """Renvoie l'arête géométrique associée à ce brin."""
        return geom.Edge(self.origin, self.target)
    
    @property
    def face(self) -> geom.Triangle:
        """Renvoie le triangle géométrique associé à ce brin."""
        a = self.origin
        b = self.target
        c = self.next.target
        return geom.Triangle(a, b, c)
    
    @property
    def cycle(self) -> List["Dart"]:
        """Renvoie tous les brins du cycle (face)."""
        darts = [self]
        current_d = self.next
        while current_d is not self:
            darts.append(current_d)
            current_d = current_d.next
        return darts

    @staticmethod
    def set_twin_each_other(d_ab: "Dart", d_ba: "Dart") -> None:
        """Définit deux brins comme étant twins l'un de l'autre."""
        d_ab.twin, d_ba.twin = d_ba, d_ab

    @staticmethod
    def set_next_each_other(darts: List["Dart"]) -> None:
        """Définit la relation next entre une liste de brins."""
        for i in range(len(darts)):
            darts[i-1].next = darts[i]

    def choose_unique_finite(self) -> bool:
        """Détermine si le brin est fini et unique (pour affichage)."""
        a = self.origin
        b = self.target
        inf_V = geom.Point(0, 0, 0)
        if a == inf_V or b == inf_V or geom.are_clockwise(a.coord, b.coord, (0, 0)):
            return False
        return True
        
    def flip(self) -> None: 
        """Flippe le brin dans un quadrilatère paqb, remplaçant ab par pq."""
        d_ab, d_bp, d_pa = self.cycle # les 3 darts de abb
        d_ba, d_aq, d_qb = self.twin.cycle # les 3 darts de aqb
        # maj des darts de reference des sommets si besoin
        for d in (d_ab, d_ba):
            if d.origin.ref_dart == d:
                d.origin.ref_dart = d.rotate # on choisit alors d.rotate car il n'est pas modifié par le flip en cours
        # flip des sommets
        d_ab.origin = d_qb.origin 
        d_ba.origin = d_pa.origin
        d_qp, d_pq = d_ab, d_ba # renommés juste pour la lisibilité
        # maj des pointages next
        tri_aqp = [d_aq, d_qp, d_pa]
        Dart.set_next_each_other(tri_aqp)
        tri_bpq = [d_bp, d_pq, d_qb]
        Dart.set_next_each_other(tri_bpq)
    

#-----------------------------------------------------GRAPHES---------------
class Graph:
    """
    Classe de base pour les graphes géométriques.
    """
    def reset(self) -> None:   # a modifier
        self.__init__()

#----------------------------------------------------Delaunay triangulation
class Delaunay_Triangulation(Graph):
    """
    Structure de triangulation de Delaunay.
    """
    vertices: List[Vertex]
    darts: List[Dart]

    def __init__(self):
        self.vertices: List[Vertex] = [Vertex(0, 0, 0)]
        self.darts: List[Dart] = []

    @property
    def unique_finite_darts(self) -> List[Dart]:
        """Renvoie la liste des brins finis et uniques pour affichage. """
        return [dart for dart in self.darts if dart.choose_unique_finite()]

    @property
    def edges(self) -> List[geom.Edge]:
        """Renvoie la liste des arêtes géométriques du graphe."""
        return [dart.edge for dart in self.unique_finite_darts]

    def build(self, points: List[geom.Point]) -> None:
        """Construit la triangulation à partir d'une liste de points."""
        self.reset()
        for p in points:
            self.insert_point(p)

    def insert_point(self, p: geom.Point) -> None:
        """Insère un point dans la triangulation."""
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

    def _init_first_faces(self) -> None:
        """Crée et initialise les 6 premiers darts (4 infinis et 2 finis)."""
        a, b, c = self.vertices
        # initialisation des darts
        darts_A = [Dart(a), Dart(b), Dart(c)]
        darts_B = [Dart(b), Dart(c), Dart(a)]
        # maj des refs, twin, next
        for i in range(3):
            self.vertices[i].ref_dart = darts_A[i]
            Dart.set_twin_each_other(darts_A[i], darts_B[i])
        Dart.set_next_each_other(darts_A)
        Dart.set_next_each_other(darts_B[::-1])
        self.darts.extend(darts_A)
        self.darts.extend(darts_B)

    def _insert_in_Delaunay(self, v: Vertex) -> None:
        """Insère un sommet dans la triangulation de Delaunay et met à jour les darts."""
        dart = self.segment_walk_to(v) # On trouve une face en conflit
        if dart == "Point deja existant":
            self.vertices.pop()
            print("Point non ajouté.")
            return
        darts_to_flip = self._init_new_darts(dart, v) # On relie la triangualtion avec les nouveaux darts
        for dart in darts_to_flip: # Et on rétablit recursivement la propriété de Delanuay
            Delaunay_Triangulation._flip_until_Del(dart)

    def segment_walk_to(self, target: Vertex) -> Dart:
        """Recherche le triangle contenant le point cible par segment walk."""
        dart = random.choice(self.darts)
        triangle = dart.face
        found = target.is_in_triangle(triangle)
        if not found:
            if triangle.is_infinite: # si c'est une face infinie, on change de dart pour rentrer dans l'enveloppe convexe
                while dart.edge.is_infinite: # on cherche le dart fini du triangle
                    dart = dart.next
                dart = dart.twin # puis on switch à l'intérieur de l'enveloppe convexe
                triangle = dart.face # 2 cas possibles: Soit target est dans triangle, soit triangle est fini
                found = target.is_in_triangle(triangle)
            source = triangle.centroid
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
    def _find_crossing_dart(d: Dart, segment: geom.Edge) -> Dart:
        """Trouve le brin de la face qui intersecte un segment donné."""
        found = False
        while not found:
            d = d.next # on teste deja d.next sinon on repartirai en arrière
            edge = d.edge
            found = edge.intersects(segment)
        return d.twin

    def _init_new_darts(self, dart: Dart, v: Vertex) -> List[Dart]:
        """Crée et initialise les nouveaux darts liés à l'ajout d'un sommet."""
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
    def _flip_until_Del(dart: Dart) -> None:
        """Réétablit récursivement la propriété de Delaunay après l'ajout d'un point."""
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
    """
    Structure pour le diagramme de Voronoï.
    """
    cells: List[geom.Cell]

    def __init__(self):
        self.cells: List[geom.Cell] = []

    @property
    def edges(self) -> List[geom.Edge]:
        """Renvoie la liste des arêtes des cellules du diagramme."""
        edges: List[geom.Edge] = []
        for cell in self.cells:
            edges.extend(cell.edges)
        return edges

    def extract_from_Del(self, DT: Delaunay_Triangulation) -> None:
        """Détermine les cellules de Voronoï à partir d'une triangulation de Delaunay."""
        self.reset()
        vertices = DT.vertices[1:]
        if len(vertices) <= 1:
            return
        for v1 in vertices:  # pour chaque sommet fini
            cell_edges: List[geom.Edge] = []
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
    """
    Graphe de Gabriel extrait d'une triangulation de Delaunay.
    """
    edges: List[geom.Edge]

    def __init__(self):
        self.edges: List[geom.Edge] = []

    def extract_from_Del(self, DT: Delaunay_Triangulation) -> None:
        """Extrait le graphe de Gabriel à partir des arêtes de Delaunay."""
        self.reset()
        for d in DT.unique_finite_darts:
            edge = d.edge
            p = d.next.target
            q = d.twin.next.target             
            if not(p.is_in_Gab_circle(edge) or q.is_in_Gab_circle(edge)):
                self.edges.append(edge)

#-------------------------Relative neighbors graph-----------------------

class Rel_Neighbor_Graph(Graph):
    """
    Graphe des voisins relatifs extrait d'une triangulation de Delaunay.
    """
    edges: List[geom.Edge]

    def __init__(self):
        self.edges: List[geom.Edge] = []

    def extract_from_Del(self, DT: Delaunay_Triangulation) -> None:
        """Extrait le RNG à partir des arêtes de Delaunay."""
        self.reset()
        for d in DT.unique_finite_darts:
            edge = d.edge          
            if Rel_Neighbor_Graph.empty_right_RNG_moon(d) and Rel_Neighbor_Graph.empty_right_RNG_moon(d.twin):
                self.edges.append(edge)

    @staticmethod
    def empty_right_RNG_moon(dart: Dart) -> bool:
        """Teste si la lune RNG à droite de l'arête est vide."""
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
    """
    Arbre couvrant minimal extrait d'une triangulation de Delaunay.
    """
    edges: List[geom.Edge]

    def __init__(self):
        self.edges: List[geom.Edge] = []

    def extract_from_Del(self, DT: Delaunay_Triangulation) -> None:
        """Extrait l'arbre couvrant minimal à partir des arêtes de Delaunay. """
        self.reset()
        edges = DT.edges
        edges.sort(key = lambda edge: edge.square_length)

        for v in DT.vertices:
            uf.make_set(v)

        for edge in edges:
            a, b = edge.vertices
            if uf.union(a, b):
                self.edges.append(edge)

if __name__ == "__main__":
    # Exemple de liste de points
    points = [(0, 0), (1, 0), (0, 1), (1, 1), (0.5, 0.5)]

    # Construction de la triangulation
    DT = Delaunay_Triangulation()
    DT.build(points)

    # Récupération des arêtes
    edges = DT.edges

    # Pour afficher les coordonnées des arêtes
    for edge in edges:
        print(f"Edge from {edge.a.coord} to {edge.b.coord}")