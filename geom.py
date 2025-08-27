"""
Module de géométrie pour la manipulation de points, arêtes, triangles et cellules dans le plan.

Ce module fournit des classes et fonctions utilitaires pour les calculs géométriques de base
(distances, milieux, centre de gravité, cercle circonscrit, etc.) ainsi que des objets structurants
pour la triangulation, les graphes de voisinage, et le diagramme de Voronoï.

Les classes sont :
    - Point : point du plan (éventuellement à l'infini)
    - Edge : arête reliant deux points (avec gestion des arêtes infinies)
    - Triangle : triangle défini par trois sommets
    - Cell : cellule définie par une liste d'arêtes

Des fonctions prédicats sont également fournies pour les tests d'appartenance, d'intersection, etc.
"""

from math import sqrt
from dataclasses import dataclass, field
from typing import Tuple, List

# ------------------------ Géométrie de base ------------------------

def square_dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Retourne la distance au carré entre deux points a et b."""
    x_a, y_a = a
    x_b, y_b = b
    return (x_b - x_a) ** 2 + (y_b - y_a) ** 2

def midpoint(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    """Retourne le milieu du segment [a, b]."""
    ax, ay = a
    bx, by = b
    return ((ax + bx) / 2, (ay + by) / 2)

def centroid(points: List[tuple[float, float]]) -> tuple[float, float]:
    """Retourne le centre de gravité d'une liste de points."""
    gx, gy = 0.0, 0.0
    for vx, vy in points:
        gx += vx
        gy += vy
    n = len(points)
    return (gx / n, gy / n)

def circumcenter(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> tuple[float, float]:
    """Retourne le centre du cercle circonscrit au triangle abc."""
    x_a, y_a = a
    x_b, y_b = b
    x_c, y_c = c
    DA = 2 * (x_a * (y_b - y_c) + x_b * (y_c - y_a) + x_c * (y_a - y_b))
    x = ((x_a**2 + y_a**2) * (y_b - y_c) +
         (x_b**2 + y_b**2) * (y_c - y_a) +
         (x_c**2 + y_c**2) * (y_a - y_b)) / DA
    y = ((x_a**2 + y_a**2) * (x_c - x_b) +
         (x_b**2 + y_b**2) * (x_a - x_c) +
         (x_c**2 + y_c**2) * (x_b - x_a)) / DA
    return (x, y)

# ------------------------ Prédicats ------------------------

def in_circle(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], p: tuple[float, float]) -> bool:
    """Teste si le point p est à l'intérieur du cercle circonscrit au triangle abc."""
    x_a, y_a = a
    x_b, y_b = b
    x_c, y_c = c
    x_p, y_p = p
    mat = [
        [x_a - x_p, y_a - y_p, (x_a - x_p) ** 2 + (y_a - y_p) ** 2],
        [x_b - x_p, y_b - y_p, (x_b - x_p) ** 2 + (y_b - y_p) ** 2],
        [x_c - x_p, y_c - y_p, (x_c - x_p) ** 2 + (y_c - y_p) ** 2]
    ]
    det = (
        mat[0][0] * (mat[1][1] * mat[2][2] - mat[2][1] * mat[1][2]) -
        mat[1][0] * (mat[0][1] * mat[2][2] - mat[2][1] * mat[0][2]) +
        mat[2][0] * (mat[0][1] * mat[1][2] - mat[1][1] * mat[0][2])
    )
    return det < 0

def in_triangle(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], p: tuple[float, float]) -> bool:
    """Teste si le point p est à l'intérieur du triangle abc."""
    test_1 = are_clockwise(a, b, p)
    test_2 = are_clockwise(b, c, p)
    test_3 = are_clockwise(c, a, p)
    return test_1 and test_2 and test_3

def segments_intersect(p1: tuple[float, float], p2: tuple[float, float], q1: tuple[float, float], q2: tuple[float, float]) -> bool:
    """Teste si les segments [p1, p2] et [q1, q2] se croisent."""
    test_1 = are_clockwise(p1, q1, q2) != are_clockwise(p2, q1, q2)
    test_2 = are_clockwise(p1, p2, q1) != are_clockwise(p1, p2, q2)
    return test_1 and test_2

