import pygame
import random
import math
import sys
import os
from settings import *
from sprites import Player, Enemy
from level_manager import LevelManager

# --- Cấu hình Giải thuật Di truyền ---
POPULATION_SIZE = 1000
GENES_PER_STEP = 500  # Số bước khởi đầu
MUTATION_RATE = 0.05
ELITISM_COUNT = 4
DNA_INCREASE_RATE = 50  # Số gene tăng thêm mỗi 10 thế hệ

class Genome:
    def __init__(self, length):
        self.genes = []
        last_gene = None
        for _ in range(length):
            # 10% cơ hội đổi hướng hoặc là gene đầu tiên
            if last_gene is None or random.random() < 0.1:
                angle = random.uniform(0, 2 * math.pi)
                last_gene = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)
            
            self.genes.append(last_gene)
            
        self.fitness = 0
        self.is_dead = False
        self.reached_finish = False
        self.current_step = 0
        self.coins_collected = 0

class TrainVisualizer:
    def __init__(self, level):
        pygame.init()
        self.level = level
        self.config = LevelManager.get_config(level)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"AI Trainer Level {level} - Sequential Coins")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.num_font = pygame.font.SysFont("Arial", 14, bold=True)

        # 1. Tạo Mask tường
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        if self.config["walls_pts"]:
            pygame.draw.polygon(surf, BLACK, self.config["walls_pts"], WALL_WIDTH) 
        self.wall_mask = pygame.mask.from_surface(surf) 

        # 2. Định nghĩa vị trí Coin cho Level 0
        if level == 0:
            self.custom_coins = [
                {"pos": (325, 475), "type": "RED"},    
                {"pos": (775, 225), "type": "RED"},
                {"pos": (825, 225), "type": "RED"}  
            ]
        if level == 1:
            self.custom_coins = [
                {"pos": (550, 350), "type": "YELLOW"},
                {"pos": (825, 350), "type": "RED"}  
            ]
        self.target_pos = pygame.Vector2(self.config["finish_rect"].center)
        self.generation = 0
        self.setup_generation()

    def setup_generation(self):
        global GENES_PER_STEP
        if self.generation > 0 and self.generation % 10 == 0:
            GENES_PER_STEP += DNA_INCREASE_RATE
            print(f"--- Generation {self.generation}: DNA increased to {GENES_PER_STEP} steps ---")
            
            # Bổ sung gene còn thiếu cho quần thể hiện tại
            for genome in self.population:
                while len(genome.genes) < GENES_PER_STEP:
                    # Lấy hướng của gene cuối cùng làm gốc
                    last_gene = genome.genes[-1] if genome.genes else None
                    if last_gene is None or random.random() < 0.1:
                        angle = random.uniform(0, 2 * math.pi)
                        last_gene = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)
                    genome.genes.append(last_gene)

        if self.generation == 0:
            self.population = [Genome(GENES_PER_STEP) for _ in range(POPULATION_SIZE)]
        
        self.players = [Player(*self.config["player_pos"]) for _ in range(POPULATION_SIZE)]
        self.enemies = [Enemy(e, self.level) for e in self.config["enemies"]]
        self.current_frame = 0
        self.angle = 0
        self.generation += 1

    def run(self):
        running = True
        while running:
            self.screen.fill(BG_L_BLUE)
            
            # Vẽ Map
            pygame.draw.rect(self.screen, GREEN_FINISH, self.config["finish_rect"])
            for cell in self.config["grid_cells"]:
                pygame.draw.rect(self.screen, WHITE, (cell[0], cell[1], 50, 50))
            if self.config["walls_pts"]:
                pygame.draw.polygon(self.screen, BLACK, self.config["walls_pts"], WALL_WIDTH)

            # Vẽ các Coin tuần tự
            for i, c_data in enumerate(self.custom_coins):
                color = RED if c_data["type"] == "RED" else YELLOW_COIN
                pygame.draw.circle(self.screen, color, c_data["pos"], 10)
                pygame.draw.circle(self.screen, BLACK, c_data["pos"], 10, 2)
                lbl = self.num_font.render(str(i+1), True, BLACK)
                self.screen.blit(lbl, (c_data["pos"][0]-5, c_data["pos"][1]-25))

            active_players = False
            self.angle += 0.05
            for en in self.enemies: en.update(self.angle)

            for i in range(POPULATION_SIZE):
                genome = self.population[i]
                player = self.players[i]

                if not genome.is_dead and not genome.reached_finish:
                    active_players = True
                    # Kiểm tra an toàn chỉ số mảng
                    if self.current_frame < len(genome.genes):
                        dx, dy = genome.genes[self.current_frame]
                        player.move(dx, dy, self.wall_mask)

                    player_center = pygame.Vector2(player.rect.center)

                    # Kiểm tra va chạm kẻ địch
                    for en in self.enemies:
                        enemy_pos = pygame.Vector2(en.x, en.y)
                        if player_center.distance_to(enemy_pos) < (ENEMY_RADIUS + PLAYER_SIZE / 2):
                            genome.is_dead = True
                            genome.current_step = self.current_frame

                    # Kiểm tra ăn Coin theo đúng thứ tự
                    if genome.coins_collected < len(self.custom_coins):
                        c_pos = pygame.Vector2(self.custom_coins[genome.coins_collected]["pos"])
                        if player_center.distance_to(c_pos) < (10 + PLAYER_SIZE / 2):
                            genome.coins_collected += 1

                    # Kiểm tra vùng đích (chỉ khi đã ăn hết coin)
                    if genome.coins_collected == len(self.custom_coins):
                        if player.rect.colliderect(self.config["finish_rect"]):
                            genome.reached_finish = True
                            genome.current_step = self.current_frame
                            self.save_achievement()

                # Vẽ nhân vật
                p_color = RED if not genome.is_dead else (100, 100, 100)
                pygame.draw.rect(self.screen, p_color, player.rect)
                pygame.draw.rect(self.screen, BLACK, player.rect, 1)

            for en in self.enemies: en.draw(self.screen) 

            # Hiển thị UI
            ui = f"GEN: {self.generation} | DNA: {GENES_PER_STEP} | BEST COINS: {max(g.coins_collected for g in self.population)}"
            self.screen.blit(self.font.render(ui, True, BLACK), (20, 10))
            
            self.current_frame += 1
            if self.current_frame >= GENES_PER_STEP or not active_players:
                self.evolve()
                self.setup_generation()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

            pygame.display.flip()
            self.clock.tick(120)
        pygame.quit()

    # Trong file train.py

    def calculate_fitness(self, genome, player):
        # Thưởng lớn cho số lượng coin ăn được
        fitness = genome.coins_collected * 2000
        
        # Chọn mục tiêu hiện tại (Coin tiếp theo hoặc Đích)
        if genome.coins_collected < len(self.custom_coins):
            target = pygame.Vector2(self.custom_coins[genome.coins_collected]["pos"])
        else:
            target = self.target_pos
        
        dist = pygame.Vector2(player.rect.center).distance_to(target)
        fitness += (1 / (dist + 1)) * 1000
        
        if genome.reached_finish:
            fitness += (GENES_PER_STEP - genome.current_step) + 5000

        # --- THAY ĐỔI: Trừ 10% điểm nếu bị chết (giống C#) ---
        if genome.is_dead:
            fitness *= 0.9 
            
        return fitness

    def evolve(self):
        # --- THAY ĐỔI: Đột biến mạnh 5 bước cuối của các cá thể chết trước khi chọn lọc ---
        for genome in self.population:
            if genome.is_dead:
                death_step = genome.current_step
                # Xác định vị trí bắt đầu đột biến (tối đa 5 bước trước khi chết)
                start_mutate = max(0, death_step - 5)
                for j in range(start_mutate, death_step):
                    angle = random.uniform(0, 2 * math.pi)
                    genome.genes[j] = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)

        # Sau đó mới tính fitness và sắp xếp như cũ
        for i in range(POPULATION_SIZE):
            self.population[i].fitness = self.calculate_fitness(self.population[i], self.players[i])
        
        self.population.sort(key=lambda x: x.fitness, reverse=True)
            
        new_pop = []
        
        # 1. Đối với Elitism (Cá thể ưu tú)
        for i in range(ELITISM_COUNT):
            elite = self.population[i]
            while len(elite.genes) < GENES_PER_STEP:
                last_gene = elite.genes[-1] if elite.genes else None
                if last_gene is None or random.random() < 0.1:
                    angle = random.uniform(0, 2 * math.pi)
                    last_gene = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)
                elite.genes.append(last_gene)
            new_pop.append(elite)
        
        # Tạo thế hệ con lai
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = random.choice(self.population[:10]), random.choice(self.population[:10])
            child = Genome(GENES_PER_STEP)
            
            # Crossover
            parent_dna_len = len(p1.genes)
            cp = random.randint(0, parent_dna_len)
            child_dna = p1.genes[:cp] + p2.genes[cp:]
            
            # Bù đắp các gene còn thiếu do tăng DNA
            while len(child_dna) < GENES_PER_STEP:
                last_gene = child_dna[-1] if child_dna else None
                if last_gene is None or random.random() < 0.1:
                    angle = random.uniform(0, 2 * math.pi)
                    last_gene = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)
                child_dna.append(last_gene)
            
            # Đột biến (Mutation)
            for j in range(len(child_dna)):
                if random.random() < MUTATION_RATE:
                    angle = random.uniform(0, 2 * math.pi)
                    child_dna[j] = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)
            
            child.genes = child_dna
            new_pop.append(child)
            
        self.population = new_pop

    def save_achievement(self):
        with open("archivement.txt", "a", encoding="utf-8") as f:
            f.write(f"Level {self.level}: Win at Gen {self.generation} | DNA: {GENES_PER_STEP}\n")

if __name__ == "__main__":
    trainer = TrainVisualizer(level=1)
    trainer.run()