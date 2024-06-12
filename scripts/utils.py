import numpy as np
import math

def quaternionToRotationMatrix(q):
    #normalize q first
    q = q / np.linalg.norm(q)
    w, x, y, z  = q
    M = [[0 for _ in range(3)] for _ in range(3)] 
    M[0][0] = 1 - 2 * (y*y + z*z)
    M[0][1] = 2 * (x*y - w*z)
    M[0][2] = 2 * (w * y + x*z)
    M[1][0] = 2 * (x*y + w*z)
    M[1][1] = 1 - 2 * (x*x + z*z)
    M[1][2] = 2 * (y*z - w*x)
    M[2][0] = 2 * (x*z - w*y)
    M[2][1] = 2 * (w*x + y*z)
    M[2][2] = 1 - 2 * (x*x + y*y)
    return np.array(M)

def skewSymmetric(w):
    x, y, z = w
    M = [[0 for _ in range(4)] for _ in range(4)] 
    M[0] = [0, -x, -y, -z]
    M[1] = [x, 0, z, -y]
    M[2] = [y, -z, 0, x]
    M[3] = [z, y, -x, 0]
    return np.array(M)

def angleBetween(v1, v2):
    calc = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    if calc < -1 or calc > 1:
        return 0
    angle = np.arccos(calc)
    #print(angle)
    return angle * 180 / math.pi
