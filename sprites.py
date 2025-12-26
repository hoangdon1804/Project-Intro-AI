import pygame
import math
from settings import *

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        
    def move(self, dx, dy, wall_mask):
        # Trục X
        self.rect.x += dx
        if wall_mask.overlap(pygame.mask.Mask((PLAYER_SIZE, PLAYER_SIZE), fill=True), (self.rect.x, self.rect.y)):
            self.rect.x -= dx
        # Trục Y
        self.rect.y += dy
        if wall_mask.overlap(pygame.mask.Mask((PLAYER_SIZE, PLAYER_SIZE), fill=True), (self.rect.x, self.rect.y)):
            self.rect.y -= dy

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

class Enemy:
    def __init__(self, data, lvl):
        self.lvl = lvl
        self.x = float(data[0])
        self.y = float(data[1])
        self.start_x, self.start_y = self.x, self.y
        self.radius = data[2]
        self.angle_offset = data[3]
        self.dx = data[2] # Cho linear movement
        self.dy = data[3] # Cho linear movement

    def update(self, angle):
        if self.lvl in [0, 1]: # Linear
            if self.lvl == 0:
                self.x += self.dx
                if self.x <= 325 or self.x >= 775: self.dx *= -1
            else:
                self.y += self.dy
                if self.y <= 226 or self.y >= 474: self.dy *= -1
        elif self.lvl == 2: # Box
            self.x += self.dx
            self.y += self.dy
            cx, cy = round(self.x), round(self.y)
            if cx == 475 and cy == 275: self.dx, self.dy = 1.5, 0
            elif cx == 625 and cy == 275: self.dx, self.dy = 0, 1.5
            elif cx == 625 and cy == 425: self.dx, self.dy = -1.5, 0
            elif cx == 475 and cy == 425: self.dx, self.dy = 0, -1.5
        else: # Orbital (3, 4, 5)
            self.x = self.start_x + self.radius * math.cos(angle + self.angle_offset)
            self.y = self.start_y + self.radius * math.sin(angle + self.angle_offset)

    def draw(self, surface):
        pygame.draw.circle(surface, BLUE_ENEMY, (int(self.x), int(self.y)), ENEMY_RADIUS)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), ENEMY_RADIUS, 2)

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x-15, y-15, 30, 30)
        self.pos = (x, y)
    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW_COIN, self.pos, 10)
        pygame.draw.circle(surface, BLACK, self.pos, 10, 2)