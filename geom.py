"""
Module de géométrie
"""
from math import sqrt

#------------------------          Géométrie de base           ----------------------
# Pas d'objets, les points sont des couples, les triangles de triplets, etc...

def square_dist(a, b):
    x_a, y_a = a
    x_b, y_b = b
    d2 = ((x_b - x_a)**2 + (y_b - y_a)**2)
    return d2


def gravity_center(points):
    gx, gy = (0,0)
    for v in points:
        vx, vy = v
        gx = gx + vx
        gy = gy + vy
    n = len(points)
    return (gx / n, gy / n)

def circumcenter(a, b, c):
    x_a, y_a = a
    x_b, y_b = b
    x_c, y_c = c

    DA = 2 * (x_a*(y_b - y_c) + x_b*(y_c - y_a) + x_c*(y_a - y_b)) # correspond au double de l'aire signée
    if DA == 0:
        raise ValueError("Points alignés — pas de cercle circonscrit")

    x = ((x_a**2 + y_a**2)*(y_b - y_c) +
          (x_b**2 + y_b**2)*(y_c - y_a) +
          (x_c**2 + y_c**2)*(y_a - y_b)) / DA

    y = ((x_a**2 + y_a**2)*(x_c - x_b) +
          (x_b**2 + y_b**2)*(x_a - x_c) +
          (x_c**2 + y_c**2)*(x_b - x_a)) / DA

    return (x, y)



#------------------------         Prédicats           ----------------------

def in_circle(a, b, c, p): 
    """
    Teste si le point p est à l'intérieur du cercle circonscrit au triangle abc.
    Tous les points sont des tuples (x, y).
    """
    x_a, y_a = a
    x_b, y_b = b
    x_c, y_c = c
    x_p, y_p = p

    mat = [
        [x_a - x_p, y_a - y_p, (x_a - x_p)**2 + (y_a - y_p)**2],
        [x_b - x_p, y_b - y_p, (x_b - x_p)**2 + (y_b - y_p)**2],
        [x_c - x_p, y_c - y_p, (x_c - x_p)**2 + (y_c - y_p)**2]
    ]

    det = (
        mat[0][0] * (mat[1][1] * mat[2][2] - mat[2][1] * mat[1][2]) -
        mat[1][0] * (mat[0][1] * mat[2][2] - mat[2][1] * mat[0][2]) +
        mat[2][0] * (mat[0][1] * mat[1][2] - mat[1][1] * mat[0][2])
    )
    return det < 0  


def in_triangle(a, b, c, p):
    """
    Teste si le point p est à l'intérieur du triangle abc.
    Tous les points sont des tuples (x, y).
    """
    test_1 = are_clockwise(a, b, p)
    test_2 = are_clockwise(b, c, p)
    test_3 = are_clockwise(c, a, p)
    return test_1 and test_2 and test_3


def segments_intersect(p1, p2, q1, q2): # test si [p1, p2] croise [q1, q2]
    test_1 = are_clockwise(p1, q1, q2) != are_clockwise(p2, q1, q2)
    test_2 = are_clockwise(p1, p2, q1) != are_clockwise(p1, p2, q2)
    return test_1 and test_2


def are_clockwise(a, b, c):
    """
    Renvoie True si a b c clockwise
    """
    x_a, y_a = a
    x_b, y_b = b
    x_c, y_c = c
    det = (x_b - x_a) * (y_c - y_a) - (y_b - y_a) * (x_c - x_a)
    return det <= 0


def in_Gab_Circle(a, b, p):
    """
    Renvoie True si p est dans le cercle dont edge est l'arete
    """
    x_a, y_a = a
    x_b, y_b = b
    x_p, y_p = p
    x_c = (x_a + x_b) / 2
    y_c = (y_a + y_b) / 2
    c = (x_c, y_c)
    r2 = ((x_a - x_b)**2 + (y_a - y_b)**2) / 4
    d2 = square_dist(c, p)
    return d2 < r2

def in_RNG_Moon(a, b, p):
    """
    Renvoie True si p est dans la Moon dont edge est l'arete
    """
    d2ab = square_dist(a, b)
    d2ap = square_dist(a, p)
    d2bp = square_dist(b, p)
    return d2ap < d2ab and d2bp < d2ab


