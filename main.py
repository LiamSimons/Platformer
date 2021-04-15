import pygame
import sys
import random

from pygame.locals import *

# INITIALISATIONS
clock = pygame.time.Clock()

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

pygame.mixer.set_num_channels(64)  # how many sounds can play at the same time

pygame.display.set_caption("Pygame Window")

main_font = pygame.font.SysFont("comicsans", 50)

# VARIABLES
WINDOW_SIZE = (600, 400)
TILE_SIZE = 16
FPS = 60

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

display = pygame.Surface((300, 200))

# player_image = pygame.transform.scale(pygame.image.load('Assets/player.png'), (20, 20))
# player_image.set_colorkey((255, 255, 255))
# this makes the white pixels in the player image transparent

grass_image = pygame.transform.scale(pygame.image.load('Assets/grass.png'), (TILE_SIZE, TILE_SIZE))
dirt_image = pygame.transform.scale(pygame.image.load('Assets/grass.png'), (TILE_SIZE, TILE_SIZE))
# this should be dirt.png but i'm temporarily just gonna use grass for all

plant_image = pygame.transform.scale(pygame.image.load('Assets/GraveRobber.png'), (TILE_SIZE, TILE_SIZE))

tile_index = {1: grass_image,
              2: dirt_image,
              3: plant_image}

background_objects = [[0.25, [120, 10, 70, 400]],
                      [0.25, [280, 30, 40, 400]],
                      [0.5, [30, 40, 40, 400]],
                      [0.5, [130, 90, 100, 400]],
                      [0.5, [300, 80, 120, 400]]]

# def load_map(path):
#     f = open(path + '.txt', 'r')
#     data = f.read()
#     f.close()
#     data = data.split('\n')
#     game_map = []
#     for row in data:
#         game_map.append(list(row))
#     return game_map

# game_map = load_map('map')  # creates map from a list which is not that good, a dictionary is better

CHUNK_SIZE = 8


def generate_chunk(x, y):
    # whole world -> chunk -> tile
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0  # nothing
            if target_y > 10:
                tile_type = 2  # dirt
            elif target_y == 10:
                tile_type = 1  # grass
            elif target_y == 9:
                if random.randint(1, 5) == 1:
                    tile_type = 3  # plant
            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])
    return chunk_data


game_map = {}

# only add chunks when they would appear on screen

global animation_frames
animation_frames = {}


def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.jpg'
        # print(img_loc)
        animation_image = pygame.transform.scale(pygame.image.load(img_loc).convert(), (30, 30))
        animation_image.set_colorkey((0, 0, 0))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


animation_database = {}

animation_database['run'] = load_animation('Assets/player_animation/run', [7, 7, 7, 7, 7, 7])
animation_database['idle'] = load_animation('Assets/player_animation/idle', [7, 7, 14, 7])

# Action variables
player_action = 'idle'
player_frame = 0
player_flip = False

# Sounds
jump_sound = pygame.mixer.Sound('Assets/sound/platformer_jump.mp3')
grass_sounds = [pygame.mixer.Sound('Assets/sound/platformer_jump.mp3'),
                pygame.mixer.Sound('Assets/sound/platformer_jump.mp3')]
grass_sounds[0].set_volume(0.4)
grass_sounds[1].set_volume(0.4)
# make sounds for the grass

pygame.mixer.music.load('Assets/sound/platformer_soundtrack.mp3')
pygame.mixer.music.play(-1)

# Grass sound stuff
grass_sound_timer = 0


def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True

    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


moving_right = False
moving_left = False

player_y_momentum = 0
air_timer = 0

true_scroll = [0, 0]

player_rect = pygame.Rect(50, 50, 30, 30)
test_rect = pygame.Rect(100, 100, 100, 50)

camera_offset_x = 120
camera_offset_y = 70

# MAIN LOOP
while True:
    display.fill((146, 244, 255))

    if grass_sound_timer > 0:
        grass_sound_timer -= 1

    if moving_left:
        camera_offset_x = 140

    true_scroll[0] += (player_rect.x - true_scroll[0] - camera_offset_x) / 10
    true_scroll[1] += (player_rect.y - true_scroll[1] - camera_offset_y) / 10
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                               background_object[1][1] - scroll[1] * background_object[0],
                               background_object[1][2], background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), obj_rect)
        else:
            pygame.draw.rect(display, (9, 91, 85), obj_rect)

    tile_rects = []

    # Tile rendering
    for y in range(4):
        for x in range(4):
            target_x = x - 1 + int(round(scroll[0] / (CHUNK_SIZE * TILE_SIZE)))
            target_y = y - 1 + int(round(scroll[1] / (CHUNK_SIZE * TILE_SIZE)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = generate_chunk(target_x, target_y)
            for tile in game_map[target_chunk]:
                display.blit(tile_index[tile[1]],
                             (tile[0][0] * TILE_SIZE - scroll[0], tile[0][1] * TILE_SIZE - scroll[1]))
                if tile[1] in [1, 2]:
                    tile_rects.append(pygame.Rect(tile[0][0] * TILE_SIZE,
                                                  tile[0][1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # y = 0
    # for row in game_map:
    #     x = 0
    #     for tile in row:
    #         if tile == '1':
    #             display.blit(dirt_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
    #         if tile == '2':
    #             display.blit(grass_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
    #         if tile != '0':
    #             tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    #         x += 1
    #     y += 1
    # This is code that used the list map

    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    if player_movement[0] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = False
    if player_movement[0] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')
    if player_movement[0] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = True

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 120
                random.choice(grass_sounds).play()
    else:
        air_timer += 1
    if collisions['top']:
        player_y_momentum = 0

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_image = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_image, player_flip, False),
                 (player_rect.x - scroll[0], player_rect.y - scroll[1]))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_w:
                pygame.mixer.music.fadeout(1000)
            if event.key == K_e:
                pygame.mixer.music.play(-1)
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    jump_sound.play()
                    player_y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    fps = str(int(clock.get_fps()))
    fps_label = main_font.render(fps, True, (255, 255, 255))
    display.blit(fps_label, (WINDOW_SIZE[0] / 4 - fps_label.get_width() / 2, 50))

    dummy_surface = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(dummy_surface, (0, 0))

    pygame.display.update()
    clock.tick(FPS)
