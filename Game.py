import pygame, sys
from settings import *
from Wall import Wall
from Border import Border
from SafeZone import Zone
from EnemyLinear import EnemyLinear
from Player import Player

class Game:
    def __init__(self, headless=False):
        self.headless = headless
        if not self.headless:
            pygame.init()
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption(Title)
            self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        
    def _load_map_data(self, level):
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.zones = pygame.sprite.Group()
        self.borders = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.startx, self.starty, self.target_x, self.target_y = 0, 0, None, None
        self.level = level
        try:
            with open(map_path, 'r', encoding='utf-8') as f: data = f.readlines()
            level_header = f"Level {self.level}"; index = [i for i, line in enumerate(data) if level_header in line][0]
            for y in range(index + 2, index + 33):
                for x in range(0, 41):
                    symbol = data[y][x]; mapx_grid = x; mapy_grid = (y - 2 - index)
                    actual_map_x = mapx_grid * tile_size / 2; actual_map_y = mapy_grid * tile_size / 2
                    if mapy_grid % 2 == 0 or mapx_grid % 2 == 0:
                        if symbol in ['-', '|']: Border(self, actual_map_x, actual_map_y, tile_size, 4, black, 0 if symbol == '-' else 1)
                    else:
                        tile_center_x = (mapx_grid - 1) / 2 * tile_size; tile_center_y = (mapy_grid - 1) / 2 * tile_size
                        if symbol == '1': Wall(self, tile_center_x, tile_center_y, tile_size, lightsteelblue)
                        elif symbol in ['g', 'h', 'j', 's']:
                            Zone(self, tile_center_x, tile_center_y, tile_size, palegreen, symbol)
                            if symbol == 's': self.startx, self.starty = tile_center_x, tile_center_y
                        elif symbol == '2':
                            if self.target_x is None: self.target_x, self.target_y = tile_center_x + tile_size / 2, tile_center_y + tile_size / 2
        except Exception as e: print(f"Lỗi tải map: {e}"); self.quit()
        if self.target_x is None: print("LỖI: Không tìm thấy mục tiêu '2'."); self.quit()
        
        EnemyLinear(self, 22, 4.65, 251, 220, [[251, 220], [549, 220]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 549, 260, [[549, 260], [251, 260]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 251, 300, [[251, 300], [549, 300]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 549, 340, [[549, 340], [251, 340]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 251, 380, [[251, 380], [549, 380]], blue, midnightblue)

    def reset(self, level):
        self._load_map_data(level)
        player = Player(self, self.startx, self.starty, 2, 28, red, maroon, "", 0)
        return player

    def step(self, player, action):
        self.enemies.update()
        player.update_single_step(action)
        if pygame.sprite.spritecollide(player, self.enemies, False):
            return True, 'enemy_hit'
        zones_hit = pygame.sprite.spritecollide(player, self.zones, False)
        if zones_hit:
            player.safe_zone_frames += 1
            for zone in zones_hit:
                if zone.type == 'j':
                    return True, 'win'
        return False, ''

    # <<< SỬA LỖI: Đồng bộ hàm này với cấu trúc dữ liệu mới >>>
    def reset_for_population(self, level, population_moves, change_limit):
        self._load_map_data(level)
        # population_moves giờ là một danh sách các chuỗi
        for moves in population_moves:
            # Gọi Player constructor với đúng các tham số
            Player(self, self.startx, self.starty, 2, 28, red, maroon, moves, change_limit)
        return list(self.players)

    def draw(self, additional_texts=[]):
        if self.headless: return
        self.screen.fill(black)
        for y in range(0, 15):
            for x in range(0, 20): pygame.draw.rect(self.screen, lavender if (x + y) % 2 != 0 else ghostwhite, [x * tile_size, y * tile_size, tile_size, tile_size])
        self.all_sprites.draw(self.screen)
        for border in self.borders: border.draw()
        for i, text in enumerate(additional_texts):
            self.screen.blit(self.font.render(text, True, black), (10, 10 + i * 20))
        pygame.display.update()

    def quit(self):
        pygame.quit()