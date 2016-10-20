import numpy as np
from pygame import mouse, locals, camera, surface
import pygame, math
import sys

from armsegment import ArmSegment

black = (0, 0, 0)
white = (255, 255, 255)
arm_color = (50, 50, 50, 200)  # fourth value specifies transparency

pygame.init()

camera.init()

width = 640
height = 480
size = (width, height)
cam = camera.Camera('/dev/video0', (width, height))
cam.start()
display = pygame.display.set_mode((width, height))

fpsClock = pygame.time.Clock()

l1 = ArmSegment(150.)
l2 = ArmSegment(300.)

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
    return angle1, angle2 - angle1


def get_angles1(point):
    a, b = l2.length, l1.length
    xf, yf = point
    xy2 = xf**2 + yf**2
    angle_d = np.arctan2(-yf/math.sqrt(xy2), xf/math.sqrt(xy2))
    c = math.sqrt(xy2)
    # angle_a = np.arccos((b**2 + c**2 - a**2) / (2*b*c))
    th = np.arccos(-1 * (xy2 + b**2 - a**2) / math.sqrt(((-2 * b * xf)**2) + ((-2 * b * yf)**2)))
    angle_a = angle_d - th
    angle1 = angle_d + th  # angle_a
    angle2 = np.arcsin((np.sin(angle_a) * c)/a)
    return angle1, angle2


def get_angles2(point):
    a, b = l2.length, l1.length
    x, y = point
    xy2 = x**2 + y**2

    angle_d = np.arctan2(-y / math.sqrt(xy2), x / math.sqrt(xy2))
    th2 = np.arctan2(
            math.sqrt(1-((xy2 - b**2 - a**2)/(2 * b * a))**2),
            (xy2 - b**2 - a**2)/(2 * b * a))
    th1 = np.arctan2(y, x) - angle_d
    return th1, th2


def get_angles3(point):
    a = l2.length
    b = l1.length
    angle_d = np.arctan2(point[1], point[0])
    c = math.sqrt(point[0]**2 + point[1]**2)
    angle_a = np.arccos((b**2 + c**2 - a**2) / (2*b*c))
    angle1 = angle_d - angle_a
    angle2 = np.arcsin((np.sin(angle_a) * c)/a)
    return angle1, angle2


def update_frame():
    # display.fill(white)
    # cam.get_image(display)

    thresholded = pygame.surface.Surface(size, 0, display)
    snapshot = cam.get_image(display)
    pygame.transform.threshold(thresholded, cam.get_image(display), (0, 255, 0), (90, 170, 170), (0, 0, 0), 2)

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
            angle_l1, angle_l2 = get_angles(target)

            l1_arm, l1_rect = l1.rotate(angle_l1)
            l2_arm, l2_rect = l2.rotate(angle_l2)

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
