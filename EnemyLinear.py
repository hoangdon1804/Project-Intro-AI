import pygame
import math
from settings import *

FIXED_POINT_SCALE = 1000

class EnemyLinear(pygame.sprite.Sprite):
    def __init__(self, game, size, speed, x, y, criticals, fill, border):
        self.groups = game.all_sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, border, [int(size/2), int(size/2)], int(size/2))
        pygame.draw.circle(self.image, fill, [int(size/2), int(size/2)], int(size/2) - 4)
        self.rect = self.image.get_rect()
        self.size = size
        self.speed_fixed = int(speed * FIXED_POINT_SCALE)
        self.x_fixed = int(x * FIXED_POINT_SCALE)
        self.y_fixed = int(y * FIXED_POINT_SCALE)
        self.criticals_fixed = [[int(p[0] * FIXED_POINT_SCALE), int(p[1] * FIXED_POINT_SCALE)] for p in criticals]
        self.reset()

    def move(self):
        dx = self.nextx_fixed - self.x_fixed
        dy = self.nexty_fixed - self.y_fixed
        dist_sq = dx*dx + dy*dy
        if dist_sq <= self.speed_fixed * self.speed_fixed:
            self.x_fixed = self.nextx_fixed
            self.y_fixed = self.nexty_fixed
            self.step = (self.step + 1) % len(self.criticals_fixed)
            self.nextx_fixed = self.criticals_fixed[self.step][0]
            self.nexty_fixed = self.criticals_fixed[self.step][1]
        else:
            dist = int(math.sqrt(dist_sq))
            if dist == 0: return
            self.x_fixed += (dx * self.speed_fixed) // dist
            self.y_fixed += (dy * self.speed_fixed) // dist

    def update(self):
        self.move()
        self.rect.x = (self.x_fixed // FIXED_POINT_SCALE) - self.size // 2
        self.rect.y = (self.y_fixed // FIXED_POINT_SCALE) - self.size // 2

    def reset(self):
        self.x_fixed = self.criticals_fixed[0][0]
        self.y_fixed = self.criticals_fixed[0][1]
        self.rect.x = (self.x_fixed // FIXED_POINT_SCALE) - self.size // 2
        self.rect.y = (self.y_fixed // FIXED_POINT_SCALE) - self.size // 2
        self.step = 0
        self.nextx_fixed = self.criticals_fixed[self.step][0]
        self.nexty_fixed = self.criticals_fixed[self.step][1]