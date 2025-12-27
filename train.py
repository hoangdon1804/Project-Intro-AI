import pygame
import random
import math
import json
import sys
import os
from settings import *
from sprites import Player, Enemy
from level_manager import LevelManager

# --- Cấu hình Giải thuật Di truyền ---
POPULATION_SIZE = 1000
GENES_PER_STEP = 300 
MUTATION_RATE = 0.05
ELITISM_COUNT = 10
DNA_INCREASE_RATE = 50  # Tăng DNA sau mỗi 10 thế hệ

class Genome:
    def __init__(self, length):
        self.genes = []
        last_gene = None
        for _ in range(length):
            # 10% cơ hội đổi hướng để di chuyển mượt hơn 
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
        pygame.display.set_caption(f"AI Trainer Level {level} - Sequential Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.num_font = pygame.font.SysFont("Arial", 14, bold=True)

        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        if self.config["walls_pts"]:
            pygame.draw.polygon(surf, BLACK, self.config["walls_pts"], WALL_WIDTH) 
        self.wall_mask = pygame.mask.from_surface(surf) 

        self.custom_coins = []
        if level == 0:
            self.custom_coins = [
                {"pos": (325, 475), "type": "RED"},    
                {"pos": (775, 225), "type": "RED"}
            ]
        elif level == 1:
            self.custom_coins = [
                {"pos": (275, 350), "type": "RED"},
                {"pos": (550, 350), "type": "YELLOW"},
                {"pos": (825, 350), "type": "RED"}
            ]
        elif level == 2:
            self.custom_coins = [
                {"pos": (475, 225), "type": "YELLOW"}
            ]
        elif level == 3:
            self.custom_coins = [
                {"pos": (550, 250), "type": "YELLOW"},
                {"pos": (625, 325), "type": "RED"},
                {"pos": (700, 400), "type": "YELLOW"},
                {"pos": (625, 475), "type": "RED"},
                {"pos": (550, 550), "type": "YELLOW"},
                {"pos": (375, 425), "type": "RED"}
            ]
        self.target_pos = pygame.Vector2(self.config["finish_rect"].center)
        self.finished = False
        self.generation = 0
        self.setup_generation()

    def setup_generation(self):
        global GENES_PER_STEP
        
        # Tăng DNA sau mỗi 10 thế hệ
        if self.generation > 0 and self.generation % 15 == 0:
            GENES_PER_STEP += DNA_INCREASE_RATE
            print(f"--- Gen {self.generation}: DNA increased to {GENES_PER_STEP} ---")
            
            # Bù đắp gene cho quần thể hiện tại
            for genome in self.population:
                while len(genome.genes) < GENES_PER_STEP:
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

            # Vẽ Coin
            for i, c_data in enumerate(self.custom_coins):
                color = RED if c_data["type"] == "RED" else YELLOW_COIN
                pygame.draw.circle(self.screen, color, c_data["pos"], 10)
                pygame.draw.circle(self.screen, BLACK, c_data["pos"], 10, 2)
                lbl = self.num_font.render(str(i+1), True, BLACK)
                self.screen.blit(lbl, (c_data["pos"][0]-5, c_data["pos"][1]-25))

            active_players = False
            self.angle += 0.025
            for en in self.enemies: en.update(self.angle)

            for i in range(POPULATION_SIZE):
                genome = self.population[i]
                player = self.players[i]

                if not genome.is_dead and not genome.reached_finish:
                    active_players = True
                    if self.current_frame < len(genome.genes):
                        dx, dy = genome.genes[self.current_frame]
                        player.move(dx, dy, self.wall_mask)

                    player_center = pygame.Vector2(player.rect.center)

                    # Check va chạm kẻ địch
                    for en in self.enemies:
                        enemy_pos = pygame.Vector2(en.x, en.y)
                        if player_center.distance_to(enemy_pos) < (ENEMY_RADIUS + PLAYER_SIZE / 2):
                            genome.is_dead = True
                            genome.current_step = self.current_frame

                    # Check ăn Coin tuần tự
                    if genome.coins_collected < len(self.custom_coins):
                        c_pos = pygame.Vector2(self.custom_coins[genome.coins_collected]["pos"])
                        if player_center.distance_to(c_pos) < (10 + PLAYER_SIZE / 2):
                            genome.coins_collected += 1

                    # Check Win: CHỈ thắng khi ăn hết coin VÀ chạm đích
                    if genome.coins_collected == len(self.custom_coins):
                        if player.rect.colliderect(self.config["finish_rect"]):
                            # Ở Level 2 (spawn tại đích), cần di chuyển ít nhất vài bước mới tính thắng
                            if self.current_frame > 5:
                                genome.reached_finish = True
                                genome.current_step = self.current_frame
                                self.finished = True

                p_color = RED if not genome.is_dead else (100, 100, 100)
                pygame.draw.rect(self.screen, p_color, player.rect)
                pygame.draw.rect(self.screen, BLACK, player.rect, 1)

            for en in self.enemies: en.draw(self.screen) 

            ui = f"GEN: {self.generation} | DNA: {GENES_PER_STEP} | BEST COINS: {max(g.coins_collected for g in self.population)}"
            self.screen.blit(self.font.render(ui, True, BLACK), (20, 10))
            
            self.current_frame += 1
            if self.current_frame >= GENES_PER_STEP or not active_players:
                self.evolve() # Tính fitness và tạo thế hệ mới
                
                if self.finished:
                    # Nếu có người thắng trong thế hệ này, tìm người tốt nhất và lưu
                    best_genome = max(self.population, key=lambda g: g.fitness)
                    self.save_achievement(best_genome)
                    print(f"CONGRATULATIONS! Level {self.level} cleared. Training stopped.")
                    running = False # Thoát vòng lặp chính
                else:
                    self.setup_generation()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

            pygame.display.flip()
            self.clock.tick(120)
        pygame.quit()


    def calculate_fitness(self, genome, player):
        # Thưởng theo số coin đã ăn
        fitness = genome.coins_collected * 2000
        
        # Xác định Target hiện tại
        if genome.coins_collected < len(self.custom_coins):
            # Nếu chưa ăn hết coin, target là coin tiếp theo
            target = pygame.Vector2(self.custom_coins[genome.coins_collected]["pos"])
            dist = pygame.Vector2(player.rect.center).distance_to(target)
            fitness += (1 / (dist + 1)) * 1000
            
            # Phạt nếu chạm đích khi chưa ăn đủ coin (đặc biệt cho Level 2)
            if player.rect.colliderect(self.config["finish_rect"]):
                fitness *= 0.5
        else:
            # Nếu đã ăn hết coin, target mới là Đích
            target = self.target_pos
            dist = pygame.Vector2(player.rect.center).distance_to(target)
            fitness += (1 / (dist + 1)) * 1000
        
        if genome.reached_finish:
            fitness += (GENES_PER_STEP - genome.current_step) + 5000

        if genome.is_dead:
            fitness *= 0.8 
            
        return fitness

    def evolve(self):
        cnt = 0
        # Đột biến có tính kế thừa cho các cá thể chết [cite: 130]
        for genome in self.population:
            if genome.is_dead:
                # Xác định điểm bắt đầu đột biến (20 bước trước khi chết) [cite: 130]
                start_mutate = max(1, genome.current_step - 10) 
                
                # Lấy gene làm mốc từ trước đoạn đột biến để đảm bảo tính liên tục 
                last_gene = genome.genes[start_mutate - 1]
                
                for j in range(start_mutate, genome.current_step):
                    # 10% cơ hội đổi hướng so với bước trước đó 
                    if random.random() < 0.1:
                        angle = random.uniform(0, 2 * math.pi)
                        last_gene = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)
                    
                    # Gán gene (có thể là hướng mới hoặc hướng cũ của j-1) 
                    genome.genes[j] = last_gene

        for i in range(POPULATION_SIZE):
            self.population[i].fitness = self.calculate_fitness(self.population[i], self.players[i])
        
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        new_pop = []
        
        # Elitism
        for i in range(ELITISM_COUNT):
            elite = self.population[i]
            while len(elite.genes) < GENES_PER_STEP:
                last_gene = elite.genes[-1] if elite.genes else None
                if last_gene is None or random.random() < 0.1:
                    angle = random.uniform(0, 2 * math.pi)
                    last_gene = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)
                elite.genes.append(last_gene)
            new_pop.append(elite)
        # Crossover & Mutation
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = random.choice(self.population[:10]), random.choice(self.population[:10])
            child = Genome(GENES_PER_STEP)
            cp = random.randint(0, len(p1.genes))
            child_dna = p1.genes[:cp] + p2.genes[cp:]
            
            while len(child_dna) < GENES_PER_STEP:
                last_gene = child_dna[-1] if child_dna else None
                if last_gene is None or random.random() < 0.1:
                    angle = random.uniform(0, 2 * math.pi)
                    last_gene = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)
                child_dna.append(last_gene)
            if cnt < POPULATION_SIZE * 0.2:
                for j in range(len(child_dna)):
                    if random.random() < MUTATION_RATE:
                        angle = random.uniform(0, 2 * math.pi)
                        child_dna[j] = (math.cos(angle) * PLAYER_SPEED, math.sin(angle) * PLAYER_SPEED)
            cnt = cnt + 1   
            child.genes = child_dna
            new_pop.append(child)
            
        self.population = new_pop

    def save_achievement(self, best_genome):
        file_path = "archivement.txt"
        achievements = {}

        # 1. Đọc dữ liệu cũ nếu file tồn tại
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    achievements = json.load(f)
            except:
                achievements = {}

        # 2. Chuẩn bị dữ liệu mới
        new_data = {
            "level": self.level,
            "generation": self.generation,
            "population_size": POPULATION_SIZE,
            "dna_length": len(best_genome.genes),
            "fitness": best_genome.fitness,
            "dna": best_genome.genes # Lưu list các tuple (dx, dy)
        }

        # 3. Kiểm tra level đã tồn tại chưa
        lvl_key = str(self.level)
        if lvl_key in achievements:
            if best_genome.fitness > achievements[lvl_key]["fitness"]:
                achievements[lvl_key] = new_data
                print(f"Updated Level {self.level} with higher fitness: {best_genome.fitness}")
            else:
                print(f"Level {self.level} already has a better record. Skipping save.")
        else:
            achievements[lvl_key] = new_data
            print(f"Saved new record for Level {self.level}")

        # 4. Ghi lại vào file (dùng định dạng JSON để dễ đọc/ghi DNA)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(achievements, f, indent=4)

if __name__ == "__main__":
    # Bắt đầu huấn luyện (Thay đổi level tại đây)
    trainer = TrainVisualizer(level=3)
    trainer.run()