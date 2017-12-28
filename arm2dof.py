import numpy as np
from pygame import mouse, locals, camera
import pygame, math
import sys

from armsegment import ArmSegment

black = (0, 0, 0)
white = (255, 255, 255)
arm_color = (50, 50, 50, 200)  # fourth value specifies transparency

# pygame.font.init()
coordinates = (0, 0)
angle_l1, angle_l2 = (0, 0)

pygame.init()

info = pygame.font.SysFont('Arial', 24)
width = 800
height = 800
display = pygame.display.set_mode((width, height))
pygame.display.set_caption("2 DOF Robot Arm")
fpsClock = pygame.time.Clock()

l2 = ArmSegment(200.)
l1 = ArmSegment(200.)

l1.arm.fill(arm_color)
l2.arm.fill(arm_color)

origin = (width / 2, height / 2)

follow_mode = False


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
    top = (l1.length**2 + A**2 + Z**2 - l2.length**2)
    bottom = 2*l1.length * math.sqrt(A**2 + Z**2)
    first_arm = top/bottom
    first_arm = fix(first_arm)
    second_arm = (l1.length**2 + l2.length**2 - A**2 - Z**2)/(2 * l1.length * l2.length)
    second_arm = fix(second_arm)
    angle_1, angle_2 = np.arccos([first_arm, second_arm])
    angle_1 = angle_1 + angle_d
    angle_2 = (angle_2 + angle_1) - math.pi
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
    print(joints)
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

    angle_1_text = info.render(f'{int(np.degrees(angle_l1))} degrees', False, (0, 0, 0))
    angle_2_text = info.render(f'{int(np.degrees(angle_l2))} degrees', False, (0, 0, 0))
    display.blit(angle_1_text, joints[0])
    display.blit(angle_2_text, joints[1])

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

        if follow_mode:
            ## This will make the arm follow the mouse always
            target = normalize_points(mouse.get_pos())
            angle_l1, angle_l2 = get_angles(target)
            l1_arm, l1_rect = l1.rotate(angle_l1)
            l2_arm, l2_rect = l2.rotate(angle_l2)

        for event in pygame.event.get():
            if event.type == locals.QUIT:
                print('ALL YOUR BASE ARE BELONG TO US.')
                pygame.quit()
                sys.exit()
            if event.type == locals.KEYDOWN:
                if pygame.key.get_pressed()[32]: # if spacebar is pressed
                    print('Resetting Arm.')
                    reset = True
                    angle_l1, angle_l2 = (0, 0)
                    follow_mode = False
                    break
            if event.type == locals.MOUSEBUTTONDOWN:
                if mouse.get_pressed()[2]:
                    if follow_mode:
                        follow_mode = False
                    else:
                        follow_mode = True
            if event.type == locals.MOUSEBUTTONUP:
                coordinates = mouse.get_pos()
                target = normalize_points(coordinates)
                print(target)
                angle_l1, angle_l2 = get_angles(target)
                angle_info = f'Angle 1: {np.degrees(angle_l1)}\nAngle 2: {np.degrees(angle_l2)}'

                print('')
                print('CHANGE >>\nAngle 1: {: f}\nAngle 2: {: f}\n'.format(np.degrees(angle_l1), np.degrees(angle_l2)))

                l1_arm, l1_rect = l1.rotate(angle_l1)
                l2_arm, l2_rect = l2.rotate(angle_l2)

                print('CURRENT >>\nAngle 1: {: f}\nAngle 2: {: f}\n'.format(np.degrees(l1.rotation), np.degrees(l2.rotation)))

                update_frame()
                pygame.event.clear()
