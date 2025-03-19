import os
import traceback
import pygame
from helpers import Cable
from helpers import Wall
from helpers import plot_data
from Physics import Physics
import time
import json
import datetime

pygame.init()
physics = Physics(hardware_version=3)
device_connected = physics.is_device_connected()
pygame.mouse.set_visible(False)

# Parameters
W, H = 800, 600
window_scale = 4000
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Cable Sim")

cables = [
    Cable((W // 6, H // 4), screen, (0, 77, 64)),
    Cable((W // 6, H // 4 + 100), screen, (30, 136, 229)),
    Cable((W // 6, H // 4 + 200), screen, (255, 193, 7))
]

wall_pos = (700,0)
wall_size = (1200-wall_pos[0], 600)
hole_size = (22,10) # one pixel on each end bigger
hole_pos = [(wall_pos[0]+(hole_size[0]/2), wall_size[1]/3),
            (wall_pos[0]+(hole_size[0]/2), wall_size[1]/2),
            (wall_pos[0]+(hole_size[0]/2), 2*wall_size[1]/3),
            ]
hole_colors = [
    (0, 77/2, 64/2),
    (30/2, 136/2, 229/2),
    (255/2, 193/2, 7/2)
]
wall = Wall(screen, wall_pos, wall_size,  hole_pos, hole_size, hole_colors)

handle = pygame.transform.scale_by(pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "handle.png")), 0.75).convert_alpha(screen)
cables[0].update((0,0))
cables[0].draw_connector_end()

shocks = 0
review_data = list()
start_time = time.time()

run = True
try:
    while run:
        time.sleep(0.01)
        screen.fill((255, 255, 255))
        data = dict()

        if device_connected:
            mouse_pos = physics.get_mouse_pos(window_scale=window_scale, window_size=(W, H))
        else:
            mouse_pos = pygame.mouse.get_pos()
        mouse_rect = pygame.rect.Rect(*mouse_pos, 1,1)
        
        
        unlocked_cable = cables[0]
        for cable in cables:
            if not cable.locked:
                unlocked_cable = cable
        if not wall.check_collision(mouse_rect):
            end_pos = mouse_pos
        elif wall.check_collision(red_rect=unlocked_cable.red_rect_rect):
            end_pos = (700,mouse_pos[1])
        else:
            end_pos = mouse_pos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYUP:
                if event.key == ord('q'):
                    run = False
                elif event.key == ord(' '):
                    for cable in cables:
                        # Unlocking the cable or warning the user based on mouse position
                        if cable.locked:
                            status = cable.check_hover_status(mouse_pos)
                            
                            if status == "red":
                                print("Shocked")
                                cable.enable_lightning(5)
                                shocks += 1
                            elif status == "green":
                                print("Safe")
                                cable.locked = False 
                        
                        # Locking the cable to the current mouse position
                        else:
                            cable.locked = True
                            cable.locked_position = pygame.Vector2(mouse_pos)
                            print("Locked")

        wall.draw()

        F_locked_cable = pygame.Vector2(0,0)
        for cable in cables:
            if not cable.locked:
                F_locked_cable = cable.get_force()

        F_shock = pygame.Vector2(0,0)
        for cable in cables:
            F_shock += cable.get_lightning_force()

        
        F_wall = pygame.Vector2(0,0)
        for cable in cables:
            cable.update(end_pos)
            cable.draw()

            # Check if cable end is inside the hole
            if wall.check_collision(unlocked_cable.red_rect_rect):
                print("Cable is through the hole!")

            proxy_pos, F_wall_part = wall.collision_control(mouse_pos, cable)
            if not cable.locked:
                F_wall += F_wall_part

        F = F_shock + F_locked_cable - F_wall
        if device_connected:
            physics.update_force(F)
        

        

        screen.blit(handle, handle.get_rect(center = mouse_pos))
        pygame.display.flip()

        data['time'] = time.time()-start_time
        data['Force'] = (F[0], F[1])
        data['Force_locked_cable'] = (F_locked_cable[0], F_locked_cable[1])
        data['Force_wall'] = (F_wall[0], F_wall[1])
        data['mouse_pos'] = mouse_pos
        data['end_pos'] = end_pos
        data['shocks'] = shocks
        review_data.append(data)
except Exception as e:
    print(f"Exception occured: {e}")
    traceback.print_exc()

physics.close()
pygame.quit()

with open(f"Cable_data_{datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}.json", 'w') as file:
    json.dump(review_data, file)

plot_data(review_data)