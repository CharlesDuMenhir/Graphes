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

def isClockwise(a, b, c):
    """
    Renvoie True si a b c clockwise
    """
    ax, ay = a
    bx, by = b
    cx, cy = c

    det = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    return det > 0

def in_Gab_Circle(edge, p):
    a, b = edge
    # a, b, p sont des tuples (x, y)
    a_x, a_y = a
    b_x, b_y = b
    p_x, p_y = p
    c_x = (a_x + b_x) / 2
    c_y = (a_y + b_y) / 2
    r2 = ((a_x - b_x)**2 + (a_y - b_y)**2) / 4
    d2 = ((p_x - c_x)**2 + (p_y - c_y)**2)
    return d2 < r2



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