#------------------------------------       Objets géométriques          ------------------------

INF_P = (float("inf"), float("inf"))

class Oriented_Polygon:
    def __init__(self, points):
        #points est une liste ou un tuple de points (paire de coordonées)
        self.points = points

    def __repr__(self):
        str_points = ", ".join(f"({x:.3f},{y:.3f})" for x, y in self.points)
        return f"{self.__class__.__name__}[{str_points}]"

    @property
    def is_infinite(self):
        # renvoie True si un sommet est INF_P
        for p in self.points:
            if p == INF_P:
                return True
                break
        return False


class Oriented_Triangle(Oriented_Polygon):

    @property
    def circumcenter(self):
        a, b, c = self.points
        if c == INF_P:
            return INF_P
        elif a == INF_P:
            return INF_P
        elif b == INF_P:
            return INF_P
        else:
            return circumcenter(a, b, c)
    
    def is_in_conflict(self, p):
        # renvoie True si p est dans le cercle circonscrit au triangle
        a, b, c = self.points
        if c == INF_P:
            return are_clockwise(a, b, p)
        elif a == INF_P:
            return are_clockwise(b, c, p)
        elif b == INF_P:
            return are_clockwise(c, a, p)
        elif p == INF_P: # cas où a, b, c est fini mais pas p 
            return False
        else:
            return in_circle(a, b, c, p)
        
    def contains(self, p):
        # renvoie True si p est dans le triangle, ou visible par le triangle infini
        a, b, c = self.points
        if c == INF_P:
            return are_clockwise(a, b, p)
        elif a == INF_P:
            return are_clockwise(b, c, p)
        elif b == INF_P:
            return are_clockwise(c, a, p)
        elif p == INF_P: # cas où a, b, c est fini mais pas p 
            return False
        else:
            return in_triangle(a, b, c, p)
        

class Oriented_Edge(Oriented_Polygon):
    """
    Arête orientée de a vers b
    """
    # utilisé pour la triangulation de Delaunay
    @property
    def has_0_on_left(self):
        a, b = self.points
        return are_clockwise(a, b, (0, 0))
    
    
    def Gab_Circle_contains(self, p):
        # renvoie True si p est dans le cercle de diamètre [ab]
        a, b = self.points
        if a == INF_P:
            return True
        elif b == INF_P:
            return True
        elif p == INF_P: # cas où a, b, c est fini mais pas p 
            return False
        else:
            return in_Gab_Circle(a, b, p)
          
    def RNG_Moon_contains(self, p):      
        # renvoie True si p est dans la lune de [ab], l'intersection des cercles centrés sur a (resp b) qui passe par b (resp a)
        a, b = self.points
        if a == INF_P:
            return True
        elif b == INF_P:
            return True
        elif p == INF_P: # cas où a, b, c est fini mais pas p 
            return False
        else:
            return in_RNG_Moon(a, b, p)
    
class Ray():
    """
    Demi-droite définie par son point d'origine et point par lequel elle passe
    """
    # utilisé dans les cellules de Voronoi infinies 
    def __init__(self, source, vector):
        self.vertex = source
        self.direction = vector

    def get_point(self, dist):
        # renvoie le point de Ray à distance dist de sa source
        # utilsé pour l'affichage
        x_s, y_s = self.vertex
        x_d, y_d = self.direction
        norm = sqrt(x_d**2 + y_d**2)
        p = (x_s + dist * x_d / norm , y_s + dist * y_d / norm)
        return p

class Cell():
    def __init__(self, edges):
        self.edges = edges

if __name__ == "__main__":
    p1 = (0,0)
    p2 = (1,1)
    q1 = (0,1)
    q2 = (1,0)
    a = segments_intersect(p2, p1, q1, q2)
    print(a)

    s = (.2,.2)
    b = in_triangle(p1, q2, q1, s)
    print(b)

    p3 = (0.98765434567,1)
    tri = Oriented_Triangle([p1, p3, INF_P])
    print(tri)



