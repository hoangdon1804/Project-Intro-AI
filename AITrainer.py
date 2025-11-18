import random
import math
import pygame
import sys
from settings import *
from Game import Game

class AITrainer:
    def __init__(self, level, population_size, max_move_limit, visualize_mode=0):
        self.level = level
        self.population_size = population_size
        self.max_move_limit = max_move_limit
        self.generation = 0
        self.visualize_mode = visualize_mode
        self.population = []
        self.best_score_so_far = -float('inf')

    def _calculate_final_score(self, game_instance, player_instance, cause_of_death):
        target_pos = None
        next_checkpoint_index = player_instance.last_checkpoint_reached
        all_checkpoints_cleared = next_checkpoint_index >= len(game_instance.checkpoints)
        
        if all_checkpoints_cleared:
            target_pos = game_instance.target_j_pos
        else:
            target_pos = game_instance.checkpoints[next_checkpoint_index]

        player_center_x = player_instance.rect.x + player_instance.size / 2
        player_center_y = player_instance.rect.y + player_instance.size / 2
        distance_to_next = math.hypot(target_pos['x'] - player_center_x, target_pos['y'] - player_center_y)

        progress_score = (player_instance.last_checkpoint_reached - 1) * CHECKPOINT_REWARD
        progress_score += DISTANCE_REWARD_BASE / (1.0 + distance_to_next)
        final_fitness = (progress_score) ** 2
        
        if cause_of_death != 'win' and player_instance.last_checkpoint_reached <= 1:
            final_fitness *= 0.5

        if cause_of_death == 'win':
            final_fitness += 1e18

        return final_fitness, distance_to_next

    def _run_headless_simulation(self, moves_sequence):
        game = Game(headless=True)
        player = game.reset(self.level)
        player.moves = moves_sequence
        player.max_move_limit = self.max_move_limit
        
        done, cause = False, ''
        max_simulation_steps = self.max_move_limit + 10

        for _ in range(max_simulation_steps):
            player.update()
            game.enemies.update()
            
            if not player.is_alive:
                cause = player.cause_of_death
                done = True
                break

            if pygame.sprite.spritecollide(player, game.enemies, False):
                player.die('enemy_hit')
                cause = player.cause_of_death
                done = True
                break

            zones_hit = pygame.sprite.spritecollide(player, game.zones, False)
            if zones_hit:
                for zone in zones_hit:
                    if zone.type.isdigit():
                        checkpoint_id = int(zone.type)
                        if checkpoint_id == player.last_checkpoint_reached + 1:
                            player.last_checkpoint_reached = checkpoint_id
                    elif zone.type == 'j':
                        if player.last_checkpoint_reached == game.checkpoints[-1]['id']:
                            player.die('win') 
                            cause = player.cause_of_death
                            done = True
                            break
            if done:
                break
        
        if not done and player.is_alive:
            player.die('timeout') 
            cause = player.cause_of_death
        
        score, distance = self._calculate_final_score(game, player, cause)
        
        final_moves_str = "".join(player.full_move_history)
        
        return {
            "moves": final_moves_str, 
            "score": score, "cause": cause, 
            "actual_move_count": player.actual_move_count, "distance_to_target": distance,
            "checkpoints_passed": player.last_checkpoint_reached - 1
        }

    def _visualize_best_simulation(self, best_individual):
        print("-> Đang hiển thị cá thể tốt nhất...")
        game = Game(headless=False)
        player = game.reset(self.level)
        player.moves = best_individual['moves']
        player.max_move_limit = self.max_move_limit
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
            
            player.update()
            game.enemies.update() 
            
            if not player.is_alive: running = False

            if pygame.sprite.spritecollide(player, game.enemies, False): player.die('enemy_hit')
            zones_hit = pygame.sprite.spritecollide(player, game.zones, False)
            if zones_hit:
                for zone in zones_hit:
                    if zone.type.isdigit():
                        if int(zone.type) == player.last_checkpoint_reached + 1: player.last_checkpoint_reached = int(zone.type)
                    elif zone.type == 'j':
                        if player.last_checkpoint_reached == game.checkpoints[-1]['id']: player.die('win')

            next_target_text = f"Next Target: {'J (Win)' if player.last_checkpoint_reached >= len(game.checkpoints) else player.last_checkpoint_reached + 1}"
            texts = [f"GENERATION: {self.generation}", f"SCORE: {best_individual['score']:.2E}", next_target_text, f"Step: {player.actual_move_count}/{self.max_move_limit}"]
            game.draw(additional_texts=texts)
            game.clock.tick(FPS)
                
        pygame.time.wait(2000); game.quit(); print("-> Hiển thị hoàn tất.")
    
    def _create_initial_population(self):
        initial_population = []
        initial_change_limit = 80 

        for _ in range(self.population_size):
            moves, direction, changes = "", 0, 0
            for _ in range(self.max_move_limit): 
                if random.randint(0, 10) == 0: 
                    changes += 1
                    direction = random.randint(0, 8)
                
                if changes > initial_change_limit: 
                    break
                moves += str(direction)
            initial_population.append(moves)
        self.population = initial_population
        print(f"Thế hệ {self.generation}: Đã tạo {self.population_size} cá thể ngẫu nhiên (initial_change_limit: {initial_change_limit}).")

    def _apply_conditional_mutation(self, parent_individual):
        parent_moves = parent_individual['moves']; parent_cause = parent_individual['cause']
        if not parent_moves: return ""
        child_moves_list = list(parent_moves)
        if parent_cause != 'win' and len(child_moves_list) > 5:
            for i in range(len(child_moves_list) - 5):
                if random.random() < NORMAL_MUTATION_CHANCE: child_moves_list[i] = str(random.randint(0, 8))
            for i in range(len(child_moves_list) - 5, len(child_moves_list)):
                if random.random() < END_STEP_MUTATION_CHANCE: child_moves_list[i] = str(random.randint(0, 8))
        else:
            for i in range(len(child_moves_list)):
                if random.random() < NORMAL_MUTATION_CHANCE: child_moves_list[i] = str(random.randint(0, 8))
        return "".join(child_moves_list)

    def _apply_elite_mutation(self, parent_moves):
        if not parent_moves: return ""
        
        child_moves_list = list(parent_moves)
        length = len(child_moves_list)

        if length > 10:
            for i in range(length - 10, length):
                if random.random() < END_STEP_MUTATION_CHANCE:
                    child_moves_list[i] = str(random.randint(0, 8))
        else: 
            for i in range(length):
                if random.random() < NORMAL_MUTATION_CHANCE:
                    child_moves_list[i] = str(random.randint(0, 8))

        return "".join(child_moves_list)

    def _apply_decade_reset_mutation(self, best_moves):
        """
        Tạo một cá thể mới từ cá thể tốt nhất.
        Giữ lại một tỷ lệ phần trăm ban đầu (DECADE_RESET_KEEP_PERCENTAGE),
        đột biến phần còn lại với xác suất đặc biệt.
        """
        if not best_moves: return ""

        midpoint = int(len(best_moves) * DECADE_RESET_KEEP_PERCENTAGE)
        
        first_half = list(best_moves[:midpoint])
        second_half_original = list(best_moves[midpoint:])
        
        new_second_half = []
        for move in second_half_original:
            if random.random() < DECADE_RESET_MUTATION_CHANCE:
                new_second_half.append(str(random.randint(0, 8)))
            else:
                new_second_half.append(move)
        
        return "".join(first_half + new_second_half)

    def _create_new_generation(self, sorted_results):
        if self.generation > 0 and self.generation % 10 == 0:
            print(f"\n*** THỰC HIỆN DECADE RESET TẠI THẾ HỆ {self.generation} ***")
            print("Tất cả cá thể mới sẽ được tạo dựa trên cá thể tốt nhất, với 50% sau được đột biến.")
            new_population = []
            best_moves = sorted_results[0]['moves']

            for _ in range(self.population_size):
                child_moves = self._apply_decade_reset_mutation(best_moves)
                new_population.append(child_moves)
            
            self.population = new_population
            print(f"Đã tạo thế hệ mới với {len(self.population)} cá thể từ Decade Reset.")
            return 
        new_population = []
        
        best_parent = sorted_results[0]
        num_elites = 10
        print(f"Tạo {num_elites} cá thể ưu tú từ cá thể tốt nhất thế hệ trước...")
        for _ in range(num_elites):
            elite_child = self._apply_elite_mutation(best_parent['moves'])
            new_population.append(elite_child)

        parent_pool = sorted_results

        if len(parent_pool) < TOURNAMENT_SIZE:
            print(f"Cảnh báo nghiêm trọng: Toàn bộ quần thể (size: {len(parent_pool)}) quá nhỏ để tạo giải đấu. Tạo lại quần thể ngẫu nhiên.")
            self._create_initial_population()
            return

        remaining_population_size = self.population_size - num_elites
        print(f"Tạo {remaining_population_size} cá thể còn lại bằng Tournament Selection từ toàn bộ {len(parent_pool)} cá thể của thế hệ trước.")
        for _ in range(remaining_population_size):
            tournament_contenders = random.sample(parent_pool, TOURNAMENT_SIZE)
            winner_parent = max(tournament_contenders, key=lambda x: x['score'])
            child_moves = self._apply_conditional_mutation(winner_parent)
            new_population.append(child_moves)

        self.population = new_population
        print(f"Đã tạo thế hệ mới với {len(self.population)} cá thể ({num_elites} ưu tú, {remaining_population_size} từ giải đấu).")
        
    def _run_parallel_visual_simulation(self):
        game = Game(headless=False)
        living_players = game.reset_for_population(self.level, self.population, self.max_move_limit)
        results = []
        while living_players:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.quit()
                    return []
            
            game.all_sprites.update(); game.enemies.update()

            for player in living_players[:]:
                if not player.is_alive:
                    if player in living_players: living_players.remove(player)
                    continue

                if pygame.sprite.spritecollide(player, game.enemies, False): player.die('enemy_hit')
                zones_hit = pygame.sprite.spritecollide(player, game.zones, False)
                if zones_hit:
                    for zone in zones_hit:
                        if zone.type.isdigit():
                            if int(zone.type) == player.last_checkpoint_reached + 1: player.last_checkpoint_reached = int(zone.type)
                        elif zone.type == 'j':
                            if player.last_checkpoint_reached == game.checkpoints[-1]['id']: player.die('win')

                if not player.is_alive:
                    final_moves_str = "".join(player.full_move_history)
                    score, dist = self._calculate_final_score(game, player, player.cause_of_death)
                    results.append({
                        "moves": final_moves_str, "score": score, "cause": player.cause_of_death, 
                        "actual_move_count": player.actual_move_count, "distance_to_target": dist,
                        "checkpoints_passed": player.last_checkpoint_reached - 1
                    })
                    if player in living_players: living_players.remove(player)

            texts = [f"GENERATION: {self.generation}", f"PLAYERS ALIVE: {len(living_players)}/{self.population_size}", f"MAX MOVES: {self.max_move_limit}"]
            game.draw(additional_texts=texts); game.clock.tick(FPS)
        game.quit()
        return results

    def run_training(self, max_generations=100):
        self._create_initial_population()
        while self.generation < max_generations:
            print(f"\n--- Bắt đầu Thế hệ {self.generation} (max_move_limit: {self.max_move_limit}) ---")
            results = []
            if self.visualize_mode == 3: results = self._run_parallel_visual_simulation()
            else: results = [self._run_headless_simulation(moves) for moves in self.population]
            
            if not results:
                print("Lỗi: Không có kết quả (có thể do cửa sổ hiển thị đã bị đóng). Dừng huấn luyện.")
                return

            results.sort(key=lambda x: x['score'], reverse=True)
            best_individual = results[0]
            current_best_score = best_individual['score']
            
            score_str=f"{current_best_score:.2E}"; dist_str=f"{best_individual['distance_to_target']:.2f}"; cause_str=f"{best_individual['cause']}"
            checkpoints_str = f"{best_individual['checkpoints_passed']}"
            
            print(f"Kết thúc Thế hệ {self.generation}. Điểm cao nhất: {score_str} | Checkpoints: {checkpoints_str} | Khoảng cách: {dist_str} | Nguyên nhân: {cause_str}")

            if current_best_score > self.best_score_so_far:
                self.best_score_so_far = current_best_score
                self.max_move_limit += 50
                print(f"-> Kết quả cải thiện! Tăng max_move_limit lên {self.max_move_limit}")
            else:
                 print(f"-> Kết quả không cải thiện. Giữ nguyên max_move_limit là {self.max_move_limit}")

            if best_individual['cause'] == 'win':
                print(f"\n!!! AI ĐÃ CHIẾN THẮNG SAU {self.generation + 1} THẾ HỆ !!!");
                with open(archive_path, 'a', encoding='utf-8') as f: f.write(f"Level {self.level} Solution:\n{best_individual['moves']}\n\n")
                self._visualize_best_simulation(best_individual); return
            if self.visualize_mode == 1: self._visualize_best_simulation(best_individual)
            self._create_new_generation(results); self.generation += 1
        print(f"\nĐạt giới hạn {max_generations} thế hệ.")