import pygame
import sys
import random
from Game import Game
from settings import *
from train import POPULATION_SIZE

def get_last_solution():
    """Đọc chuỗi hành động cuối cùng từ archive.txt."""
    try:
        with open(archive_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip().isdigit()]
        if lines:
            solution = lines[-1]
            print(f"Đã tìm thấy lời giải với {len(solution)} bước.")
            return solution
        print("Lỗi: Không tìm thấy chuỗi hành động hợp lệ trong archive.txt")
        return None
    except FileNotFoundError:
        print(f"Lỗi: không tìm thấy {archive_path}")
        return None

def _apply_replay_mutation(parent_moves):
    if not parent_moves: return ""
    child_moves_list = list(parent_moves)
    mutation_chance = 0.05  # 5% cơ hội đột biến mỗi bước
    for i in range(len(child_moves_list)):
        if random.random() < mutation_chance:
            child_moves_list[i] = str(random.randint(0, 8))
    
    # Thêm một chút ngẫu nhiên vào độ dài của lộ trình
    if random.random() < 0.1:
        cutoff = random.randint(int(len(child_moves_list) * 0.95), len(child_moves_list))
        child_moves_list = child_moves_list[:cutoff]
        
    return "".join(child_moves_list)

def run_replay(moves, level):
    """
    Chạy lại game với chuỗi hành động cho trước, hiển thị song song
    một quần thể đầy đủ giống như chế độ huấn luyện.
    """
    if not moves:
        return

    game = Game(headless=False)

    # ================================================================= #
    # === THAY ĐỔI: TẠO RA MỘT QUẦN THỂ DỰA TRÊN LỘ TRÌNH CHIẾN THẮNG === #
    # ================================================================= #
    print(f"Tạo một quần thể gồm {POPULATION_SIZE} cá thể để replay...")
    population_moves = [moves]  # Cá thể đầu tiên luôn là cá thể chiến thắng
    
    # Tạo các cá thể còn lại bằng cách đột biến nhẹ lộ trình chiến thắng
    for _ in range(POPULATION_SIZE - 1):
        mutated_moves = _apply_replay_mutation(moves)
        population_moves.append(mutated_moves)

    # Sử dụng hàm reset_for_population để tạo tất cả người chơi
    max_moves_for_replay = len(moves) + 100
    living_players = game.reset_for_population(level, population_moves, max_moves_for_replay)

    # Tìm và đổi màu cá thể chính (cá thể chiến thắng) để làm nổi bật
    main_player = living_players[0]
    main_player.image.fill(black) 
    pygame.draw.rect(main_player.image, lime, [4, 4, main_player.size - 8, main_player.size - 8])
    
    running = True
    print("--- Bắt đầu Replay song song ---")

    # ================================================================= #
    # === THAY ĐỔI: VÒNG LẶP GAME ĐỂ QUẢN LÝ NHIỀU CÁ THỂ === #
    # ================================================================= #
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # Nếu không còn cá thể nào sống, hoặc cá thể chính đã chết, kết thúc replay
        if not living_players or not main_player.is_alive:
            running = False

        # Cập nhật trạng thái của tất cả sprites (người chơi, kẻ địch)
        game.all_sprites.update()
        game.enemies.update()

        # Kiểm tra va chạm và điều kiện thắng cho từng cá thể
        for player in living_players[:]:  # Dùng slice copy để có thể xóa phần tử khỏi list
            if not player.is_alive:
                if player in living_players:
                    living_players.remove(player)
                continue

            # a. Va chạm với kẻ địch
            if pygame.sprite.spritecollide(player, game.enemies, False):
                player.die('enemy_hit')

            # b. Đi vào vùng an toàn/checkpoint/chiến thắng
            zones_hit = pygame.sprite.spritecollide(player, game.zones, False)
            if zones_hit:
                for zone in zones_hit:
                    if zone.type.isdigit():
                        if int(zone.type) == player.last_checkpoint_reached + 1:
                            player.last_checkpoint_reached = int(zone.type)
                    elif zone.type == 'j':
                        if player.last_checkpoint_reached == game.checkpoints[-1]['id']:
                            player.die('win')
                            if player is main_player:
                                print("Replay kết thúc: CÁ THỂ CHÍNH ĐÃ CHIẾN THẮNG!")

            # Xóa cá thể nếu nó vừa chết trong vòng lặp này
            if not player.is_alive and player in living_players:
                living_players.remove(player)

        # Vẽ lại màn hình với thông tin cập nhật
        texts = [
            "PARALLEL REPLAY MODE",
            f"PLAYERS ALIVE: {len(living_players)}/{POPULATION_SIZE}",
            f"Main Player Step: {main_player.current_move_index}/{len(moves)}"
        ]
        game.draw(additional_texts=texts)
        game.clock.tick(FPS)

    pygame.time.wait(2000)
    print(f"Trạng thái cuối cùng của cá thể chính: {main_player.cause_of_death}")
    print("--- Kết thúc Replay ---")
    game.quit()

if __name__ == "__main__":
    LEVEL_TO_REPLAY = 1
    winning_moves = get_last_solution()
    if winning_moves:
        run_replay(winning_moves, LEVEL_TO_REPLAY)