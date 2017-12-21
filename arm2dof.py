import numpy as np
from pygame import mouse, locals, camera
import pygame, math
import sys

from armsegment import ArmSegment

black = (0, 0, 0)
white = (255, 255, 255)
arm_color = (50, 50, 50, 200)  # fourth value specifies transparency

pygame.init()

width = 800
height = 800
display = pygame.display.set_mode((width, height))
pygame.display.set_caption("2 DOF Robot Arm")
fpsClock = pygame.time.Clock()

l1 = ArmSegment(300.)
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

def fix(arg):
    if arg > 1:
        return 1
    if arg < -1:
        return -1
    return arg

def get_angles(point):
    A, Z = point
    angle_d = np.arctan2(Z, A)
    print(np.degrees(angle_d))
    top = (l1.length**2 + A**2 + Z**2 - l2.length**2)
    bottom = 2*l1.length * math.sqrt(A**2 + Z**2)
    first_arm = top/bottom
    first_arm = fix(first_arm)
    second_arm = (l1.length**2 + l2.length**2 - A**2 - Z**2)/(2 * l1.length * l2.length)
    second_arm = fix(second_arm)
    angle_1, angle_2 = np.arccos([first_arm, second_arm])
    print(np.degrees(angle_1))
    print(np.degrees(angle_2))
    angle_1 = angle_1 + angle_d
    angle_2 = (angle_2 + angle_1) - math.pi
    print(np.degrees(angle_1))
    print(np.degrees(angle_2))
    return angle_1, angle_2


def update_frame():
    display.fill(white)

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

    l1.rotation = 0
    l2.rotation = 0
    print('Robot ready for mission.')

    reset = False
    while not reset:
        update_frame()
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                print('ALL YOUR BASE ARE BELONG TO US.')
                pygame.quit()
                sys.exit()
            if event.type == locals.KEYDOWN:
                if pygame.key.get_pressed()[32]: # if spacebar is pressed
                    print('Resetting Arm.')
                    reset = True
                    break
            if event.type == locals.MOUSEBUTTONUP:
                target = normalize_points(mouse.get_pos())
                print(target)
                angle_l1, angle_l2 = get_angles(target)

                print('')
                print('CHANGE >>\nAngle 1: {: f}\nAngle 2: {: f}\n'.format(np.degrees(angle_l1), np.degrees(angle_l2)))

                l1_arm, l1_rect = l1.rotate(angle_l1)
                l2_arm, l2_rect = l2.rotate(angle_l2)

                print('CURRENT >>\nAngle 1: {: f}\nAngle 2: {: f}\n'.format(np.degrees(l1.rotation), np.degrees(l2.rotation)))

                # rotate_l1, rotate_l2 = True, True
                # while rotate_l1 or rotate_l2:  # l1.rotation < angle_l1 and l2.rotation < angle_l2:
                #
                #     # rotate our joints
                #     if math.fabs(l1.rotation) <= math.fabs(angle_l1):
                #         l1_arm, l1_rect = l1.rotate(.01)
                #     # if angle_l1 > 0:
                #     #         l1.rotate(angle_l1)  # (.03*1)
                #     #     else:
                #     #         l1.rotate(angle_l1)
                #     else:
                #         rotate_l1 = False
                #
                #     if math.fabs(l2.rotation) <= math.fabs(angle_l2) + math.fabs(angle_l1):
                #         l2_arm, l2_rect = l2.rotate(.01 * -2)
                #         # if angle_l2 > 0:
                #         #     l2.rotate(angle_l1 + angle_l2)
                #         # else:
                #         #     l2.rotate(angle_l1 + angle_l2)
                #     else:
                #         rotate_l2 = False
                #    update_frame()

                update_frame()
                pygame.event.clear()
