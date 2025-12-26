import pygame
import sys
from settings import *
from sprites import Player, Enemy, Coin
from level_manager import LevelManager

class Game:
    def __init__(self, start_level=0):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("The World's Hardest Game - Python")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        
        self.lvl = start_level
        self.deaths = 0
        self.angle = 0
        self.checkpoint_pos = None
        self.load_level()

    def load_level(self):
        data = LevelManager.get_config(self.lvl)
        # Hệ thống checkpoint
        if self.checkpoint_pos is None:
            self.checkpoint_pos = data["player_pos"]
            
        self.player = Player(*self.checkpoint_pos)
        self.enemies = [Enemy(e, self.lvl) for e in data["enemies"]]
        self.coins = [Coin(c[0], c[1]) for c in data["coins"]]
        self.finish_rect = data["finish_rect"]
        self.checkpoints = data.get("checkpoints", [])
        self.walls_pts = data["walls_pts"]
        self.grid_cells = data["grid_cells"]
        self.coins_req = data["coins_req"]
        self.current_coins = 0
        
        # Tạo mask tường để va chạm pixel
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        if self.walls_pts:
            pygame.draw.polygon(surf, BLACK, self.walls_pts, WALL_WIDTH)
        self.wall_mask = pygame.mask.from_surface(surf)

    def update(self):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * PLAYER_SPEED
        if dx != 0 or dy != 0: self.player.move(dx, dy, self.wall_mask)

        # Cập nhật enemy và check chết
        self.angle += 0.05
        for en in self.enemies:
            en.update(self.angle)
            if self.player.rect.inflate(-12, -12).collidepoint(en.x, en.y):
                self.deaths += 1
                self.load_level()
                return

        # Check ăn coin
        for c in self.coins[:]:
            if self.player.rect.colliderect(c.rect):
                self.coins.remove(c)
                self.current_coins += 1

        # Check checkpoint
        for cp in self.checkpoints:
            if cp.colliderect(self.player.rect):
                new_cp = (cp.x + (cp.width-PLAYER_SIZE)//2, cp.y + (cp.height-PLAYER_SIZE)//2)
                if self.checkpoint_pos != new_cp:
                    self.checkpoint_pos = new_cp

        # Check về đích
        if self.finish_rect.colliderect(self.player.rect) and self.current_coins >= self.coins_req:
            self.lvl += 1
            self.checkpoint_pos = None
            self.load_level()

    def draw(self):
        # Màu nền thay đổi theo độ khó
        color = BG_L_BLUE if self.lvl < 19 else BG_PURPLE
        self.screen.fill(color)

        # 1. Vẽ vùng đặc biệt (Start/Checkpoint/Finish)
        if self.lvl == 0: pygame.draw.rect(self.screen, RED, (100, 200, 150, 300))
        elif self.lvl == 1: pygame.draw.rect(self.screen, RED, (100, 300, 150, 100))
        for cp in self.checkpoints: pygame.draw.rect(self.screen, GREEN_CHECKPOINT, cp)
        pygame.draw.rect(self.screen, GREEN_FINISH, self.finish_rect)

        # 2. VẼ Ô LƯỚI (GRID) - Vẽ trước tường để không đè lên viền
        for cell in self.grid_cells:
            pygame.draw.rect(self.screen, WHITE, (cell[0], cell[1], 50, 50))

        # 3. Vẽ Tường
        if self.walls_pts:
            pygame.draw.polygon(self.screen, BLACK, self.walls_pts, WALL_WIDTH)

        # 4. Vẽ Entities
        for c in self.coins: c.draw(self.screen)
        for en in self.enemies: en.draw(self.screen)
        self.player.draw(self.screen)
        
        # 5. Vẽ UI
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, 40))
        ui_txt = f"LEVEL: {self.lvl + 1} / 30    COINS: {self.current_coins}/{self.coins_req}    DEATHS: {self.deaths:04}"
        self.screen.blit(self.font.render(ui_txt, True, WHITE), (20, 8))
        
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            self.update(); self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    # Thay đổi level bắt đầu ở đây
    game = Game(start_level=7) 
    game.run()