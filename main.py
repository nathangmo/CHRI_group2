# -*- coding: utf-8 -*-
import sys
import math
import time
import numpy as np
import pygame

from Physics import Physics
import helpers

def run():
    global window
    global running
    if device_connected:
        pA0,pB0,pA,pB,pE = physics.get_device_pos() #positions of the various points of the pantograph
        pA0,pB0,pA,pB,xh = helpers.convert_pos(pA0,pB0,pA,pB,pE, window_scale=windowscale, window_size=windowsize) #convert the physical positions to screen coordinates

    else:
        #TODO
        pass
        xh = np.array([400,300])

    fe = np.array([0.0,0.0])

    for event in pygame.event.get(): # interrupt function
        if event.type == pygame.QUIT: # force quit with closing the window
            running = False
        elif event.type == pygame.KEYUP:
            if event.key==ord("q"):
                running = False
            if event.key == ord('m'):
                pygame.mouse.set_visible(not pygame.mouse.get_visible())
    
    window.fill((255,255,255))
    
    
    if device_connected:
        physics.update_force(fe)
    else:
        #TODO
        pass
    pygame.display.flip()
        
def close():
    global physics
    physics.close()



windowscale = 800 # pixels per meter
windowsize = (800,600)
running = True



if __name__=="__main__":
    pygame.init()
    pygame.display.set_caption('Virtual Haptic Device')
    window = pygame.display.set_mode((800, 600)) 
    physics = Physics(hardware_version=3) #setup physics class. Returns a boolean indicating if a device is connected
    device_connected = physics.is_device_connected()

    try:
        while running:
            run()
    finally:
        close()