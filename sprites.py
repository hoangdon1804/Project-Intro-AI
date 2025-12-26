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
        self.dx = float(data[2]) 
        self.dy = float(data[3])
        self.speed_rot = 1.0 # Riêng cho level 10

    def update(self, angle):
        if self.lvl in [0, 1, 6]: # Linear đơn giản
            self.x += self.dx
            self.y += self.dy
            if self.lvl == 0:
                if self.x <= 325 or self.x >= 775: self.dx *= -1
            elif self.lvl == 1:
                if self.y <= 226 or self.y >= 474: self.dy *= -1
            elif self.lvl == 6:
                if self.y <= 170 or self.y >= 530: self.dy *= -1

        elif self.lvl == 7: # Path movement (Chạy quanh ô vuông)
            self.x += self.dx
            self.y += self.dy
            cx, cy = round(self.x), round(self.y)
            if cx in [426, 574, 576] and cy in [124, 174, 274, 424]: self.dx, self.dy = 0, 4
            elif cx == 426 and cy in [276, 426, 576]: self.dx, self.dy = -4, 0
            elif cx == 574 and cy in [276, 426, 576]: self.dx, self.dy = 4, 0
            elif cx in [274, 424, 726] and cy in [276, 426, 526, 576]: self.dx, self.dy = 0, -4
            elif cx == 274 and cy in [124, 274, 424]: self.dx, self.dy = 4, 0
            elif cx == 726 and cy in [124, 274, 424]: self.dx, self.dy = -4, 0

        elif self.lvl == 8: # Logic đổi hướng tại các biên
            if self.dx != 0 or self.dy != 0:
                self.x += self.dx
                self.y += self.dy
                cx, cy = round(self.x), round(self.y)
                if cx in [175, 375, 575, 775, 975] and cy in [125, 225, 425, 525]: self.dx, self.dy = 0, 5
                elif cx in [175, 375, 575, 775, 975] and cy in [175, 275, 475, 575]: self.dx, self.dy = -5, 0
                elif cx in [125, 325, 525, 725, 925] and cy in [175, 275, 475, 575]: self.dx, self.dy = 0, -5
                elif cx in [125, 325, 525, 725, 925] and cy in [125, 225, 425, 525]: self.dx, self.dy = 5, 0

        elif self.lvl == 9: # Linear va chạm biên
            self.x += self.dx
            self.y += self.dy
            if self.dx != 0:
                if self.x <= 314 or self.x >= 736: self.dx *= -1
            if self.dy != 0:
                if self.y <= 514 or self.y >= 586: self.dy *= -1

        elif self.lvl == 10: # Orbital tăng tốc
            self.speed_rot = min(self.speed_rot + 0.0001, 0.05) # Giả lập tăng tốc độ xoay
            # Sử dụng góc tích lũy riêng để không bị giật
            new_angle = angle * self.speed_rot * 40 
            self.x = self.start_x + self.radius * math.cos(new_angle + self.angle_offset)
            self.y = self.start_y + self.radius * math.sin(new_angle + self.angle_offset)
            
        else: # Orbital mặc định (3, 4, 5)
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