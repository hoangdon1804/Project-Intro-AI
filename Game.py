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
        self.startx, self.starty = 0, 0
        self.checkpoints = []
        self.target_j_pos = None
        self.level = level
        
        raw_checkpoints = []
        try:
            with open(map_path, 'r', encoding='utf-8') as f: data = f.readlines()
            level_header = f"Level {self.level}"; index = [i for i, line in enumerate(data) if level_header in line][0]
            for y in range(index + 2, index + 33):
                for x in range(0, 41):
                    symbol = data[y][x]
                    mapx_grid = x; mapy_grid = (y - 2 - index)
                    actual_map_x = mapx_grid * tile_size / 2; actual_map_y = mapy_grid * tile_size / 2
                    
                    if mapy_grid % 2 == 0 or mapx_grid % 2 == 0:
                        if symbol in ['-', '|']: Border(self, actual_map_x, actual_map_y, tile_size, 4, black, 0 if symbol == '-' else 1)
                    else:
                        tile_center_x = (mapx_grid - 1) / 2 * tile_size; tile_center_y = (mapy_grid - 1) / 2 * tile_size
                        
                        # ================================================================= #
                        # === THAY ĐỔI LOGIC ĐỌC CHECKPOINT ĐỂ HỖ TRỢ SỐ LỚN HƠN 9 === #
                        # ================================================================= #
                        
                        is_checkpoint = False
                        checkpoint_id = 0

                        if symbol.isdigit() and symbol != '1':
                            is_checkpoint = True
                            checkpoint_id = int(symbol)
                        # Nếu ký tự là chữ cái thường (a-z), chuyển nó thành số (a=10, b=11, ...)
                        elif symbol.isalpha() and symbol.islower() and symbol not in ['g', 'h', 's', 'j']:
                            is_checkpoint = True
                            # Dùng mã ASCII để tính toán: ord('a') - ord('a') + 10 = 10
                            checkpoint_id = ord(symbol) - ord('a') + 10

                        if symbol == '1': 
                            Wall(self, tile_center_x, tile_center_y, tile_size, lightsteelblue)
                        
                        elif is_checkpoint:
                            color = yellow
                            raw_checkpoints.append({'id': checkpoint_id, 'x': tile_center_x + tile_size / 2, 'y': tile_center_y + tile_size / 2})
                            Zone(self, tile_center_x, tile_center_y, tile_size, color, str(checkpoint_id)) # Lưu type là số
                        
                        elif symbol in ['g', 'h', 's', 'j']:
                            color = palegreen
                            if symbol == 's': 
                                self.startx, self.starty = tile_center_x, tile_center_y
                            elif symbol == 'j': 
                                self.target_j_pos = {'x': tile_center_x + tile_size / 2, 'y': tile_center_y + tile_size / 2}
                            Zone(self, tile_center_x, tile_center_y, tile_size, color, symbol)

        except Exception as e: print(f"Lỗi tải map: {e}"); self.quit()

        raw_checkpoints.sort(key=lambda c: c['id'])
        self.checkpoints = [{'id': 1, 'x': self.startx + tile_size/2, 'y': self.starty + tile_size/2}] + raw_checkpoints
        
        if len(self.checkpoints) < 2: print("CẢNH BÁO: Map không có checkpoint được đánh số. AI sẽ nhắm thẳng đến 'j'.")
        if not self.target_j_pos: print("LỖI: Map phải có một điểm chiến thắng 'j'."); self.quit()
        
        EnemyLinear(self, 22, 2.50, 251, 220, [[251, 220], [549, 220]], blue, midnightblue)
        EnemyLinear(self, 22, 2.50, 549, 260, [[549, 260], [251, 260]], blue, midnightblue)
        EnemyLinear(self, 22, 2.50, 251, 300, [[251, 300], [549, 300]], blue, midnightblue)
        EnemyLinear(self, 22, 2.50, 549, 340, [[549, 340], [251, 340]], blue, midnightblue)
        EnemyLinear(self, 22, 2.50, 251, 380, [[251, 380], [549, 380]], blue, midnightblue)

    def reset(self, level):
        self._load_map_data(level)
        player = Player(self, self.startx, self.starty, 2, 28, red, maroon, "", 9999)
        return player

    def step(self, player, action):
        player.update_single_step(action)
        self.enemies.update()
        if pygame.sprite.spritecollide(player, self.enemies, False): return True, 'enemy_hit'
        zones_hit = pygame.sprite.spritecollide(player, self.zones, False)
        if zones_hit:
            player.safe_zone_frames += 1
            for zone in zones_hit:
                if zone.type == 'j':
                    if player.last_checkpoint_reached == self.checkpoints[-1]['id']: return True, 'win'
        return False, ''

    def reset_for_population(self, level, population_moves, max_move_limit):
        self._load_map_data(level)
        for moves in population_moves:
            Player(self, self.startx, self.starty, 2, 28, red, maroon, moves, max_move_limit)
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