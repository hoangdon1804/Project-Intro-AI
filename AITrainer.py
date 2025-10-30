import random
import math
import pygame
import sys
from settings import *
from Game import Game

class AITrainer:
    def __init__(self, level, population_size, change_limit, visualize_mode=0):
        self.level = level; self.population_size = population_size; self.change_limit = change_limit; self.generation = 0
        self.visualize_mode = visualize_mode; self.population = []

    def _calculate_final_score(self, game_instance, player_instance, cause_of_death, actual_move_count):
        player_center_x = player_instance.rect.x + player_instance.size / 2
        player_center_y = player_instance.rect.y + player_instance.size / 2
        distance_to_target = math.hypot(game_instance.target_x - player_center_x, game_instance.target_y - player_center_y)
        reward = 150000.0 / (distance_to_target + 1.0)
        safe_zone_penalty = player_instance.safe_zone_frames * SAFE_ZONE_PENALTY_WEIGHT
        move_penalty = actual_move_count * MOVE_PENALTY_WEIGHT
        final_score = reward - safe_zone_penalty - move_penalty
        if cause_of_death == 'enemy_hit': final_score -= ENEMY_HIT_PENALTY
        elif cause_of_death == 'wander_death': final_score -= WANDER_DEATH_PENALTY
        elif cause_of_death == 'win': final_score += WIN_REWARD
        return final_score, distance_to_target

    def _run_headless_simulation(self, moves_sequence):
        game = Game(headless=True)
        player = game.reset(self.level)
        player.moves = moves_sequence
        
        done, cause = False, ''
        max_simulation_steps = len(player.moves) + 500 

        for _ in range(max_simulation_steps):
            player.update()
            
            done, cause_from_step = game.step(player, -1)
            if done:
                cause = cause_from_step; break
            
            if not player.is_alive:
                cause = player.cause_of_death; break
        
        if not done and player.is_alive: cause = 'timeout'
        
        score, distance = self._calculate_final_score(game, player, cause, player.actual_move_count)
        return {"moves": player.moves, "score": score, "cause": cause, "actual_move_count": player.actual_move_count, "distance_to_target": distance}

    def _visualize_best_simulation(self, best_individual):
        print("-> Đang hiển thị cá thể tốt nhất...")
        game = Game(headless=False)
        player = game.reset(self.level)
        player.moves = best_individual['moves']
        
        running = True
        while running and player.is_alive:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
            
            player.update()
            done, _ = game.step(player, -1)
            if done: running = False

            texts = [f"GENERATION: {self.generation}", f"BEST SCORE: {best_individual['score']:.2f}", f"DISTANCE: {best_individual['distance_to_target']:.2f}", f"ACTUAL MOVES: {best_individual['actual_move_count']}", f"Step: {player.current_move_index}/{len(player.moves)}"]
            game.draw(additional_texts=texts)
            game.clock.tick(FPS)
        game.quit()
        print("-> Hiển thị hoàn tất.")
    
    def _create_initial_population(self):
        initial_population = []
        for _ in range(self.population_size):
            moves, direction, changes = "", 0, 0
            for _ in range(self.change_limit * 10): 
                if random.randint(0, 10) == 0: changes += 1; direction = random.randint(0, 8)
                if changes > self.change_limit: break
                moves += str(direction)
            initial_population.append(moves)
        self.population = initial_population
        print(f"Thế hệ {self.generation}: Đã tạo {self.population_size} cá thể ngẫu nhiên ban đầu.")

    def _create_offspring_by_step_mutation(self, parent_moves, mutation_chance):
        if not parent_moves: return ""
        child_moves_list = []
        for move in parent_moves:
            if random.random() < mutation_chance:
                child_moves_list.append(str(random.randint(0, 8)))
            else:
                child_moves_list.append(move)
        return "".join(child_moves_list)

    def _create_new_generation(self, sorted_results):
        if len(sorted_results) < NUM_ELITES_TO_USE:
            print(f"Cảnh báo: Không đủ {NUM_ELITES_TO_USE} cá thể. Tạo lại quần thể ngẫu nhiên.")
            self._create_initial_population(); return
        
        elites = sorted_results[:NUM_ELITES_TO_USE]
        new_population = []
        
        for parent in elites:
            parent_moves = parent['moves']
            
            # 7 con đột biến nhẹ (5%)
            for _ in range(50):
                new_population.append(self._create_offspring_by_step_mutation(parent_moves, LIGHT_MUTATION_CHANCE))
            
            # 2 con đột biến vừa (30%)
            for _ in range(0):
                new_population.append(self._create_offspring_by_step_mutation(parent_moves, MEDIUM_MUTATION_CHANCE))
                
            # 1 con đột biến mạnh (70%)
            for _ in range(0):
                new_population.append(self._create_offspring_by_step_mutation(parent_moves, HEAVY_MUTATION_CHANCE))

        self.population = new_population
        print(f"Đã tạo thế hệ mới từ Top {NUM_ELITES_TO_USE} cá thể với chiến lược đột biến 7/2/1.")
        
    def _run_parallel_visual_simulation(self):
        game = Game(headless=False)
        living_players = game.reset_for_population(self.level, self.population, self.change_limit)
        results = []
        while living_players:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: game.quit()
            
            game.all_sprites.update(); game.enemies.update()

            for player in living_players[:]:
                if pygame.sprite.spritecollide(player, game.enemies, False): player.die('enemy_hit')
                
                zones_hit = pygame.sprite.spritecollide(player, game.zones, False)
                if zones_hit:
                    player.safe_zone_frames += 1
                    for zone in zones_hit:
                        if zone.type == 'j': player.die('win')

                if not player.is_alive:
                    score, dist = self._calculate_final_score(game, player, player.cause_of_death, player.actual_move_count)
                    results.append({"moves": player.moves, "score": score, "cause": player.cause_of_death, "actual_move_count": player.actual_move_count, "distance_to_target": dist})
                    living_players.remove(player)

            texts = [f"GENERATION: {self.generation}", f"PLAYERS ALIVE: {len(living_players)} / {self.population_size}"]
            game.draw(additional_texts=texts); game.clock.tick(FPS)
        game.quit()
        return results

    def run_training(self, max_generations=100):
        self._create_initial_population()
        while self.generation < max_generations:
            print(f"\n--- Bắt đầu Thế hệ {self.generation} ---"); results = []
            if self.visualize_mode == 3: results = self._run_parallel_visual_simulation()
            else: results = [self._run_headless_simulation(moves) for moves in self.population]
            if not results: print("Lỗi: Không có kết quả."); return
            results.sort(key=lambda x: x['score'], reverse=True)
            best_individual = results[0]
            score_str=f"{best_individual['score']:.2f}"; dist_str=f"{best_individual['distance_to_target']:.2f}"; moves_str=f"{best_individual['actual_move_count']}"; cause_str=f"{best_individual['cause']}"
            print(f"Kết thúc Thế hệ {self.generation}. Điểm cao nhất: {score_str} | Khoảng cách: {dist_str} | Số bước: {moves_str} | Nguyên nhân: {cause_str}")
            if best_individual['cause'] == 'win':
                print(f"\n!!! AI ĐÃ CHIẾN THẮNG !!!");
                with open(archive_path, 'a', encoding='utf-8') as f: f.write(f"Level {self.level} Solution:\n{best_individual['moves']}\n\n")
                self._visualize_best_simulation(best_individual); return
            if self.visualize_mode == 1: self._visualize_best_simulation(best_individual)
            self._create_new_generation(results); self.generation += 1
        print(f"\nĐạt giới hạn {max_generations} thế hệ.")