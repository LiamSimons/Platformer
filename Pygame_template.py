import pygame
import sys

from pygame.locals import *

main_clock = pygame.time.Clock()

pygame.init()

pygame.display.set_caption('Physics explanation')

screen = pygame.display.set_mode((500, 500), 0, 32)

while True:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    main_clock.tick(60)
