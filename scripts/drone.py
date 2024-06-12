import numpy as np
from utils import quaternionToRotationMatrix, skewSymmetric, angleBetween
import math

class Drone():
    def __init__(self, init_pos, m=1, J=[[0,0,0],[0,0,0],[0,0,0]], l=0, g=[0,0,-9.81]):
        super(Drone, self).__init__()
        self.m = m
        self.J = np.array([[2.5, 0, 0],
                           [0, 2.1, 0],
                           [0, 0, 4.3]])
        self.l = l
        self.g = np.array(g)
        self.n_gates_passed = 0
        self.D = np.array([[0.5, 0, 0],
                          [0, 0.25, 0],
                          [0, 0, 0]])
        self.force =0
        self.torque = np.array([0,0,0])
        self.addThrusts([10,10,0,0])

        init_att = np.array([1,0,0,0])

        self.prevR = quaternionToRotationMatrix(init_att)
        self.angleX = 0
        self.maxVel = [50,50,50]
        self.maxAngVel = [10,10,10]
        self.minVel = [-50,-50,-50]
        self.minAngVel = [-10,-10,-10]

        print("starting pos: ", init_pos)

        # [px, py, pz, vx, vy, vz, qw, qx, qy, qz, wx, wy, wz]
        self.states = np.array([init_pos[0], init_pos[1], init_pos[2], 0, 0, 0,\
                       init_att[0], init_att[1], init_att[2], init_att[3], 0,0,0])
        
    def ode(self, x, t):
        dots = [0] * len(self.states) 
        vel = self.getVelocity()
        angVel = self.getAngVelocity()
        dots[0], dots[1], dots[2] = vel

        R = quaternionToRotationMatrix(self.getQuaternion())

        acc = self.g + 1 / self.m * R @ np.array([0,0,self.force]) - R @ self.D @ R.transpose() @ vel
        dots[3], dots[4], dots[5] = acc

        skew = skewSymmetric(angVel)
        qdot = 0.5 * skew @ self.getQuaternion()
        dots[6], dots[7], dots[8], dots[9] = qdot

        angAcc = np.linalg.inv(self.J) @ (self.torque - np.cross(angVel, (self.J @ angVel)))
        dots[10], dots[11], dots[12] = angAcc

        return dots
    
    def checkMaxVel(self, vel):
        v = [max(vel[0], self.minVel[0]), max(vel[1], self.minVel[1]), max(vel[2], self.minVel[2]) ]
        return np.array([min(v[0], self.maxVel[0]),min(v[1], self.maxVel[1]),min(v[2], self.maxVel[2])])
    
    def checkMaxAngVel(self, angVel):
        w = [max(angVel[0], self.minVel[0]), max(angVel[1], self.minVel[1]), max(angVel[2], self.minVel[2]) ]
        return np.array([min(w[0], self.maxAngVel[0]),min(w[1], self.maxAngVel[1]),min(w[2], self.maxAngVel[2])])
    
    def addThrusts(self, thrusts):
        f1, f2, f3, f4 = thrusts
        l = 0.15
        ct = 1
        self.force = f1 + f2 + f3 + f4
        torquex = l / math.sqrt(2) * (f1 + f2 - f3 - f4)
        torquey = l / math.sqrt(2) * (-f1 + f2 + f3 - f4)
        torquez = ct * (f1 - f2 + f3 - f4)
        self.torque = np.array([torquex, torquey, torquez])
        #return force, np.array([torquex, torquey, torquez])


    def getPosition(self):
        p = np.array([self.states[0], self.states[1], self.states[2]])
        return p
    
    def getVelocity(self):
        v = np.array([self.states[3], self.states[4], self.states[5]])
        return v
    
    def getQuaternion(self):
        #w,x,y,z
        q = np.array([self.states[6], self.states[7], self.states[8], self.states[9]])
        return q
    
    def getAngVelocity(self):
        w = np.array([self.states[10], self.states[11], self.states[12]])
        return w
    
    def setPosition(self, pos):
        self.states[0] += pos[0]
        self.states[1] += pos[1]
        self.states[2] = 10

