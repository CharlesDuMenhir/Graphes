"""
Module de géométrie
"""

#------------------------          Géométrie de base           ----------------------


def square_dist(a, b):
    ax, ay = a
    bx, by = b
    d2 = ((bx - ax)**2 + (by - ay)**2)
    return d2


def gravity_center(vertices):
    gx, gy = (0,0)
    for v in vertices:
        vx, vy = v
        gx = gx + vx
        gy = gy + vy
    n = len(vertices)
    return (gx / n, gy / n)

#------------------------         Prédicats           ----------------------

def in_circle(a, b, c, p): 
    """
    Teste si le point p est à l'intérieur du cercle circonscrit au triangle abc.
    Tous les points sont des tuples (x, y).
    """
    ax, ay = a
    bx, by = b
    cx, cy = c
    px, py = p

    mat = [
        [ax - px, ay - py, (ax - px)**2 + (ay - py)**2],
        [bx - px, by - py, (bx - px)**2 + (by - py)**2],
        [cx - px, cy - py, (cx - px)**2 + (cy - py)**2]
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
    ax, ay = a
    bx, by = b
    cx, cy = c
    det = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    return det <= 0


def in_Gab_Circle(a, b, p):
    """
    Renvoie True si p est dans le cercle dont edge est l'arete
    """
    ax, ay = a
    bx, by = b
    px, py = p
    cx = (ax + bx) / 2
    cy = (ay + by) / 2
    c = (cx, cy)
    r2 = ((ax - bx)**2 + (ay - by)**2) / 4
    d2 = square_dist(c, p)
    return d2 < r2


#------------------------------------       Objets géométriques          ------------------------

INF_P = (float("inf"), float("inf"))

class Oriented_Face:
    def __init__(self, vertices):
        self.vertices = vertices # un dart de reference

    def __repr__(self):
        verts = ", ".join(f"({x:.3f},{y:.3f})" for x, y in self.vertices)
        return f"{self.__class__.__name__}[{verts}]"

    @property
    def is_infinite(self):
        # renvoie True si un sommet est INF_P
        is_inf = False
        for v in self.vertices:
            if v == INF_P:
                is_inf = True
                break
        return is_inf


class Oriented_Triangle(Oriented_Face):
    
    def is_in_conflict(self, p):
        # renvoie True si p est dans le cercle circonscrit au triangle
        a, b, c = self.vertices
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
        
    def is_visible_from(self, p):
        # renvoie True si p est dans le triangle, ou visible par le triangle infini
        a, b, c = self.vertices
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
        

class Oriented_Edge(Oriented_Face):

    @property
    def has_0_on_left(self):
        a, b = self.vertices
        return are_clockwise(a, b, (0, 0))

    def Gab_Circle_contains(self, p):
        # renvoie True si p est dans le cercle circonscrit au triangle
        a, b = self.vertices
        if a == INF_P:
            return True
        elif b == INF_P:
            return True
        elif p == INF_P: # cas où a, b, c est fini mais pas p 
            return False
        else:
            return in_Gab_Circle(a, b, p)
        

    


def create_copies(points, width):
    # crée des copies de la liste de points autour de l'écran
    # w est la largueur de l'écran
    copies = []
    h_width = width // 2
    for p in points: # faire une fonction
        px, py = p
        if px < h_width and py < h_width:
            copies.append((px + width, py))
            copies.append((px, py + width))
            copies.append((px + width, py + width))
        if px < h_width and py >= h_width:
            copies.append((px + width, py))
            copies.append((px, py - width))
            copies.append((px + width, py - width))
        if px >= h_width and py < h_width:
            copies.append((px - width, py))
            copies.append((px, py + width))
            copies.append((px - width, py + width))
        if px >= h_width and py >= h_width:
            copies.append((px - width, py))
            copies.append((px, py - width))
            copies.append((px - width, py - width))
    return(copies)

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