def are_clockwise(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> bool:
    """Renvoie True si a, b, c sont dans le sens horaire."""
    x_a, y_a = a
    x_b, y_b = b
    x_c, y_c = c
    det = (x_b - x_a) * (y_c - y_a) - (y_b - y_a) * (x_c - x_a)
    return det <= 0

def in_Gab_Circle(a: tuple[float, float], b: tuple[float, float], p: tuple[float, float]) -> bool:
    """Renvoie True si p est dans le cercle de diamètre [ab]."""
    x_a, y_a = a
    x_b, y_b = b
    x_c = (x_a + x_b) / 2
    y_c = (y_a + y_b) / 2
    c = (x_c, y_c)
    r2 = ((x_a - x_b) ** 2 + (y_a - y_b) ** 2) / 4
    d2 = square_dist(c, p)
    return d2 < r2

def in_RNG_Moon(a: tuple[float, float], b: tuple[float, float], p: tuple[float, float]) -> bool:
    """Renvoie True si p est dans la lune de RNG de l'arête."""
    d2ab = square_dist(a, b)
    d2ap = square_dist(a, p)
    d2bp = square_dist(b, p)
    return d2ap < d2ab and d2bp < d2ab

# ------------------------ Objets géométriques ------------------------

@dataclass
class Point:
    """
    Représente un point du plan, éventuellement à l'infini.
    w (int): Poids homogène. Si w == 0, le point est à l'infini.
    """
    x: float
    y: float
    w: int = 1

    @property
    def coord(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def is_infinite(self) -> bool:
        return self.w == 0

    def __repr__(self) -> str:
        if self.is_infinite:
            return "Infinite point"
        return f"Point({self.x:.3f}, {self.y:.3f})"

    @staticmethod
    def midpoint(a: "Point", b: "Point") -> "Point":
        """Retourne le milieu de deux points."""
        mx, my = midpoint(a.coord, b.coord)
        return Point(mx, my)

    def is_in_circumcircle(self, triangle: "Triangle") -> bool:
        """Teste si le point est dans le cercle circonscrit du triangle."""
        a, b, c = triangle.vertices
        if c.is_infinite:
            return are_clockwise(a.coord, b.coord, self.coord)
        elif a.is_infinite:
            return are_clockwise(b.coord, c.coord, self.coord)
        elif b.is_infinite:
            return are_clockwise(c.coord, a.coord, self.coord)
        elif self.is_infinite:
            return False
        else:
            return in_circle(a.coord, b.coord, c.coord, self.coord)

    def is_in_triangle(self, triangle: "Triangle") -> bool:
        """Teste si le point est dans le triangle."""
        a, b, c = triangle.vertices
        if c.is_infinite:
            return are_clockwise(a.coord, b.coord, self.coord)
        elif a.is_infinite:
            return are_clockwise(b.coord, c.coord, self.coord)
        elif b.is_infinite:
            return are_clockwise(c.coord, a.coord, self.coord)
        elif self.is_infinite:
            return False
        else:
            return in_triangle(a.coord, b.coord, c.coord, self.coord)

    def is_in_Gab_circle(self, edge: "Edge") -> bool:
        """Teste si le point est dans le cercle de Gabriel de l'arête."""
        a, b = edge.vertices
        if a.is_infinite or b.is_infinite:
            return True
        elif self.is_infinite:
            return False
        else:
            return in_Gab_Circle(a.coord, b.coord, self.coord)

    def is_in_RNG_moon(self, edge: "Edge") -> bool:
        """Teste si le point est dans la RNG-moon de l'arête."""
        a, b = edge.vertices
        if a.is_infinite or b.is_infinite:
            return True
        elif self.is_infinite:
            return False
        else:
            return in_RNG_Moon(a.coord, b.coord, self.coord)

@dataclass
class Edge:
    """
    Représente une arête entre deux points (a, b).
    Peut être infinie. Nécessite un ref_point pour la dessiner.
    """
    a: Point
    b: Point
    ref_point: Point = field(default = None)

    def __repr__(self) -> str:
        return f"Edge({self.a}, {self.b})"

    @property
    def vertices(self) -> tuple[Point, Point]:
        """Renvoie les sommets de l'arête."""
        return (self.a, self.b)

    @property
    def is_infinite(self) -> bool:
        return self.a.is_infinite or self.b.is_infinite

    @property
    def square_length(self) -> float:
        return square_dist(self.a.coord, self.b.coord)

    def intersects(self, other: "Edge") -> bool:
        """Renvoie True si les segments finis se croisent."""
        a, b = self.vertices
        c, d = other.vertices
        return segments_intersect(a.coord, b.coord, c.coord, d.coord)

    @property
    def finite_vertex(self) -> Point:
        """Renvoie un sommet fini si l'arête est infinie d'un côté."""
        a, b = self.vertices
        if a.is_infinite:
            return b
        return a

    def desinfinite(self, dist: float) -> "Edge":
        """Renvoie une nouvelle arête avec des points à distance 'dist' pour affichage,
        utilisé pour tracer les cellules de Voronoi."""
        a, b = self.vertices
        if a.is_infinite and b.is_infinite:
            xm, ym = self.ref_point.coord
            x_d, y_d = a.coord
            norm = sqrt(x_d ** 2 + y_d ** 2)
            p1 = Point(xm + dist * x_d / norm, ym + dist * y_d / norm)
            p2 = Point(xm - dist * x_d / norm, ym - dist * y_d / norm)
            return Edge(p1, p2)
        elif a.is_infinite:
            x_s, y_s = b.coord
            x_d, y_d = a.coord
            norm = sqrt(x_d ** 2 + y_d ** 2)
            p = Point(x_s + dist * x_d / norm, y_s + dist * y_d / norm)
            return Edge(p, b)
        else:
            return Edge(b, a).desinfinite(dist)


@dataclass
class Triangle:
    """
    Représente un triangle défini par trois sommets.
    """
    a: Point
    b: Point
    c: Point

    @property
    def vertices(self) -> tuple[Point, Point, Point]:
        """Renvoie les sommets du triangle."""
        return (self.a, self.b, self.c)

    @property
    def is_infinite(self) -> bool:
        """Renvoie True si un sommet est à l'infini."""
        a, b, c = self.vertices
        return a.is_infinite or b.is_infinite or c.is_infinite

    @property
    def centroid(self) -> Point:
        """Renvoie le centre de gravité du triangle."""
        a, b, c = self.vertices
        if self.is_infinite:
            return Point(0, 0, 0)
        else:
            g_x, g_y = centroid([a.coord, b.coord, c.coord])
            return Point(g_x, g_y)

    @property
    def circumcenter(self) -> Point:
        """Renvoie le centre du cercle circonscrit."""
        a, b, c = self.vertices
        if c.is_infinite:
            norm = sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)
            x_dir = (b.y - a.y) / norm
            y_dir = -(b.x - a.x) / norm
            return Point(x_dir, y_dir, 0)
        elif a.is_infinite:
            return Triangle(b, c, a).circumcenter
        elif b.is_infinite:
            return Triangle(c, a, b).circumcenter
        else:
            cc_x, cc_y = circumcenter(a.coord, b.coord, c.coord)
            return Point(cc_x, cc_y)

@dataclass
class Cell:
    """Représente une cellule définie par une liste d'arêtes."""
    edges: List[Edge]


if __name__ == "__main__":
    p1 = (0, 0)
    p2 = (1, 1)
    q1 = (0, 1)
    q2 = (1, 0)
    a = segments_intersect(p2, p1, q1, q2)
    print(a)
    s = (.2, .2)
    b = in_triangle(p1, q2, q1, s)
    print(b)

    a = Point(1, 2)
    b = Point(2,3)
    c = Point(2, 3, 0)
    print(Edge(a, b))
    print(Edge(b, c))
    print(Triangle(a, b, c))