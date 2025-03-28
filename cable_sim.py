import os
import traceback
import pygame
from helpers import Cable
from helpers import Wall
from helpers import plot_data
from helpers import assist_controller
from helpers import special_control
from Physics import Physics
import time
import json
import datetime
import math
import random

pygame.init()
physics = Physics(hardware_version=3)
device_connected = physics.is_device_connected()
pygame.mouse.set_visible(False)
font = pygame.font.Font(pygame.font.get_default_font(), 36)
instruction_font = pygame.font.Font(pygame.font.get_default_font(), 24)

# Parameters
W, H = 800, 600
window_scale = 4000
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Cable Sirm")

wall_pos = (700, 0)
wall_size = (600, 600)
hole_size = (22, 10)  # one pixel on each end bigger
hole_pos = [(wall_pos[0] + (hole_size[0] / 2), wall_size[1] / 3),
            (wall_pos[0] + (hole_size[0] / 2), wall_size[1] / 2),
            (wall_pos[0] + (hole_size[0] / 2), 2 * wall_size[1] / 3),
            ]
hole_colors = [
    (0, 77 / 2, 64 / 2),
    (30 / 2, 136 / 2, 229 / 2),
    (255 / 2, 193 / 2, 7 / 2)
]
wall = Wall(screen, wall_pos, wall_size, hole_pos, hole_size, hole_colors)

handle = pygame.transform.scale_by(
    pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "handle.png")),
    0.75).convert_alpha(screen)

# Experiment parameters
total_users = 10  # Number of users in the study
total_trials = 15  # 5 baseline + 5 constant + 5 dynamic
trials_per_condition = 5
conditions = ["baseline", "constant", "dynamic"]


# Generate randomized condition order with blocks of 5 consecutive trials per condition
def generate_condition_order():
    # Create the condition blocks: 5 consecutive trials for each condition
    condition_blocks = []
    for cond in conditions:
        condition_blocks.append([cond] * trials_per_condition)

    # Shuffle the blocks to randomize the order of the conditions
    random.shuffle(condition_blocks)

    # Flatten the list into a single list of conditions
    condition_order = [cond for block in condition_blocks for cond in block]

    return condition_order


