import pygame
from settings import *

class Border(pygame.sprite.Sprite):
    def __init__(self, game, x, y, length, width, color, align):
        self.groups = game.all_sprites, game.borders
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((length, length), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.align = align
        self.x, self.y, self.width, self.color = x, y, width, color

    def draw(self):
        if self.align == 0:
            pygame.draw.line(self.game.screen, self.color, [self.x - tile_size/2, self.y], [self.x + tile_size/2, self.y], self.width)
        else:
            pygame.draw.line(self.game.screen, self.color, [self.x, self.y - tile_size/2], [self.x, self.y + tile_size/2], self.width)
