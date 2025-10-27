from Player import * # Make sure Player imports EnemyLinear, Wall, SafeZone, Border, functions, settings

class Game:
    """
    The game and functions for setting up
    """

    def __init__(self):
        """
        Constructor to build a new Game
        """
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(Title)
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 1)
        self.tick = 0
        self.player_count = 1000

    def new(self, level):
        """
        Reads from the map file and creates all objects relating to the map
        """
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.player_list = []
        self.walls = pygame.sprite.Group()
        self.zones = pygame.sprite.Group()
        self.borders = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Game state attributes
        self.startx = 0
        self.starty = 0
        self.checkx = 0
        self.checky = 0
        self.level = level
        self.target_x = None
        self.target_y = None

        # <<< THAY ĐỔI: Lưu trữ top 5 moves thay vì chỉ 1 >>>
        self.top_5_moves = []
        # Thuộc tính này vẫn giữ lại để điều khiển rewinder
        self.best_move_for_rewind = ''
        self.best_move_num_for_rewind = 0
        # <<< KẾT THÚC THAY ĐỔI >>>
        
        self.generation = 0
        self.rewind = False

        # Map maker
        try:
            with open(map_path, 'r') as file:
                data = file.readlines()
        except FileNotFoundError:
            print(f"Error: map file not found at {map_path}")
            self.quit()
            return

        try:
            index = data.index(">>>>>>>>>>>>>>>> Level " + str(self.level) + "\n")
        except ValueError:
            print(f"Error: Level {self.level} not found in map file.")
            self.quit()
            return

        # Đọc map layout
        for y in range(index + 2, index + 33):
            for x in range(0, 41):
                symbol = data[y][x]
                mapx_grid = x
                mapy_grid = (y - 2 - index)
                actual_map_x = mapx_grid * tile_size / 2
                actual_map_y = mapy_grid * tile_size / 2
                if mapy_grid % 2 == 0 or mapx_grid % 2 == 0:
                    if symbol == '-' or symbol == '|':
                        align = 0 if symbol == '-' else 1
                        Border(self, actual_map_x, actual_map_y, tile_size, 4, black, align)
                else:
                    tile_center_x = (mapx_grid - 1) / 2 * tile_size
                    tile_center_y = (mapy_grid - 1) / 2 * tile_size
                    if symbol == '1':
                        Wall(self, tile_center_x, tile_center_y, tile_size, lightsteelblue)
                    elif symbol in ['g', 'h', 'j', 's']:
                        Zone(self, tile_center_x, tile_center_y, tile_size, palegreen, symbol)
                        if symbol == 's':
                            self.startx = tile_center_x
                            self.starty = tile_center_y
                            self.checkx = self.startx
                            self.checky = self.starty
                    elif symbol == '2':
                        if self.target_x is None:
                            self.target_x = tile_center_x + tile_size / 2
                            self.target_y = tile_center_y + tile_size / 2
                            print(f"Target '2' found at coordinates: ({self.target_x}, {self.target_y})")

        if self.target_x is None:
            print("FATAL ERROR: Target '2' not found in map file. AI has no goal.")
            self.quit()
            return

        # Create enemies
        
        EnemyLinear(self, 22, 4.65, 251, 220, [[251, 220], [549, 220]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 549, 260, [[549, 260], [251, 260]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 251, 300, [[251, 300], [549, 300]], blue, midnightblue)
        '''
        EnemyLinear(self, 22, 4.65, 549, 340, [[549, 340], [251, 340]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 251, 380, [[251, 380], [549, 380]], blue, midnightblue)
        '''
    def create_initial_players(self):
        self.player_list = []
        for i in range(self.player_count):
            player = Player(self, 'random', self.startx, self.starty, 2, 28, red, maroon)
            self.player_list.append(player)
        print(f"Generation {self.generation}: Created {len(self.player_list)} initial random players.")

    def new_generation_players(self):
        """
        <<< THAY ĐỔI: Tạo thế hệ mới dựa trên top 5 moves >>>
        """
        self.player_list = []
        if not self.top_5_moves:
            print(f"Warning: No best moves found from previous generation. Creating random players.")
            self.create_initial_players()
            return

        players_per_move = self.player_count // len(self.top_5_moves)

        for i in range(self.player_count):
            # Chọn move string dựa trên index của player
            move_index = min(i // players_per_move, len(self.top_5_moves) - 1)
            inherited_moves = self.top_5_moves[move_index]
            
            player = Player(self, 'hybrid', self.checkx, self.checky, 2, 28, red, maroon)
            player.inherited_moves = inherited_moves
            self.player_list.append(player)
            
        print(f"Generation {self.generation}: Created {len(self.player_list)} players inheriting from top {len(self.top_5_moves)} moves.")

    def end_gen(self):
        """
        <<< THAY ĐỔI: Tìm top 5 moves và cắt 5 bước cuối >>>
        """
        print(f"Ending Generation {self.generation}...")
        with open(moves_path, 'a') as file:
            file.write("END OF GENERATION " + str(self.generation) + "\n")

        start_line_index = self.generation * (self.player_count + 1)
        end_line_index = start_line_index + self.player_count - 1
        
        try:
            python_sort(start_line_index, end_line_index)
        except IndexError:
            # Xử lý lỗi nếu không đủ dữ liệu để sort
            self.top_5_moves = []
            self.best_move_for_rewind = ''
            self.best_move_num_for_rewind = 0
            # ... (phần còn lại của xử lý lỗi giữ nguyên)
            return

        with open(moves_path, 'r') as file:
            data = file.readlines()

        # Lấy 5 dòng cuối cùng của cluster đã sort
        num_top_moves = 5
        top_moves_start_index = max(start_line_index, end_line_index - num_top_moves + 1)
        top_moves_lines = data[top_moves_start_index : end_line_index + 1]
        top_moves_lines.reverse() # Đảo ngược để dòng tốt nhất ở index 0

        self.top_5_moves = []
        for line in top_moves_lines:
            try:
                moves_start_index = line.find("Moves: ")
                if moves_start_index != -1:
                    full_moves = line[moves_start_index + len("Moves: "):].strip()
                    
                    # Cắt 10 bước cuối
                    if len(full_moves) > 10:
                        trimmed_moves = full_moves[:-10]
                    else:
                        trimmed_moves = full_moves
                    
                    self.top_5_moves.append(trimmed_moves)
            except Exception as e:
                print(f"Error parsing a best move line: {e}")

        if not self.top_5_moves:
            print("Warning: Could not extract any best moves for the next generation.")
            self.best_move_for_rewind = ''
            self.best_move_num_for_rewind = 0
        else:
            # Move tốt nhất cho rewinder là move đầu tiên trong danh sách
            self.best_move_for_rewind = self.top_5_moves[0]
            self.best_move_num_for_rewind = len(self.best_move_for_rewind)
            print(f"Extracted top {len(self.top_5_moves)} moves for next generation.")
            print(f"Best move for rewinder has {self.best_move_num_for_rewind} steps.")

        self.generation += 1
        self.rewind = True
        print(f"Starting Generation {self.generation} rewind phase.")

        self.rewinder = Player(self, 'random', self.startx, self.starty, 2, 28, lime, black)
        self.player_list.append(self.rewinder)

        for enemy in self.enemies:
            enemy.reset()

    def run(self):
        self.run = True
        while self.run:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.rewind and len(self.player_list) == 0:
                self.end_gen()
            elif self.rewind and len(self.player_list) == 0:
                 self.rewind = False
                 self.tick = 0
                 self.new_generation_players()
            for i in range(zoom):
                self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()

    def draw_map(self):
        for y in range(0, 15):
            for x in range(0, 20):
                fill = lavender
                if (x + y) % 2 == 0:
                    fill = ghostwhite
                pygame.draw.rect(self.screen, fill, [0 + x * tile_size, 0 + y * tile_size, tile_size, tile_size])

    def draw(self):
        self.screen.fill(black)
        self.draw_map()
        self.all_sprites.draw(self.screen)
        for border in self.borders:
            border.draw()
        font = pygame.font.Font(None, 24)
        text_gen = font.render(f"Generation: {self.generation}", True, black)
        text_players = font.render(f"Players Alive: {len(self.player_list) - (1 if self.rewind else 0)}", True, black)
        self.screen.blit(text_gen, (screen_width - 180, 10))
        self.screen.blit(text_players, (screen_width - 180, 30))
        pygame.display.update()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()

    def quit(self):
        pygame.quit()
        sys.exit()