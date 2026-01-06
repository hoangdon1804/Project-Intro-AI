import pygame
import json
import sys
import os
import math
from settings import *
from sprites import Player, Enemy
from level_manager import LevelManager

class ReplayVisualizer:
    def __init__(self, level_to_replay):
        pygame.init()
        self.level = level_to_replay
        self.config = LevelManager.get_config(self.level)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Replay Level {self.level} - AI Performance")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.num_font = pygame.font.SysFont("Arial", 14, bold=True)

        # 1. Tải dữ liệu từ archivement.txt
        self.record_data = self.load_record()
        if not self.record_data:
            print(f"Error: Không tìm thấy dữ liệu cho Level {self.level}")
            pygame.quit()
            sys.exit()

        # Lấy thông tin trực tiếp từ file archivement.txt 
        self.best_dna = self.record_data["dna"]
        self.pop_size = self.record_data.get("population_size", 100) 
        self.dna_length = self.record_data.get("dna_length", len(self.best_dna))
        
        self.replay_limit = 5
        self.replay_count = 0

        # 2. Tạo Mask tường để xử lý va chạm pixel [cite: 38, 51]
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        if self.config["walls_pts"]:
            pygame.draw.polygon(surf, BLACK, self.config["walls_pts"], WALL_WIDTH)
        self.wall_mask = pygame.mask.from_surface(surf)

        # 3. Logic Coin (Giữ nguyên tương tự train.py để đồng bộ logic ăn coin) [cite: 102, 103, 112]
        self.custom_coins = []
        if self.level == 0:
            self.custom_coins = [{"pos": (325, 475), "type": "RED"}, {"pos": (775, 225), "type": "RED"}]
        elif self.level == 1:
            self.custom_coins = [{"pos": (550, 350), "type": "YELLOW"}, {"pos": (825, 350), "type": "RED"}]
        elif self.level == 2:
            self.custom_coins = [{"pos": (475, 225), "type": "YELLOW"}]
        elif self.level == 3:
            self.custom_coins = [
                {"pos": (550, 250), "type": "YELLOW"}, {"pos": (625, 325), "type": "RED"},
                {"pos": (700, 400), "type": "YELLOW"}, {"pos": (625, 475), "type": "RED"},
                {"pos": (550, 550), "type": "YELLOW"}, {"pos": (375, 425), "type": "RED"}
            ]

        self.setup_replay()

    def load_record(self):
        file_path = "archivement.txt"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(str(self.level))
            except Exception as e:
                print(f"Lỗi đọc file: {e}")
        return None

    def setup_replay(self):
        # Khởi tạo tất cả player tại vị trí bắt đầu của level [cite: 36, 109]
        self.players = [Player(*self.config["player_pos"]) for _ in range(self.pop_size)]
        self.enemies = [Enemy(e, self.level) for e in self.config["enemies"]]
        # Trạng thái riêng cho từng player trong quần thể
        self.player_states = [{"dead": False, "finished": False, "coins": 0} for _ in range(self.pop_size)]
        self.current_frame = 0
        self.angle = 0
        self.replay_count += 1

    def run(self):
        running = True
        while running and self.replay_count <= self.replay_limit:
            self.screen.fill(BG_L_BLUE)
            
            # Vẽ Map & Grid [cite: 45, 111]
            pygame.draw.rect(self.screen, GREEN_FINISH, self.config["finish_rect"])
            for cell in self.config["grid_cells"]:
                pygame.draw.rect(self.screen, WHITE, (cell[0], cell[1], 50, 50))
            if self.config["walls_pts"]:
                pygame.draw.polygon(self.screen, BLACK, self.config["walls_pts"], WALL_WIDTH)

            coins_collected = self.player_states[0]["coins"]

            for i, c_data in enumerate(self.custom_coins):
                # CHỈ vẽ những coin có chỉ số (index) lớn hơn hoặc bằng số coin đã ăn
                if i >= coins_collected:
                    color = RED if c_data["type"] == "RED" else YELLOW_COIN
                    pygame.draw.circle(self.screen, color, c_data["pos"], 10)
                    pygame.draw.circle(self.screen, BLACK, c_data["pos"], 10, 2)
                    lbl = self.num_font.render(str(i+1), True, BLACK)
                    self.screen.blit(lbl, (c_data["pos"][0]-5, c_data["pos"][1]-25))
                        # Cập nhật Enemy [cite: 39, 113]
            self.angle += 0.025
            for en in self.enemies: en.update(self.angle)

            # Cập nhật tất cả Players dùng chung bộ DNA tốt nhất [cite: 58]
            active_any = False
            for i in range(self.pop_size):
                state = self.player_states[i]
                player = self.players[i]

                if not state["dead"] and not state["finished"]:
                    active_any = True
                    if self.current_frame < len(self.best_dna):
                        dx, dy = self.best_dna[self.current_frame]
                        player.move(dx, dy, self.wall_mask)
                        
                        player_center = pygame.Vector2(player.rect.center)

                        # Check va chạm kẻ địch [cite: 40, 116]
                        for en in self.enemies:
                            enemy_pos = pygame.Vector2(en.x, en.y)
                            if player_center.distance_to(enemy_pos) < (ENEMY_RADIUS + PLAYER_SIZE / 2):
                                state["dead"] = True
                        
                        # Check ăn Coin tuần tự [cite: 42, 117]
                        if state["coins"] < len(self.custom_coins):
                            c_pos = pygame.Vector2(self.custom_coins[state["coins"]]["pos"])
                            if player_center.distance_to(c_pos) < (10 + PLAYER_SIZE / 2):
                                state["coins"] += 1
                        
                        # Check về đích (Chỉ tính khi ăn đủ coin) [cite: 43, 118]
                        if state["coins"] == len(self.custom_coins):
                            if player.rect.colliderect(self.config["finish_rect"]):
                                state["finished"] = True

                # Vẽ Player (Màu xanh dương để phân biệt với lúc train) [cite: 60]
                p_color = (0, 150, 255) if not state["dead"] else (100, 100, 100)
                pygame.draw.rect(self.screen, p_color, player.rect)
                pygame.draw.rect(self.screen, BLACK, player.rect, 1)

            for en in self.enemies: en.draw(self.screen)

            # UI hiển thị thông tin [cite: 61, 122]
            ui_texts = [
                f"REPLAY: {self.replay_count}/{self.replay_limit}",
                f"FRAME: {self.current_frame}/{self.dna_length}",
                f"FITNESS: {self.record_data['fitness']:.2f}",
                f"POPULATION: {self.pop_size}",
                f"WON AT GEN: {self.record_data['generation']}"
            ]
            for idx, text in enumerate(ui_texts):
                self.screen.blit(self.font.render(text, True, BLACK), (20, 10 + idx * 25))

            self.current_frame += 1
            
            # Kiểm tra kết thúc lượt replay hoặc hết DNA
            if not active_any or self.current_frame >= self.dna_length:
                if self.replay_count < self.replay_limit:
                    pygame.time.delay(1000) # Nghỉ 1 giây trước khi chạy lại [cite: 63]
                    self.setup_replay()
                else:
                    print(f"Đã hoàn thành {self.replay_limit} lần replay.")
                    running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()
            self.clock.tick(FPS) 

        pygame.quit()

if __name__ == "__main__":
    # Thay đổi level muốn xem lại tại đây
    replay = ReplayVisualizer(level_to_replay=1)
    replay.run()