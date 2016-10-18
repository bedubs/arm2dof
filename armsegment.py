import numpy as np
import pygame


class ArmSegment:
    """
    A class for storing relevant arm segment information.
    """
    def __init__(self, length, scale=1.0):
        self.length = length
        self.scale = self.length * scale
        self.offset = self.scale / 2.0
        self.arm = pygame.Surface((self.length, 5), pygame.SRCALPHA, 32)
        # self.rect = self.arm.get_rect()

        self.rotation = 0.0  # in radians

    def rotate(self, rotation):
        """
        Rotates and re-centers the arm segment.
        """
        self.rotation += rotation
        # rotate arms by degree
        arm = pygame.transform.rotozoom(self.arm, np.degrees(self.rotation), 1)
        # # reset the center
        rect = arm.get_rect()
        rect.center = (0, 0)
        return arm, rect


    def move_to_point(self, point):
        pass
