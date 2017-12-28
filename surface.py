import numpy as np
from pygame import mouse, locals, camera
import pygame, math
import sys


black = (0, 0, 0)
white = (255, 255, 255)
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
myfont = pygame.font.SysFont('Arial', 30)
x, y = (0, 0)
coordinates = f'x: {x}, y: {y}'

pygame.init()

width = 1000
height = 800
display = pygame.display.set_mode((width, height))
pygame.display.set_caption("2 DOF Robot Arm")
fpsClock = pygame.time.Clock()

def update_frame():
    display.fill(white)
    textsurface = myfont.render(coordinates, False, (0, 0, 0))
    display.blit(textsurface,(x, y))
    pygame.display.update()
    fpsClock.tick(30)


while 1:
    update_frame()
    for event in pygame.event.get():
        if event.type == locals.QUIT:
            print('ALL YOUR BASE ARE BELONG TO US.')
            pygame.quit()
            sys.exit()
        if event.type == locals.MOUSEBUTTONUP:
                x, y = mouse.get_pos()
                coordinates = f'x: {x}, y: {y}'
