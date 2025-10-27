import pygame
import time
import sys
import random
import math

pygame.init()

# size of the square tiles that make up the map
tile_size = 40
screen_width = tile_size * 20
screen_height = tile_size * 15

# true if the game is running
run = True

# File path for data files
map_path = r"D:\Game-Bot\map.txt"
moves_path = r"D:\Game-Bot\moves.txt"

# Game settings
FPS = 60
zoom = 5
Title = "mmmmmmmmmm"

# --- Các trọng số và phần thưởng cho hàm tính điểm mới ---
# Trọng số phạt cho mỗi frame ở trong vùng an toàn (g, s, h)
SAFE_ZONE_PENALTY_WEIGHT = 5.0
# Trọng số phạt cho mỗi bước di chuyển
MOVE_PENALTY_WEIGHT = 0.00
# Điểm phạt khi va chạm kẻ thù
ENEMY_HIT_PENALTY = 0.0
# Điểm phạt khi đi luẩn quẩn đến chết (nặng hơn va chạm enemy)
WANDER_DEATH_PENALTY = 400.0
# Điểm thưởng cực lớn khi chiến thắng
WIN_REWARD = 10000.0
# ---------------------------------------------------------

# Colors
red = (255, 0, 0)
black = (0, 0, 0)
lavender = (224, 218, 254)
ghostwhite = (248, 247, 255)
lightsteelblue = (170, 165, 255)
maroon = (127, 0, 0)
palegreen = (158, 242, 155)
blue = (0, 0, 255)
midnightblue = (0, 0, 68)
lime = (53, 247, 0)