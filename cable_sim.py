import os
import pygame
from helpers import Cable
from helpers import Wall

from Physics import Physics
import time

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
hole_pos = (wall_pos[0]+(hole_size[0]/2), wall_size[1]/2)
wall = Wall(screen, wall_pos, wall_size,  hole_pos, hole_size)

handle = pygame.transform.scale_by(pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "handle.png")), 0.75).convert_alpha(screen)

run = True
try:
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
                            cable.locked_position = pygame.Vector2(mouse_pos)
                            print("Locked")

        wall.draw()

        if device_connected:
            F_locked_cable = pygame.Vector2(0,0)
            for cable in cables:
                if not cable.locked:
                    F_locked_cable = cable.get_force()

            F_shock = pygame.Vector2(0,0)
            for cable in cables:
                F_shock += cable.get_lightning_force()

        
        F_wall = pygame.Vector2(0,0)
        for cable in cables:
            cable.update(mouse_pos)
            cable.draw()

            # Check if cable end is inside the hole
            if wall.check_collision(cable.points[-1]):
                print("Cable is through the hole!")

            proxy_pos, F_wall_part = wall.collision_control(cable.points[-1])
            F_wall += F_wall_part

        if device_connected:
            F = F_shock + F_locked_cable - F_wall
            physics.update_force(F)

        screen.blit(handle, handle.get_rect(center = mouse_pos))
        pygame.display.flip()
except Exception as e:
    print(f"Exception occured: {e}")

physics.close()
pygame.quit()
