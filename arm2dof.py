import numpy as np
from pygame import mouse, locals, camera
import pygame, math
import sys

from armsegment import ArmSegment

black = (0, 0, 0)
white = (255, 255, 255)
arm_color = (250, 250, 250, 200)  # fourth value specifies transparency

pygame.init()

camera.init()

width = 640
height = 480
cam = camera.Camera('/dev/video0', (width, height))
cam.start()
display = pygame.display.set_mode((width, height))
fpsClock = pygame.time.Clock()

l1 = ArmSegment(150.)
l2 = ArmSegment(150.)

l1.arm.fill(arm_color)
l2.arm.fill(arm_color)

origin = (width / 2, height / 2)


def transform(rect, base, arm_segment):
    rect.center += np.asarray(base)
    rect.center += np.array([np.cos(arm_segment.rotation) * arm_segment.offset,
                             -np.sin(arm_segment.rotation) * arm_segment.offset])


def transform_lines(rect, base, arm_segment):
    transform(rect, base, arm_segment)
    rect.center += np.array([-rect.width / 2.0, -rect.height / 2.0])


def normalize_points(point):
    return point[0] - 400, 400 - point[1]


def get_angles(point):
    a = l2.length
    b = l1.length
    angle_d = np.arctan2(point[1], point[0])
    c = math.sqrt(point[0]**2 + point[1]**2)
    angle_a = np.arccos((b**2 + c**2 - a**2) / (2*b*c))
    angle1 = angle_d - angle_a
    angle2 = np.arcsin((np.sin(angle_a) * c)/a)
    return angle1, angle2


def update_frame():
    cam.get_image(display)

    # generate (x,y) positions of each of the joints
    joints_x = np.cumsum([0,
                          l1.scale * np.cos(l1.rotation),
                          l2.scale * np.cos(l2.rotation)]) + origin[0]

    joints_y = np.cumsum([0,
                          l1.scale * np.sin(l1.rotation),
                          l2.scale * np.sin(l2.rotation)]) * -1 + origin[1]

    joints = [(int(x), int(y)) for x, y in zip(joints_x, joints_y)]

    # rotate arm lines
    line_l1 = pygame.transform.rotozoom(l1.arm,
                                        np.degrees(l1.rotation), 1)
    line_l2 = pygame.transform.rotozoom(l2.arm,
                                        np.degrees(l2.rotation), 1)

    # translate arm lines
    l1_rect = line_l1.get_rect()
    transform_lines(l1_rect, joints[0], l1)

    l2_rect = line_l2.get_rect()
    transform_lines(l2_rect, joints[1], l2)

    display.blit(line_l1, l1_rect)
    display.blit(line_l2, l2_rect)

    # draw circles at joints for pretty
    pygame.draw.circle(display, black, joints[0], 10)
    pygame.draw.circle(display, arm_color, joints[0], 7)
    pygame.draw.circle(display, black, joints[1], 9)
    pygame.draw.circle(display, arm_color, joints[1], 7)

    pygame.display.update()
    fpsClock.tick(30)


while 1:

    update_frame()

    for event in pygame.event.get():
        if event.type == locals.QUIT:
            cam.stop()
            pygame.quit()
            sys.exit()
        if event.type == locals.MOUSEBUTTONUP:
            target = normalize_points(mouse.get_pos())
            print target
            p1, p2 = get_angles(target)

            l1.rotate(p1)
            l2.rotate(p2+p1)
            update_frame()
            pygame.event.clear()
