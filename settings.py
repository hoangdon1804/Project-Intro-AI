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
map_path = r"D:\Project-Intro-AI\map.txt"
moves_path = r"D:\Project-Intro-AI\moves.txt"
archive_path = r"D:\Project-Intro-AI\archive.txt"

# Cài đặt game
FPS = 60
Title = "AI Game Bot"

# CHỌN CHẾ ĐỘ HIỂN THỊ QUÁ TRÌNH HUẤN LUYỆN
# 0: Không hiển thị gì (nhanh nhất)
# 1: Hiển thị cá thể tốt nhất sau mỗi thế hệ
# 3: Hiển thị song song tất cả cá thể (rất chậm, chỉ để debug)
VISUALIZATION_MODE = 3

# --- Cài đặt cho thuật toán tiến hóa ---
TOURNAMENT_SIZE = 3
NORMAL_MUTATION_CHANCE = 0.035
END_STEP_MUTATION_CHANCE = 0.90
DECADE_RESET_MUTATION_CHANCE = 0.50

# ================================================================= #
# === THAM SỐ MỚI === #
# ================================================================= #
# Tỷ lệ phần trăm chuỗi di chuyển của cá thể tốt nhất sẽ được giữ lại NGUYÊN VẸN
# trong sự kiện Decade Reset. Ví dụ: 0.7 nghĩa là giữ lại 70% đầu. (Giá trị từ 0.0 đến 1.0)
DECADE_RESET_KEEP_PERCENTAGE = 0.95 
# ================================================================= #

# --- Cài đặt cho hàm tính điểm (Fitness Function) ---
CHECKPOINT_REWARD = 150000.0
DISTANCE_REWARD_BASE = 100000.0

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
yellow = (255, 255, 0) # Màu cho checkpoint