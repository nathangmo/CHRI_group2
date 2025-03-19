import os
import time
import pygame
import math
import matplotlib.pyplot as plt
import numpy as np

class Cable:
    def __init__(self, anchor, screen, colour, segments=20, length=5):
        # Init parameters
        self.lightning = pygame.transform.scale_by(pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "lightning.png")), 0.1)
        self.lightning_enable = False
        self.lightning_enabled_on = time.time()
        self.lightning_show_for = 5 #seconds
        self.lightning_time_to_run = 0
        self.screen = screen
        self.SEGMENTS, self.LENGTH = segments, length
        self.GRAVITY = pygame.Vector2(0, 5.0)
        self.anchor = anchor
        self.points = [pygame.Vector2(anchor[0], anchor[1] + i * self.LENGTH) for i in range(self.SEGMENTS)]
        self.old_points = self.points[:]
        self.locked = True  # Initially locked
        self.locked_position = pygame.Vector2(anchor[0] + 100, anchor[1]) 
        self.colour = colour

    def update(self, target):
        # Apply physics to each segment
        for i in range(1, self.SEGMENTS):
            if self.locked and i == self.SEGMENTS - 1:
                continue  # Skips when locked

            # Apply motion and gravity
            velocity = (self.points[i] - self.old_points[i]) #* 0.98
            self.old_points[i] = self.points[i]
            self.points[i] += velocity + self.GRAVITY

        # Segment constraints
        for _ in range(10):
            self.points[0] = pygame.Vector2(self.anchor)
            for i in range(self.SEGMENTS - 1):
                delta = self.points[i + 1] - self.points[i]
                if delta.length():
                    correction = delta * ((delta.length() - self.LENGTH) / delta.length()) * 0.5
                    self.points[i] += correction
                    self.points[i + 1] -= correction

        # Locking mechanism
        if self.locked:
            self.points[-1] = pygame.Vector2(self.locked_position)
        else:
            self.points[-1] = pygame.Vector2(target)

    def draw(self):
        # Draw cable and connector ends
        for i in range(self.SEGMENTS - 1):
            pygame.draw.line(self.screen, (0, 0, 0), self.points[i], self.points[i + 1], 2)
            #pygame.draw.circle(self.screen, (255, 0, 0), self.points[i], 2)
        self.draw_connector_end()

    def draw_connector_end(self):
        # Align with the end of the cable
        end = self.points[-1]
        prev = self.points[-2]
        direction = end - prev
        angle = math.degrees(math.atan2(direction.y, direction.x))

        unit_direction = direction.normalize()

        # --- Connector (Red Plug) ---
        rectangle = pygame.Surface((20, 8), pygame.SRCALPHA)
        rectangle.fill((216, 27, 96))
        rotated_rect = pygame.transform.rotate(rectangle, -angle)
        self.red_rect_rect = rotated_rect.get_rect()
        self.red_rect_rect.center = end + unit_direction * 10

        self.screen.blit(rotated_rect, self.red_rect_rect.topleft)

        # --- Safe Connection Area (Green Port) ---
        square = pygame.Surface((12, 12), pygame.SRCALPHA)
        square.fill(self.colour)
    
        rotated_square = pygame.transform.rotate(square, -angle)
        self.green_square_rect = rotated_square.get_rect()
        self.green_square_rect.center = end
    
        self.green_square_rect.center = end - unit_direction * 6

        self.screen.blit(rotated_square, self.green_square_rect.topleft)

        # --- Draw Shocked ---
        if self.lightning_enable:
            self.lightning_time_to_run = self.lightning_enabled_on + self.lightning_show_for - time.time()
            rotated_square = pygame.transform.rotate(pygame.transform.scale_by(self.lightning, (math.sin(self.lightning_time_to_run*math.pi*2)+1)/2), -angle)
            
            time_to_run = self.lightning_enabled_on + self.lightning_show_for - time.time()
            rotated_square = pygame.transform.rotate(pygame.transform.scale_by(self.lightning, (math.sin(time_to_run*math.pi*2)+1)/2), -angle)

            self.shock_square_rect = rotated_square.get_rect()
            self.shock_square_rect.center = end + 24*unit_direction
        
            self.shock_square_rect.center = end+30*unit_direction - unit_direction * 6

            self.screen.blit(rotated_square, self.shock_square_rect.topleft)

            if self.lightning_time_to_run < 0:
                self.lightning_enable = False

    def enable_lightning(self, show_for = None):
        if show_for is not None:
            self.lightning_show_for = show_for
        self.lightning_enable = True
        self.lightning_enabled_on = time.time()

    def check_hover_status(self, mouse_pos):
        # Check where the mouse is hovering
        if self.green_square_rect and self.green_square_rect.collidepoint(mouse_pos):
            return "green"
        if self.red_rect_rect and self.red_rect_rect.collidepoint(mouse_pos):
            return "red"
        return None

    def get_lightning_force(self):
        if self.lightning_enable:
            lightning_perturbation = pygame.Vector2(math.sin(self.lightning_time_to_run*10), math.cos(self.lightning_time_to_run*10))
        else:
            lightning_perturbation = pygame.Vector2(0, 0)
        return 3*lightning_perturbation

    def get_force(self):
        end = self.points[-1]
        prev = self.points[-2]
        direction = end - prev
        unit_direction = direction.normalize()
        return unit_direction #TODO hier schaal factor berekenen op basis van gewicht etc

