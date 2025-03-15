import pygame
import math

pygame.init()

# Parameters
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Cable Sim")

SEGMENTS, LENGTH = 10, 5
GRAVITY = pygame.Vector2(0, 5.0)

class Cable:
    def __init__(self, anchor):
        # Init parameters
        self.anchor = anchor
        self.points = [pygame.Vector2(anchor[0], anchor[1] + i * LENGTH) for i in range(SEGMENTS)]
        self.old_points = self.points[:]
        self.locked = True  # Initially locked
        self.locked_position = pygame.Vector2(anchor[0] + 100, anchor[1]) 

    def update(self, target):
        # Apply physics to each segment
        for i in range(1, SEGMENTS):
            if self.locked and i == SEGMENTS - 1:
                continue  # Skips when locked
            
            # Apply motion and gravity
            velocity = (self.points[i] - self.old_points[i]) * 0.98
            self.old_points[i] = self.points[i]
            self.points[i] += velocity + GRAVITY
        
        # Segment constraints
        for _ in range(10):
            self.points[0] = pygame.Vector2(self.anchor)
            for i in range(SEGMENTS - 1):
                delta = self.points[i + 1] - self.points[i]
                if delta.length():
                    correction = delta * ((delta.length() - LENGTH) / delta.length()) * 0.5
                    self.points[i] += correction
                    self.points[i + 1] -= correction

        # Locking mechanism
        if self.locked:
            self.points[-1] = pygame.Vector2(self.locked_position)
        else:
            self.points[-1] = pygame.Vector2(target)

    def draw(self):
        # Draw cable and connector ends
        for i in range(SEGMENTS - 1):
            pygame.draw.line(screen, (0, 0, 0), self.points[i], self.points[i + 1], 2)
        
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
        rectangle.fill((255, 0, 0))
    
        rotated_rect = pygame.transform.rotate(rectangle, -angle)
        self.red_rect_rect = rotated_rect.get_rect()
        self.red_rect_rect.center = end + unit_direction * 10
    
        screen.blit(rotated_rect, self.red_rect_rect.topleft)
    
        # --- Safe Connection Area (Green Port) ---
        square = pygame.Surface((12, 12), pygame.SRCALPHA)
        square.fill((0, 255, 0))
    
        rotated_square = pygame.transform.rotate(square, -angle)
        self.green_square_rect = rotated_square.get_rect()
        self.green_square_rect.center = end - unit_direction * 6
    
        screen.blit(rotated_square, self.green_square_rect.topleft)
    
    def check_hover_status(self, mouse_pos):
        # Check where the mouse is hovering
        if self.green_square_rect and self.green_square_rect.collidepoint(mouse_pos):
            return "green"
        if self.red_rect_rect and self.red_rect_rect.collidepoint(mouse_pos):
            return "red"
        return None

cables = [
    Cable((W // 6, H // 4)),
    Cable((W // 6, H // 4 + 100)),
    Cable((W // 6, H // 4 + 200))
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
