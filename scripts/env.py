import gymnasium
import numpy as np
from gymnasium import spaces
from drone import Drone
from gate import Gate
import random
import pygame
import os
import math
from rk4_integrator import RK4

WIDTH, HEIGHT = 800, 800
GATE_WIDTH, GATE_HEIGHT = 100, 100
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
DRONE_WIDTH, DRONE_HEIGHT = 75, 60
DRONE_IMG = pygame.image.load(os.path.join('Assets', 'Vikavolt.png'))
DRONE = pygame.transform.scale(DRONE_IMG, (DRONE_WIDTH, DRONE_HEIGHT))
GATE_IMG = pygame.image.load(os.path.join('Assets', 'gate.png'))
GATE_DONE_IMG = pygame.image.load(os.path.join('Assets', 'gate-done.png'))
GATE = pygame.transform.scale(GATE_IMG, (GATE_WIDTH, GATE_HEIGHT))
GATE_DONE = pygame.transform.scale(GATE_DONE_IMG, (GATE_WIDTH, GATE_HEIGHT))

class DroneEnv(gymnasium.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(DroneEnv, self).__init__()
        #define action and observation space
        # they must be gym.spaces objects
        self.action_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)
        mins = np.array([-1,-1, 0, -1, 0])
        maxs = np.array([1,1,1, 1, 1])
        # self.observation = [x, y, z, dist, vel]
        self.observation_space = spaces.Box(low=mins, high=maxs, dtype=np.float64)

        self.render_mode = "human"
        self.window = None
        self.clock = None

    def update(self, thrusts):
        #dots = self.drone.ode()
        self.drone.addThrusts(thrusts)
        self.rk4.step(self.drone.states, self.time)
        self.time += self.step_size

    def checkGate(self):
        i = self.drone.n_gates_passed
        x, y, z = self.drone.getPosition()
        
        curr = self.gates[i]
        minX = min(curr.c1[0], curr.c2[0], curr.c3[0], curr.c4[0])
        maxX = max(curr.c1[0], curr.c2[0], curr.c3[0], curr.c4[0])
        minY = min(curr.c1[1], curr.c2[1], curr.c3[1], curr.c4[1])
        maxY = max(curr.c1[1], curr.c2[1], curr.c3[1], curr.c4[1])

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
        if x > boundary or x < -boundary or y > boundary or y < -boundary or z > boundary:
            print("hit wall")
            return True
        return False

    def step(self, action):
        # assuming action = [f1,f2,f3,f4]
        action = 10 * action
        print("action: ", action)
        self.update(action)
        # may want to add time limit
        self.reward -= 0.001 # penalize for longer time or reward for staying in air?

        if self.collisionWithBoundaries():
            self.reward = -100
            self.done = True
        elif self.reward < -100:
            print("ran out of time")
            self.done = True

        x, y, z = self.drone.getPosition()
        dist_from_gate = math.sqrt((x-self.gates[self.score].position[0])**2 + (y-self.gates[self.score].position[1])**2)
        vel_norm = np.linalg.norm(self.drone.getVelocity())

        if self.checkGate():
            self.drone.n_gates_passed += 1
            self.score += 1
            self.reward = 30
        elif dist_from_gate < self.dist_last_step:
            #self.reward += 0.0001 * (100 - dist_from_gate) 
            self.reward = 1
        else:
            self.reward = -1
        self.dist_last_step = dist_from_gate

        #self.reward += 0.01 * vel_norm
        #print("action: ", action, ", reward: ", self.reward)
        #print(self.gates[self.score].position, " + dist from gate: ", dist_from_gate)

        if self.drone.n_gates_passed == len(self.gates):
            print("congrats, you win!")
            self.reward = 200
            self.done = True

        self.observation = np.array([x, y, z, dist_from_gate, vel_norm])
        print("obs: ", self.observation)


        if self.render_mode == "human":
            self.render()

        return self.observation, self.reward, self.done, False, {}
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.done = False
        self.start_pos = [0,90]
        #self.start_pos = [random.randrange(-100, 100),random.randrange(-100,100)] 
        self.drone = Drone([self.start_pos[0], self.start_pos[1], 10])
        #gate1 = Gate([0,50], 0)
        gate2 = Gate([30,-30], -45)
        #gate3 = Gate([-70,-50], 10)  
        #self.gates = [gate1, gate2, gate3]
        self.gates = [gate2]
        self.step_size = 0.01
        self.rk4 = RK4(self.drone, self.step_size)
        self.time = 0
        #game = Game(drone, gates)
        #self.score = random.randrange(0, 2) 
        self.score = 0
        self.drone.n_gates_passed = self.score
        print("start pos, score: ", self.start_pos, self.score)
        self.reward = 0
        self.dist_last_step = 1000

        # x, y, z, current_gate_x_dist, current_gate_y_dist, vel?
        x, y, z = self.drone.getPosition()
        dist_from_gate = math.sqrt((x-self.gates[self.score].position[0])**2 + (y-self.gates[self.score].position[1])**2)

        vel = np.linalg.norm(self.drone.getVelocity())

        self.observation = np.array([x, y, z, dist_from_gate, vel])

        if self.render_mode == "human":
            self.render()

        return self.observation, {}
    
    def convertToPygame(self, x, y):
        x = x * 4 + WIDTH/2
        y = -y * 4 + HEIGHT/2
        return x, y
    
    def draw_window(self, drone, gates, n_gates_passed, text):
        WIN.fill((255,255,255))

        for i in range(len(gates)):
            if i >= n_gates_passed:
                WIN.blit(GATE, (gates[i].x-GATE_WIDTH, gates[i].y-GATE_HEIGHT))
            else:
                # done gates
                WIN.blit(GATE_DONE, (gates[i].x-GATE_WIDTH, gates[i].y-GATE_HEIGHT))

        WIN.blit(DRONE, (drone.x - DRONE_WIDTH, drone.y - DRONE_HEIGHT))
        WIN.blit(text, (0,0))

        pygame.display.update()
    
    def render(self, mode='human'):
        if self.window is None:
            pygame.init()
            pygame.display.init()
            pygame.display.set_caption("drone race")
            self.window = pygame.display.set_mode((900,900))

        if self.clock is None:
            self.clock = pygame.time.Clock()

        x, y = self.convertToPygame(self.start_pos[0], self.start_pos[1])
        pygame.font.init()

        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        pygame_gates = []
        for i in range(len(self.gates)):
            gate_x, gate_y = self.convertToPygame(self.gates[i].position[0], self.gates[i].position[1])
            pygame_gates.append(pygame.Rect(gate_x+GATE_WIDTH/2, gate_y+GATE_WIDTH/2, GATE_WIDTH, GATE_HEIGHT))

        player = pygame.Rect(x+DRONE_WIDTH/2, y+DRONE_HEIGHT/2, DRONE_WIDTH, DRONE_HEIGHT)

        if self.render_mode == "human":
            self.clock.tick(FPS)
            pygame.event.pump()
            x,y = self.convertToPygame(self.drone.getPosition()[0], self.drone.getPosition()[1])
            player.x = x +DRONE_WIDTH/2
            player.y = y +DRONE_HEIGHT/2
            text_surface = my_font.render("z: " + str(round(self.drone.getPosition()[2])), False, (0, 0, 0))

            self.draw_window(player, pygame_gates, self.drone.n_gates_passed, text_surface)

        # pygame.quit()   