class Wall:
    def __init__(self, screen, position, size, holes_positions, hole_size, hole_colors):
        self.screen = screen
        self.position = position
        self.size = size
        self.holes_positions = holes_positions
        self.hole_size = hole_size
        self.hole_colors = hole_colors
        self.prev_xh = pygame.Vector2(0.0, 0.0)
        self.kc = 100  # Stiffness constant for the force feedback
        self.holes_rects = list()

        # Define the full wall and the hole as pygame.Rect objects
        self.wall_rect = pygame.Rect(self.position, self.size)
        for hole in self.holes_positions:
            self.holes_rects.append(pygame.Rect(
                                    hole[0] - self.hole_size[0] // 2,
                                    hole[1] - self.hole_size[1] // 2,
                                    self.hole_size[0],
                                    self.hole_size[1])
                                    )
            

    def draw(self):
        wall_rect = pygame.Rect(self.position, self.size)
        pygame.draw.rect(self.screen, (64, 64, 64), wall_rect)

        for i, hole_rect in enumerate(self.holes_rects):
            pygame.draw.rect(self.screen, self.hole_colors[i], hole_rect)

    def check_collision(self, red_rect):
        for hole_rect in self.holes_rects:
            if hole_rect.colliderect(red_rect):
                return False
        
        
        if self.wall_rect.colliderect(red_rect):
            return True
                
        return False

    def collision_control(self, cable_end_pos, cable):
        hx, hy = cable_end_pos  # Cable end position

        # Store previous position
        prev_hx, prev_hy = self.prev_xh
        self.prev_xh = pygame.Vector2([hx, hy])

        proxy_pos = pygame.Vector2([hx, hy])
        fe = pygame.Vector2([0.0, 0.0])

        # Check if cable end is inside the wall but NOT in the hole
        if self.check_collision(red_rect=cable.red_rect_rect):

            fe[0] = self.kc * (self.wall_rect.left - hx)
            proxy_pos = pygame.Vector2(self.wall_rect.left, hy)


            if not cable.locked:

                force_end = proxy_pos - fe * 0.01  # Scale factor for drawing
                pygame.draw.line(self.screen, (0, 0, 255), proxy_pos, force_end, 2)

        else:
            self.entry_side = None  # Reset when outside the wall
        return proxy_pos, fe  # Return adjusted position and force








def plot_data(review_data):

    t = list()
    force = list()
    end_pos = list()
    mouse_pos = list()
    for item in review_data:
        t.append(item['time'])
        force.append(item['Force'])
        end_pos.append(item['end_pos'])
        mouse_pos.append(item['mouse_pos'])

    force = np.array(force)
    end_pos = np.array(end_pos)
    mouse_pos = np.array(mouse_pos)

    plt.subplot(413)
    plt.plot(t,force,"b")
    plt.plot(t,force,"r")
    plt.ylabel("F [N]")
    plt.show()

    plt.figure(3)
    plt.subplot(411)
    plt.title("VARIABLES")
    plt.plot(t,end_pos[:,0],"b",label="x")
    plt.plot(t,end_pos[:,1],"r",label="y")
    plt.legend()
    plt.ylabel("end_pos [m]")

    plt.subplot(412)
    plt.plot(t,mouse_pos[:,0],"b")
    plt.plot(t,mouse_pos[:,1],"r")
    plt.ylabel("mouse_pos [m]")





    # plt.figure(4)
    # plt.title("ENDPOINT BEHAVIOUR")
    # plt.plot(0,0,"ok",label="shoulder")
    # plt.plot(state[:,1],state[:,2],"lime",label="reference")
    # plt.plot(state[:,3],state[:,4],"r",label="actual")
    # plt.axis('equal')
    # plt.xlabel("x [m]")
    # plt.ylabel("y [m]")
    # plt.legend()

    # plt.tight_layout()



    plt.show()


