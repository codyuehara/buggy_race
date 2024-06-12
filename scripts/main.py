from game import Game
from drone import Drone
import time
import pygame
import os
from gate import Gate

# may want to create config/yaml file for this
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

pygame.display.set_caption("drone race")

def draw_window(drone, gates, n_gates_passed, text):
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

def player_handle_movement(keys_pressed, drone):
    VEL = 2
    pos = [0,0]
    if keys_pressed[pygame.K_w]: 
        #player.y -= VEL
        pos[1] -= VEL
    if keys_pressed[pygame.K_a]:
        #player.x -= VEL
        pos[0] -= VEL
    if keys_pressed[pygame.K_s]: 
        #player.y += VEL
        pos[1] += VEL
    if keys_pressed[pygame.K_d]:
        #player.x += VEL
        pos[0] += VEL
    drone.setPosition(pos)

def convertToPygame(x, y):
    x = x * 4 + WIDTH/2
    y = -y * 4 + HEIGHT/2
    return x, y

def init_gates():
    gate1 = Gate([0,50], 0)
    gate2 = Gate([30,-30], -45)
    gate3 = Gate([-70,-50], 10)
    gates = [gate1, gate2, gate3]
    return gates

def main():
    start_x, start_y = 0,90
    drone = Drone([start_x, start_y, 10])
    gates = init_gates()
    game = Game(drone, gates)
    pygame.font.init()
    my_font = pygame.font.SysFont('Comic Sans MS', 30)

    x, y = convertToPygame(start_x, start_y)
    pygame_gates = []
    for i in range(len(gates)):
        gate_x, gate_y = convertToPygame(gates[i].position[0], gates[i].position[1])
        print(gate_x, gate_y)
        pygame_gates.append(pygame.Rect(gate_x+GATE_WIDTH/2, gate_y+GATE_WIDTH/2, GATE_WIDTH, GATE_HEIGHT))

    player = pygame.Rect(x+DRONE_WIDTH/2, y+DRONE_HEIGHT/2, DRONE_WIDTH, DRONE_HEIGHT)
    clock = pygame.time.Clock()
    run = True
    thrusts = [0,0,0,0]
    user_controlled = False

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if game.done:
            break
        #     #display winner text

        #player and drone need to both see gates
        if user_controlled:
            keys_pressed = pygame.key.get_pressed()
            player_handle_movement(keys_pressed, drone)
        else:
            game.update(thrusts)
        x,y = convertToPygame(drone.getPosition()[0], drone.getPosition()[1])
        player.x = x +DRONE_WIDTH/2
        player.y = y +DRONE_HEIGHT/2
        text_surface = my_font.render("z: " + str(round(drone.getPosition()[2])), False, (0, 0, 0))

        draw_window(player, pygame_gates, drone.n_gates_passed, text_surface)

    pygame.quit()    

if __name__ == "__main__":
    main()