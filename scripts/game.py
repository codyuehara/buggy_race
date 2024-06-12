import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from random import randrange
from drone import Drone
from utils import quaternionToRotationMatrix
from rk4_integrator import RK4
import numpy as np
import math
from gate import Gate

class Game():
    def __init__(self, drone, gates):
        super(Game, self).__init__()
        self.gate_size = 10
        self.border_size = 1
        self.drone = drone
        self.done = False
        self.step_size = 0.01
        self.rk4 = RK4(self.drone, self.step_size)
        self.time = 0
        self.pos_history = []
        # hardcoding gates for now, in the future would like to randomly generate
        self.gates = np.array(gates)
        self.n_gates = len(self.gates)

        print("gate positions: ", self.gates)

    def endGame(self):
        print("game is over, your score is ", self.drone.n_gates_passed)
        self.done = True

    def update(self, thrusts):
        #dots = self.drone.ode()
        #self.drone.addThrusts(thrusts)
        self.rk4.step(self.drone.states, self.time)
        if self.collisionWithBoundaries():
            self.endGame()
        if self.checkGate():
            self.drone.n_gates_passed += 1
        self.checkWinCondition()
        self.pos_history.append(self.drone.getPosition())
        self.time += self.step_size
        # calculate 
        pass


    def checkGate(self):
        #TODO
        i = self.drone.n_gates_passed
        x, y, z = self.drone.getPosition()
        
        curr = self.gates[i]
        minX = min(curr.c1[0], curr.c2[0], curr.c3[0], curr.c4[0])
        maxX = max(curr.c1[0], curr.c2[0], curr.c3[0], curr.c4[0])
        minY = min(curr.c1[1], curr.c2[1], curr.c3[1], curr.c4[1])
        maxY = max(curr.c1[1], curr.c2[1], curr.c3[1], curr.c4[1])
        # print("current x ", x, ", y ", y)
        # print("minX ", minX, "maxX", maxX)
        # print("minY ", minY, "maxY", maxY)
        if x < minX or x > maxX or y < minY or y > maxY:
            return False
        print("gate passed!")
        return True
    
    def collisionWithBoundaries(self):
        x, y, z = self.drone.getPosition()
        if z < 0:
            print("hit ground")
            return True
        boundary = 100
        if x > boundary or x < -boundary or y > boundary or y < -boundary:
            print("hit wall")
            return True
        return False
    
    def checkWinCondition(self):
        if self.drone.n_gates_passed == self.n_gates:
            print("congrats, you win!")
            self.done = True

    def display(self):
        ax = plt.axes(projection="3d")

        for gate in self.gates:
            x, y, z = gate.tolist()
            ax.scatter(x, y, z)  
        
        for i in range(len(self.pos_history)):
            x, y, z = self.pos_history[i]
            ax.scatter(x, y, z)

        plt.show()

