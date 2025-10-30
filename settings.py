import pygame
import time
import sys
import random
import math

pygame.init()

# Kích thước của các ô vuông tạo nên bản đồ
tile_size = 40
screen_width = tile_size * 20
screen_height = tile_size * 15

# Đường dẫn file
map_path = r"D:\Game-Bot\map.txt"
moves_path = r"D:\Game-Bot\moves.txt"
archive_path = r"D:\Game-Bot\archive.txt"

# Cài đặt game
FPS = 60
Title = "AI Game Bot"

# CHỌN CHẾ ĐỘ HIỂN THỊ QUÁ TRÌNH HUẤN LUYỆN
VISUALIZATION_MODE = 3

# --- Cài đặt cho thuật toán tiến hóa ---
NUM_ELITES_TO_USE = 10

# Xác suất một bước đi bị thay đổi so với cha mẹ, cho mỗi nhóm
LIGHT_MUTATION_CHANCE = 0.03  
MEDIUM_MUTATION_CHANCE = 0.3 
HEAVY_MUTATION_CHANCE = 0.7  

# --- Cài đặt cho hàm tính điểm (Fitness Function) ---
SAFE_ZONE_PENALTY_WEIGHT = 2.0
MOVE_PENALTY_WEIGHT = 0.5
ENEMY_HIT_PENALTY = 0.0
WANDER_DEATH_PENALTY = 400.0
WIN_REWARD = 10000.0

# --- Màu sắc ---
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