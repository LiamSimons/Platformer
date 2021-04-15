import pygame
import sys

from pygame.locals import *

main_clock = pygame.time.Clock()

pygame.init()

pygame.display.set_caption('Physics explanation')

screen = pygame.display.set_mode((500, 500), 0, 32)

player = pygame.Rect(100, 100, 40, 80)

tiles = [pygame.Rect(200, 350, 50, 50), pygame.Rect(260, 320, 50, 50)]


def collision_test(rect, tiles):
    collisions = []
    for tile in tiles:
        if rect.colliderect(tile):
            collisions.append(tile)
    return collisions


def move(rect, movement, tiles):  # movement = [5, 2]
    # Horizontal movement
    rect.x += movement[0]  # adding the first value of the movement
    collisions = collision_test(rect, tiles)
    for tile in collisions:
        if movement[0] > 0:
            rect.right = tile.left  # properties of rect class
        if movement[0] < 0:
            rect.left = tile.right

    # Vertical movement
    rect.y += movement[1]  # adding the first value of the movement
    collisions = collision_test(rect, tiles)
    for tile in collisions:
        if movement[1] > 0:
            rect.bottom = tile.top  # properties of rect class
        if movement[1] < 0:
            rect.top = tile.bottom

    return rect


right = False
left = False
up = False
down = False


while True:
    screen.fill((0, 0, 0))

    movement = [0, 0]
    if right:
        movement[0] += 5
    if left:
        movement[0] -= 5
    if up:
        movement[1] -= 5
    if down:
        movement[1] += 5

    player = move(player, movement, tiles)

    pygame.draw.rect(screen, (255, 255, 255), player)

    for tile in tiles:
        pygame.draw.rect(screen, (255, 0, 0), tile)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                right = True
            if event.key == K_LEFT:
                left = True
            if event.key == K_DOWN:
                down = True
            if event.key == K_UP:
                up = True
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                right = False
            if event.key == K_LEFT:
                left = False
            if event.key == K_DOWN:
                down = False
            if event.key == K_UP:
                up = False

    pygame.display.update()
    main_clock.tick(60)
