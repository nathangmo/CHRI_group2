import os
import pygame
from helpers import Cable
from Physics import Physics
import numpy as np
import time

pygame.init()
physics = Physics(hardware_version=3)
device_connected = physics.is_device_connected()

# Parameters
W, H = 800, 600
window_scale = 4000
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Cable Sim")

cables = [
    Cable((W // 6, H // 4), screen),
    Cable((W // 6, H // 4 + 100), screen),
    Cable((W // 6, H // 4 + 200), screen)
]

handle = pygame.transform.scale_by(pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "handle.png")), 0.75).convert_alpha(screen)

run = True
while run:
    time.sleep(0.01)
    screen.fill((255, 255, 255))

    if device_connected:
        mouse_pos = physics.get_mouse_pos(window_scale=window_scale, window_size=(W, H))
    else:
        mouse_pos = pygame.mouse.get_pos()

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
                        elif status == "green":
                            print("Safe")
                            cable.locked = False 
                    
                    # Locking the cable to the current mouse position
                    else:
                        cable.locked = True
                        cable.locked_position = pygame.Vector2(cable.points[-1])
                        print("Locked")
    
    if device_connected:
        F = np.zeros(2)
        F_locked_cable = np.zeros(2)
        F_cables = np.zeros(2)
        for cable in cables:
            if not cable.locked:
                F_locked_cable = cable.get_force()
        
        F_cables = pygame.Vector2(0,0)
        for cable in cables:
            F_cables += cable.get_lightning_force()

        F = F_cables + F_locked_cable
        physics.update_force(F)

    
    
    
    for cable in cables:
        cable.update(mouse_pos)
        cable.draw()

    screen.blit(handle, handle.get_rect(center = mouse_pos))

    pygame.display.flip()

physics.close()
pygame.quit()
