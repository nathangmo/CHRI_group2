import pygame
import math

def convert_pos(*positions, window_size, window_scale):
        #invert x because of screen axes
        # 0---> +X
        # |
        # |
        # v +Y
        device_origin = (int(window_size[0]/2.0 + 0.038/2.0*window_scale),0)

        converted_positions = []
        for physics_pos in positions:
            x = device_origin[0]-physics_pos[0]*window_scale
            y = device_origin[1]+physics_pos[1]*window_scale
            converted_positions.append([x,y])
        if len(converted_positions)<=0:
            return None
        elif len(converted_positions)==1:
            return converted_positions[0]
        else:
            return converted_positions

class Cable:
    def __init__(self, anchor, screen, segments=10, length= 5):
        # Init parameters
        self.screen = screen
        self.SEGMENTS, self.LENGTH = segments, length
        self.GRAVITY = pygame.Vector2(0, 5.0)
        self.anchor = anchor
        self.points = [pygame.Vector2(anchor[0], anchor[1] + i * self.LENGTH) for i in range(self.SEGMENTS)]
        self.old_points = self.points[:]
        self.locked = True  # Initially locked
        self.locked_position = pygame.Vector2(anchor[0] + 100, anchor[1]) 

    def update(self, target):
        # Apply physics to each segment
        for i in range(1, self.SEGMENTS):
            if self.locked and i == self.SEGMENTS - 1:
                continue  # Skips when locked
            
            # Apply motion and gravity
            velocity = (self.points[i] - self.old_points[i]) * 0.98
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
    
        self.screen.blit(rotated_rect, self.red_rect_rect.topleft)
    
        # --- Safe Connection Area (Green Port) ---
        square = pygame.Surface((12, 12), pygame.SRCALPHA)
        square.fill((0, 255, 0))
    
        rotated_square = pygame.transform.rotate(square, -angle)
        self.green_square_rect = rotated_square.get_rect()
        self.green_square_rect.center = end - unit_direction * 6
    
        self.screen.blit(rotated_square, self.green_square_rect.topleft)
    
    def check_hover_status(self, mouse_pos):
        # Check where the mouse is hovering
        if self.green_square_rect and self.green_square_rect.collidepoint(mouse_pos):
            return "green"
        if self.red_rect_rect and self.red_rect_rect.collidepoint(mouse_pos):
            return "red"
        return None

def draw_vector_file(inputfile: str):
    pygame.image.load(inputfile)