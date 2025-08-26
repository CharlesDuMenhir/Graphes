"""
Module de géométrie
"""
from math import sqrt

#------------------------          Géométrie de base           ----------------------
# Pas d'objets, les points sont des couples de coordonnées

def square_dist(a, b):
    x_a, y_a = a
    x_b, y_b = b
    d2 = ((x_b - x_a)**2 + (y_b - y_a)**2)
    return d2

def midpoint(a, b):
    ax, ay = a
    bx, by = b
    return ((ax + bx) / 2, (ay + by) / 2)

def centroid(points):
    gx, gy = (0,0)
    for v in points:
        vx, vy = v
        gx = gx + vx
        gy = gy + vy
    n = len(points)
    return (gx / n, gy / n)

def circumcenter(a, b, c): #a refaire car on peut avoir un circumcenter infini pour un triangle fini ( mais plat)
    x_a, y_a = a
    x_b, y_b = b
    x_c, y_c = c
    DA = 2 * (x_a*(y_b - y_c) + x_b*(y_c - y_a) + x_c*(y_a - y_b)) # correspond au double de l'aire signée
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
    Renvoie True si p est dans la Moon dont ab est l'arete
    """
    d2ab = square_dist(a, b)
    d2ap = square_dist(a, p)
    d2bp = square_dist(b, p)
    return d2ap < d2ab and d2bp < d2ab


#------------------------------------       Objets géométriques          ------------------------


class Point:
    """
    Point, peut être à l'infini si w==1, dans ce cas, (x,y) est la direction
    """
    def __init__(self, x, y, w = 1):
        self.coord = (x, y)
        self.w = w  # poids homogène

    def __repr__(self):
        if self.is_infinite:
            return "Infinite point"
        else:
            return "Point at" + str(self.coord)
    
    @property
    def x(self):
        return self.coord[0]
    
    @property
    def y(self):
        return self.coord[1]

    @property
    def is_infinite(self):
        return self.w == 0
    
    @staticmethod
    def midpoint(a, b):
        mx, my = midpoint(a.coord, b.coord)
        return Point(mx, my)

    def is_in_circumcircle(self, triangle):
        a, b, c = triangle.vertices
        if c.is_infinite:
            return are_clockwise(a.coord, b.coord, self.coord)
        elif a.is_infinite:
            return are_clockwise(b.coord, c.coord, self.coord)
        elif b.is_infinite:
            return are_clockwise(c.coord, a.coord, self.coord)
        elif self.is_infinite: # cas où a, b, c est fini mais pas self 
            return False
        else:
            return in_circle(a.coord, b.coord, c.coord, self.coord)

    def is_in_triangle(self, triangle):
        a, b, c = triangle.vertices
        if c.is_infinite:
            return are_clockwise(a.coord, b.coord, self.coord)
        elif a.is_infinite:
            return are_clockwise(b.coord, c.coord, self.coord)
        elif b.is_infinite:
            return are_clockwise(c.coord, a.coord, self.coord)
        elif self.is_infinite: # cas où a, b, c est fini mais pas self 
            return False
        else:
            return in_triangle(a.coord, b.coord, c.coord, self.coord)

    def is_in_Gab_circle(self, edge):
        # renvoie True si p est dans le cercle de diamètre [ab]
        a, b = edge.vertices
        if a.is_infinite or b.is_infinite:
            return True
        elif self.is_infinite: # cas où a et b sont finis mais pas p 
            return False
        else:
            return in_Gab_Circle(a.coord, b.coord, self.coord)
          
    def is_in_RNG_moon(self, edge):      
        # renvoie True si p est dans la lune de [ab], l'intersection des cercles centrés sur a (resp b) qui passe par b (resp a)
        a, b = edge.vertices
        if a.is_infinite or b.is_infinite:
            return True
        elif self.is_infinite: # cas où a et b sont finis mais pas p 
            return False
        else:
            return in_RNG_Moon(a.coord, b.coord, self.coord)


class Edge():
    """
    Arête [ab] (a, b:Point).
    Comme on travaille avec un point à l'infini, les arêtes sont représentées par 3 points, ses 2 extremité et un point de références fini. 
    """
    def __init__(self, a, b, c = Point(0, 0, 0)):
        self.vertices = (a, b)
        if not (a.is_infinite or b.is_infinite):
            self.ref_point = Point.midpoint(a, b)
        else:
            self.ref_point = c

    def __repr__(self):
        return f"{self.__class__.__name__}" + str(self.vertices)
    
    def type(self):
        a, b = self.vertices
        if a.is_infinite() and b.is_infinite():
            return "line"
        elif a.is_infinite() or b.is_infinite():
            return "ray"
        else:
            return "segment"


    @property
    # Si l'arete est infinie d'un côté, renvoie un sommet fini
    def finite_vertex(self):
        a, b = self.vertices
        if a.is_infinite:
            return b
        return a

    @property
    def is_infinite(self):
        a, b = self.vertices
        return a.is_infinite or b.is_infinite
    
    @property
    def square_length(self):
        a, b = self.vertices
        return square_dist(a.coord, b.coord)
    
    def intersects(self, other):
        # Renvoie True si les segments finis se croisent.
        a, b = self.vertices
        c, d = other.vertices
        return segments_intersect(a.coord, b.coord, c.coord, d.coord)
    
    
    def desinfinite(self, dist): # utilisé pour tracer les cellules de voronoi
        # renvoie le point d à distance dist de son point fini
        # pour afficher les aretes avec un point à l'infini, 
        a, b = self.vertices
        if a.is_infinite and b.is_infinite:
            xm, ym = self.ref_point.coord
            x_d, y_d = a.coord
            norm = sqrt(x_d**2 + y_d**2)
            p1 = Point(xm + dist * x_d / norm , ym + dist * y_d / norm)
            p2 = Point(xm - dist * x_d / norm , ym - dist * y_d / norm)
            return Edge(p1, p2)
        elif a.is_infinite:
            x_s, y_s = b.coord
            x_d, y_d = a.coord
            norm = sqrt(x_d**2 + y_d**2)
            p = Point(x_s + dist * x_d / norm , y_s + dist * y_d / norm)
            return Edge(p, b)
        else:
            return Edge(b, a).desinfinite(dist)


class Triangle:
    def __init__(self, a, b, c):
        self.vertices = (a, b, c)
    
    def __repr__(self):
        return f"{self.__class__.__name__}" + str(self.vertices)

    @property
    def is_infinite(self):
        a, b, c = self.vertices
        # renvoie True si un sommet est INF_P
        return a.is_infinite or b.is_infinite or c.is_infinite

    @property
    def centroid(self):
        # renvoie le centre de gravité du triangle, à l'infini, on n'a jamais besoin de leur direction
        a, b, c = self.vertices
        if self.is_infinite:
            return Point(0, 0, 0)
        else:
            g_x, g_y = centroid((a.coord , b.coord, c.coord))
            return Point(g_x, g_y)

    @property
    def circumcenter(self): 
        # Utilisé pour les cellules de Voronoi
        a, b, c = self.vertices
        if c.is_infinite:
            norm = sqrt((b.x - a.x)**2 + (b.y - a.y)**2)
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



