import pygame
from Game import Game
from settings import *

def human_play(level):
    game = Game(headless=False)
    player = game.reset(level)
    
    running = True
    print("--- Bắt đầu chơi (Điều khiển bằng W-A-S-D hoặc phím mũi tên) ---")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        # Lấy input từ bàn phím và chuyển thành action 0-8
        keys = pygame.key.get_pressed()
        direction = 0
        vy, vx = 0, 0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: vy = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]: vy = -1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: vx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: vx = 1

        if vy == -1: # Up
            if vx == -1: direction = 8
            elif vx == 1: direction = 2
            else: direction = 1
        elif vy == 1: # Down
            if vx == -1: direction = 6
            elif vx == 1: direction = 4
            else: direction = 5
        else: # No vertical
            if vx == -1: direction = 7
            elif vx == 1: direction = 3
            else: direction = 0 # Still
            
        # Cập nhật trạng thái game với hành động của người chơi
        done, cause = game.step(direction)
        
        if done:
            print(f"Trò chơi kết thúc: {cause}")
            pygame.time.wait(2000)
            # Reset lại màn chơi
            player = game.reset(level)

        # Vẽ màn hình
        game.draw(additional_texts=["HUMAN PLAY MODE"])
        game.clock.tick(FPS)

    game.quit()

if __name__ == "__main__":
    LEVEL_TO_PLAY = 1
    human_play(LEVEL_TO_PLAY)