# Run experiment for each user
for user_id in range(1, total_users + 1):
    condition_order = generate_condition_order()
    print(f"User {user_id} condition order: {condition_order}")

    # Wait for 'r' key press only before first trial
    waiting_for_user = True
    while waiting_for_user:
        screen.fill((255, 255, 255))

        # Display instructions
        lines = [
            f"User {user_id} ready",
            "Please take position",
            "",
            "Press 'R' to begin your session",
            f"You will complete {total_trials} trials",
            "",
            "Press Q to quit"
        ]

        for i, line in enumerate(lines):
            text_surface = instruction_font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, dest=(W // 2 - text_surface.get_width() // 2, 100 + i * 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                physics.close()
                exit()
            elif event.type == pygame.KEYUP:
                if event.key == ord('q'):
                    pygame.quit()
                    physics.close()
                    exit()
                elif event.key == ord('r'):
                    waiting_for_user = False

    # Run trials for this user
    for trial_num, condition in enumerate(condition_order, 1):
        # Reset variables for each trial
        cables = [
            Cable((W // 6, H // 4), screen, (0, 77, 64), target=hole_pos[0]),
            Cable((W // 6, H // 4 + 100), screen, (30, 136, 229), target=hole_pos[1]),
            Cable((W // 6, H // 4 + 200), screen, (255, 193, 7), target=hole_pos[2])
        ]
        dummy_cable = Cable((W // 6, H // 4), screen, (0, 77, 64), target=hole_pos[0])
        cables[0].update((0, 0))
        cables[0].draw_connector_end()

        shocks = 0
        review_data = list()
        start_time = time.time()
        score = 0
        assist_active = False
        special_active = False
        special_collision = False
        special_collision_last = False
        special_collision_point = (0, 0)

        # Set condition for this trial
        if condition == "constant":
            assist_active = True
            special_active = False
        elif condition == "dynamic":
            assist_active = True
            special_active = True
        else:  # baseline
            assist_active = False
            special_active = False

        print(f"Starting trial {trial_num}/{total_trials} for user {user_id} - Condition: {condition}")

        # Trial loop
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

                if special_active and special_collision:
                    mouse_pos0 = special_collision_point[0] + (mouse_pos[0] - special_collision_point[0]) / 2
                    mouse_pos1 = special_collision_point[1] + (mouse_pos[1] - special_collision_point[1]) / 2
                    mouse_pos = (mouse_pos0, mouse_pos1)

                mouse_rect = pygame.rect.Rect(*mouse_pos, 1, 1)

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
                                        cable.enable_lightning(5)
                                        shocks += 1
                                    elif status == "green":
                                        cable.locked = False

                                        # Locking the cable to the current mouse position
                                else:
                                    if wall.check_in_hole(cable.red_rect_rect):
                                        accurracy = max(1, 100 - math.sqrt(
                                            (cable.target[0] - cable.red_rect_rect.center[0]) ** 2 + (
                                                    cable.target[1] - cable.red_rect_rect.center[1]) ** 2))
                                        print(f"Cable{cable.colour} scored {accurracy} points!")
                                        score -= cable.scored_points
                                        score += accurracy
                                        cable.scored_points = accurracy
                                        if cables[0].scored_points > 0 and cables[1].scored_points > 0 and cables[
                                            2].scored_points > 0:
                                            run = False

                                    elif not wall.check_in_hole(cable.red_rect_rect) and cable.scored_points:
                                        print(f"Cable{cable.colour} removed {cable.scored_points} points!")
                                        score -= cable.scored_points
                                        cable.scored_points = 0

                                    cable.locked = True
                                    cable.locked_position = pygame.Vector2(end_pos)

                unlocked_cable = dummy_cable
                for cable in cables:
                    if not cable.locked:
                        unlocked_cable = cable

                if mouse_pos[0] < 680:
                    end_pos = mouse_pos
                elif wall.check_collision(unlocked_cable.red_rect_rect) and not wall.check_in_hole(
                        unlocked_cable.red_rect_rect):
                    end_pos = (682, mouse_pos[1])
                elif wall.check_in_hole(unlocked_cable.red_rect_rect):
                    if mouse_pos[0] > 700:
                        end_pos = (700, mouse_pos[1])
                    else:
                        end_pos = (mouse_pos[0], mouse_pos[1])
                else:
                    end_pos = mouse_pos

                wall.draw()

                F_locked_cable = pygame.Vector2(0, 0)
                for cable in cables:
                    if not cable.locked:
                        F_locked_cable = cable.get_force_weight()

                F_shock = pygame.Vector2(0, 0)
                for cable in cables:
                    F_shock += cable.get_lightning_force()

                F_wall = pygame.Vector2(0, 0)
                for cable in cables:
                    cable.update(end_pos)
                    cable.draw()

                    proxy_pos, F_wall_part = wall.collision_control(mouse_pos, cable)
                    if not cable.locked:
                        F_wall += F_wall_part

                if not unlocked_cable.locked and assist_active:
                    F_assist = -0.7 * F_locked_cable
                else:
                    F_assist = pygame.Vector2(0, 0)

                F = F_shock + F_locked_cable - F_wall + F_assist

                special_collision = special_control(unlocked_cable, screen, hole_pos, special_active)
                if special_collision and not special_collision_last:
                    special_collision_point = end_pos
                    special_collision_last = True
                if not special_collision:
                    special_collision_last = False

                if device_connected:
                    physics.update_force(F)

                text = f"User {user_id} | Trial {trial_num}/{total_trials} | Condition: {condition} | Score: {str(round(score - time.time() + start_time))}"
                text_surface = font.render(text, True, (0, 0, 0))
                screen.blit(text_surface, dest=(0, 0))

                screen.blit(handle, handle.get_rect(center=mouse_pos))
                pygame.display.flip()

                data['time'] = time.time() - start_time
                data['Force'] = (F[0], F[1])
                data['Force_locked_cable'] = (F_locked_cable[0], F_locked_cable[1])
                data['Force_wall'] = (F_wall[0], F_wall[1])
                data['mouse_pos'] = mouse_pos
                data['end_pos'] = end_pos
                data['shocks'] = shocks
                data['score'] = score - time.time() + start_time
                data['assist_active'] = assist_active
                data['special_active'] = special_active
                data['condition'] = condition
                data['user_id'] = user_id
                data['trial_num'] = trial_num
                review_data.append(data)
        except Exception as e:
            print(f"Exception occurred: {e}")
            traceback.print_exc()

        print(f"Trial {trial_num} completed. Score: {score}")

        # Save trial data
        os.makedirs("experiments", exist_ok=True)
        filename = f"experiments/user{user_id}_trial{trial_num}_{condition}_data_{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.json"
        with open(filename, 'w') as file:
            json.dump(review_data, file)

physics.close()
pygame.quit()