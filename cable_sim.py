import pygame
import math
from helpers import Cable

pygame.init()

# Parameters
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Cable Sim")


cables = [
    Cable((W // 6, H // 4), screen),
    Cable((W // 6, H // 4 + 100), screen),
    Cable((W // 6, H // 4 + 200), screen)
]

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == ord('q'):
                run = False
            elif event.key == ord('f'):
                for cable in cables:
                    # Unlocking the cable or warning the user based on mouse position
                    if cable.locked:
                        mouse_pos = pygame.mouse.get_pos()
                        status = cable.check_hover_status(mouse_pos)
                        
                        if status == "red":
                            print("Shocked")
                        elif status == "green":
                            print("Safe")
                            cable.locked = False  
                    
                    # Locking the cable to the current mouse position
                    else:
                        cable.locked = True
                        cable.locked_position = pygame.Vector2(cable.points[-1])
                        print("Locked")
    
    screen.fill((255, 255, 255))
    mouse_pos = pygame.mouse.get_pos()
    
    for cable in cables:
        cable.update(mouse_pos)
        cable.draw()
    
    pygame.display.flip()

pygame.quit()
