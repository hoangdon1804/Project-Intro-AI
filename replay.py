import pygame
import sys
from Game import Game
from settings import *

def get_last_solution():
    """Đọc chuỗi hành động cuối cùng từ archive.txt."""
    try:
        with open(archive_path, 'r', encoding='utf-8') as f:
            # Lọc ra các dòng chỉ chứa chữ số (là chuỗi hành động)
            lines = [line.strip() for line in f if line.strip().isdigit()]
        if lines:
            # Lấy lời giải cuối cùng trong file
            solution = lines[-1]
            print(f"Đã tìm thấy lời giải với {len(solution)} bước.")
            return solution
        print("Lỗi: Không tìm thấy chuỗi hành động hợp lệ trong archive.txt")
        return None
    except FileNotFoundError:
        print(f"Lỗi: không tìm thấy {archive_path}")
        return None

def run_replay(moves, level):
    """
    Chạy lại game với chuỗi hành động cho trước.
    Phiên bản này được đồng bộ hóa để hoạt động đúng với logic của lớp Player.
    """
    if not moves:
        return

    game = Game(headless=False)
    player = game.reset(level)

    # --- THAY ĐỔI QUAN TRỌNG ---
    # Gán toàn bộ chuỗi hành động cho người chơi.
    # Người chơi sẽ tự động đi theo chuỗi này khi player.update() được gọi.
    player.moves = moves
    # Đặt giới hạn di chuyển đủ lớn để hoàn thành replay
    player.max_move_limit = len(moves) + 100 

    # Đổi màu người chơi để dễ phân biệt với chế độ huấn luyện/chơi thường
    player.image.fill(black) 
    pygame.draw.rect(player.image, lime, [4, 4, player.size - 8, player.size - 8])
    
    running = True
    print("--- Bắt đầu Replay ---")

    while running:
        # 1. XỬ LÝ SỰ KIỆN (INPUT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # 2. CẬP NHẬT TRẠNG THÁI GAME
        # Chỉ cần gọi player.update(), nó sẽ tự đọc hành động từ chuỗi 'moves'
        player.update()
        game.enemies.update()

        # 3. KIỂM TRA ĐIỀU KIỆN KẾT THÚC
        # a. Người chơi chết (ví dụ: hết nước đi)
        if not player.is_alive:
            print(f"Replay kết thúc: {player.cause_of_death}")
            running = False

        # b. Va chạm với kẻ địch
        if pygame.sprite.spritecollide(player, game.enemies, False):
            print("Replay kết thúc: Bị kẻ địch va phải.")
            running = False
        
        # c. Đi vào vùng chiến thắng
        zones_hit = pygame.sprite.spritecollide(player, game.zones, False)
        if zones_hit:
            for zone in zones_hit:
                if zone.type == 'j':
                    # Đảm bảo đã đi qua hết checkpoint trước khi thắng
                    if player.last_checkpoint_reached == game.checkpoints[-1]['id']:
                        print("Replay kết thúc: CHIẾN THẮNG!")
                        running = False
                        break
        
        # Nếu một trong các điều kiện trên xảy ra, vòng lặp sẽ dừng ở lần kiểm tra tiếp theo

        # 4. VẼ LÊN MÀN HÌNH
        texts = [
            "REPLAY MODE",
            # Sử dụng current_move_index của player để hiển thị tiến độ
            f"Step: {player.current_move_index}/{len(moves)}"
        ]
        game.draw(additional_texts=texts)
        game.clock.tick(FPS)

    # Đợi một chút trước khi đóng cửa sổ
    pygame.time.wait(2000)
    print("--- Kết thúc Replay ---")
    game.quit()

if __name__ == "__main__":
    LEVEL_TO_REPLAY = 1
    winning_moves = get_last_solution()
    if winning_moves:
        run_replay(winning_moves, LEVEL_TO_REPLAY)