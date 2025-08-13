def in_circle( a, b, c, p): 
    """
    Teste si le point p est à l'intérieur du cercle circonscrit au triangle abc.
    Tous les points sont des tuples (x, y).
    """
    ax, ay = a
    bx, by = b
    cx, cy = c
    px, py = p

    # Matrice de déterminant
    mat = [
        [ax - px, ay - py, (ax - px)**2 + (ay - py)**2],
        [bx - px, by - py, (bx - px)**2 + (by - py)**2],
        [cx - px, cy - py, (cx - px)**2 + (cy - py)**2]
    ]

    # Calcul du déterminant
    det = (
        mat[0][0] * (mat[1][1] * mat[2][2] - mat[2][1] * mat[1][2]) -
        mat[1][0] * (mat[0][1] * mat[2][2] - mat[2][1] * mat[0][2]) +
        mat[2][0] * (mat[0][1] * mat[1][2] - mat[1][1] * mat[0][2])
    )
    return det > 0  

def have_common_element(l1, l2):
    """Teste si deux listes ont des élément en commun"""
    return bool(set(l1) & set(l2))

def isClockwise(a, b, c):
    """
    Renvoie True si a b c clockwise
    """
    ax, ay = a
    bx, by = b
    cx, cy = c

    det = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    return det > 0
