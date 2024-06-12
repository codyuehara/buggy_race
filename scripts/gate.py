import numpy as np
import math

class Gate():
    def __init__(self, pos, angle):
        self.width = 10
        self.thickness = 1
        self.position = np.array(pos)
        self.angle = angle
        self.rads = angle*(math.pi /180)
        w = self.width/2
        h = self.thickness/2

        c1 =np.array([-w, h])        
        c2 =  np.array([w, h]) 
        c3 = np.array([-w, -h]) 
        c4 =  np.array([w, -h]) 

        rot_matrix = np.array([[np.cos(self.rads), -np.sin(self.rads)], 
                              [np.sin(self.rads), np.cos(self.rads)]])
        
        self.c1 = (rot_matrix @ c1) + self.position
        self.c2 = (rot_matrix @ c2)+ self.position
        self.c3 = (rot_matrix @ c3)+ self.position
        self.c4 = (rot_matrix @ c4)+ self.position
        print("TEST: ", rot_matrix @ np.array([0,1]))

        print("gates [c1,c2,c3,c4]: ", self.c1, ", ", self.c2, ", ", self.c3, ", ", self.c4)