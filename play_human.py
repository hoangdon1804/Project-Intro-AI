import pygame
from Game import Game
from settings import *

def human_play(level):
    """
    Chế độ chơi cho phép người dùng điều khiển nhân vật bằng bàn phím.
    Phiên bản này đã được sửa lỗi để tuân thủ vòng lặp game tiêu chuẩn.
    """
    game = Game(headless=False)
    player = game.reset(level)
    
    running = True
    print("--- Bắt đầu chơi (Điều khiển bằng W-A-S-D hoặc phím mũi tên) ---")

    while running:
        # 1. XỬ LÝ SỰ KIỆN (INPUT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        # Lấy trạng thái các phím được nhấn để di chuyển mượt mà
        keys = pygame.key.get_pressed()
        vx, vy = 0, 0
        
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy = player.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            vy = -player.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx = -player.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx = player.speed

        # 2. CẬP NHẬT TRẠNG THÁI GAME
        
        # Cập nhật vị trí của người chơi và xử lý va chạm với tường
        # Sử dụng phương thức có sẵn trong lớp Player
        player._wall_collision(vx, vy)
        
        # Cập nhật trạng thái của tất cả kẻ địch
        game.enemies.update()

        # Kiểm tra các điều kiện kết thúc màn chơi
        game_over = False
        cause_of_death = ''

        # a. Kiểm tra va chạm với kẻ địch
        if pygame.sprite.spritecollide(player, game.enemies, False):
            game_over = True
            cause_of_death = 'enemy_hit'

        # b. Kiểm tra có đi vào vùng chiến thắng không
        zones_hit = pygame.sprite.spritecollide(player, game.zones, False)
        if zones_hit:
            for zone in zones_hit:
                if zone.type == 'j':
                    game_over = True
                    cause_of_death = 'win'
                    break 
        
        # Nếu game kết thúc, in thông báo và reset lại màn chơi
        if game_over:
            print(f"Trò chơi kết thúc: {cause_of_death}")
            pygame.time.wait(2000)
            player = game.reset(level)

        # 3. VẼ LÊN MÀN HÌNH
        game.draw(additional_texts=["HUMAN PLAY MODE"])
        
        # Giới hạn tốc độ khung hình (FPS)
        game.clock.tick(FPS)

    game.quit()

if __name__ == "__main__":
    LEVEL_TO_PLAY = 1
    human_play(LEVEL_TO_PLAY)