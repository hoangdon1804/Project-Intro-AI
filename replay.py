
import pygame
import sys
from Game import Game
from settings import *

def get_last_solution():
    """Đọc chuỗi hành động cuối cùng từ archive.txt."""
    try:
        with open(archive_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip().isdigit()]
        if lines:
            print(f"Đã tìm thấy lời giải với {len(lines[-1])} bước.")
            return lines[-1]
        print("Lỗi: Không tìm thấy chuỗi hành động hợp lệ trong archive.txt")
        return None
    except FileNotFoundError:
        print(f"Lỗi: không tìm thấy {archive_path}")
        return None

def run_replay(moves, level):
    """Chạy lại game với chuỗi hành động cho trước."""
    if not moves:
        return

    game = Game(headless=False)
    player = game.reset(level)
    player.image.fill(black) # Đổi màu cho dễ phân biệt
    pygame.draw.rect(player.image, lime, [4, 4, player.size - 8, player.size - 8])
    
    move_index = 0
    running = True
    print("--- Bắt đầu Replay ---")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        action = 0 # Mặc định đứng yên
        if move_index < len(moves):
            action = int(moves[move_index])
            move_index += 1
        
        # Cập nhật game state
        done, cause = game.step(action)
        if done:
            print(f"Replay kết thúc: {cause}")
            # Giữ màn hình một lúc rồi thoát
            pygame.time.wait(2000)
            running = False

        # Vẽ màn hình
        texts = [
            "REPLAY MODE",
            f"Step: {move_index}/{len(moves)}"
        ]
        game.draw(additional_texts=texts)
        game.clock.tick(FPS)

    print("--- Kết thúc Replay ---")
    game.quit()

if __name__ == "__main__":
    LEVEL_TO_REPLAY = 1
    winning_moves = get_last_solution()
    if winning_moves:
        run_replay(winning_moves, LEVEL_TO_REPLAY)