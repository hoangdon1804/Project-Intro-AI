import pygame
from settings import *

class Zone(pygame.sprite.Sprite):
    def __init__(self, game, x, y, size, color, type):
        self.groups = game.all_sprites, game.zones
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y, self.type = x, y, type