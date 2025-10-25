from Player import * # Make sure Player imports EnemyLinear, Wall, SafeZone, Border, functions, settings

class Game:
    """
    The game and functions for setting up

    Attributes
    ----------
    screen : surface
        The Pygame window that displays this game
    clock : Clock
        Pygame clock
    all_sprites : sprite group
        A group for all sprites in this game
    players : sprite group
        All players in this game
    player_list : Player list
        List of all players
    player_count : int
        Fixed number of players spawned each generation
    walls : sprite group
        All walls in this game
    zones : sprite group
        All green spaces such as starting/ending and checkpoints in this game
    borders : sprite group
        All bordered lines in this game
    enemies : sprite group
        All enemies in this game
    startx : float
        The x coordinate of the starting tile for this game
    starty : float
        The y coordinate of the starting tile for this game
    checkx : float
        The x coordinate of the ending position of the most recent generation
    checky : float
        The y coordinate of the ending position of the most recent generation
    level : int
        The level of the game, used to find level data in map file
    checkpoints_list : float list list
        Stores the checkpoints' x and y coordinates
    checkpoint_progress : int
        Index of currently targetted checkpoint in 'checkpoints_list' that any player has reached
    generation : int
        Current generation starting from 0
    best_moves_for_rewind : str
        A string of the highest scored moves from the previous generation (trimmed)
    best_moves_num_for_rewind : int
        Length of 'best_moves_for_rewind'
    rewind : bool
        True if the game is rewinding its best moves from each generation. Occurs at the end of each generation

    Methods
    -------
    new(level : int) -> None
        Reads from the map file and creates all objects relating to the map
    create_initial_players(number : int) -> None
        Creates multiple new players at a time for the first generation
    new_generation_players(None) -> None
        Creates multiple new players for subsequent generations, inheriting best_moves
    end_gen(None) -> None
        Sorts the ended generation's moves, begins rewind phase and then makes the next generation
    run(None) -> None
        Primary loop to update and draw game contents
    update(None) -> None
        Updates all game sprites
    draw_map(None) -> None
        Draws map grid and squares
    draw(None) -> None
        Draws all game sprites
    events(None) -> None
        Listens for any events such as keypresses
    quit(None) ->
        Closes the Pygame window and quits the program

    """

    def __init__(self):
        """
        Constructor to build a new Game

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(Title)

        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 1) # Allows continuous key presses

        # Counter for generation rewinding
        self.tick = 0
        self.player_count = 100 # Fixed number of players per generation

    def new(self, level):
        """
        Reads from the map file and creates all objects relating to the map

        Parameters
        ----------
        level : int
            The level of this game with its specific map data in the map file

        Returns
        -------
        None

        """

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.player_list = []
        self.walls = pygame.sprite.Group()
        self.zones = pygame.sprite.Group()
        self.borders = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Start position will be read from map file
        self.startx = 0
        self.starty = 0
        self.checkx = 0 # This will be updated to startx, starty initially
        self.checky = 0

        self.level = level

        # Checkpoints for AI pathing
        self.checkpoints_list = []
        for _ in range(10): # Initialize with enough empty lists for checkpoints
            self.checkpoints_list.append([])
        #
        self.checkpoint_progress = 0 # Tracks the highest checkpoint reached by any player

        # Generations
        self.generation = 0
        self.best_moves_for_rewind = '' # The best moves string for the rewinder player
        self.best_moves_num_for_rewind = 0
        self.rewind = False

        # Map maker
        try:
            with open(map_path, 'r') as file:
                data = file.readlines()
        except FileNotFoundError:
            print(f"Error: map file not found at {map_path}")
            self.quit()
            return

        # The line number of the level in the map file
        try:
            index = data.index(">>>>>>>>>>>>>>>> Level " + str(self.level) + "\n")
        except ValueError:
            print(f"Error: Level {self.level} not found in map file.")
            self.quit()
            return

        # Walls ; Green Space ; borders
        for y in range(index + 2, index + 33): # Assuming map data starts at index + 2 and has 31 rows
            for x in range(0, 41): # Assuming 41 columns
                symbol = data[y][x]
                mapx_grid = x # Grid x for border logic
                mapy_grid = (y - 2 - index) # Grid y for border logic

                # Coordinates on the actual game window
                actual_map_x = mapx_grid * tile_size / 2
                actual_map_y = mapy_grid * tile_size / 2

                if mapy_grid % 2 == 0 or mapx_grid % 2 == 0: # Check if it's a border position
                    # Symbols on the sides of tiles (borders)
                    if symbol == '-' or symbol == '|':
                        # Align: 0 for horizontal ('-'), 1 for vertical ('|')
                        align = 0 if symbol == '-' else 1
                        Border(self, actual_map_x, actual_map_y, tile_size, 4, black, align)
                else:
                    # Symbols on the centres of tiles (walls, zones)
                    # Adjust mapx, mapy for tile centers
                    tile_center_x = (mapx_grid - 1) / 2 * tile_size
                    tile_center_y = (mapy_grid - 1) / 2 * tile_size # mapy_grid is relative, so (y - 2 - index) - 1

                    if symbol == '1':
                        Wall(self, tile_center_x, tile_center_y, tile_size, lightsteelblue)
                    elif symbol in ['g', 'h', 'j', 's']:
                        Zone(self, tile_center_x, tile_center_y, tile_size, palegreen, symbol)
                        if symbol == 's': # Starting tile
                            self.startx = tile_center_x
                            self.starty = tile_center_y
                            self.checkx = self.startx # Initial checkpoint for next generation
                            self.checky = self.starty # Initial checkpoint for next generation

        # Coins (Currently not implemented, but map data expects it)
        # for y in range (index + 34, index + 65):
        #     for x in range(0, 41):
        #         symbol = data[y][x]

        # Checkpoints
        for y in range(index + 66, index + 81): # Assuming checkpoint data starts at index + 66 and has 15 rows
            # Each line has checkpoints for one index, e.g., line 0 for checkpoint 0, line 1 for checkpoint 1
            line_data = data[y].strip()
            if line_data: # If the line is not empty
                parts = line_data.split(';')
                for part in parts:
                    if ':' in part and ',' in part: # New format: "idx:x,y"
                        try:
                            # Split into checkpoint index and coordinates
                            idx_str, coords_str = part.split(':', 1)
                            cp_idx = int(idx_str.strip())
                            x_coord, y_coord = map(int, coords_str.strip().split(','))
                            
                            # Store in checkpoints_list
                            # Make sure checkpoints_list is large enough
                            while len(self.checkpoints_list) <= cp_idx:
                                self.checkpoints_list.append([])
                            
                            self.checkpoints_list[cp_idx].extend([x_coord, y_coord])
                        except ValueError as e:
                            print(f"Warning: Could not parse checkpoint line '{part}' in map file. Error: {e}")
                    else: # Old format: "x,y" (implicitly for current line index)
                        # Fix: If old format is used, cp_idx should be derived from loop index
                        cp_idx = y - (index + 66)
                        try:
                            coords = [int(val) for val in part.split(',')]
                            if len(coords) == 2:
                                while len(self.checkpoints_list) <= cp_idx:
                                    self.checkpoints_list.append([])
                                self.checkpoints_list[cp_idx].extend(coords)
                            else:
                                print(f"Warning: Invalid coordinate format '{part}' for checkpoint in map file. Expected 'x,y'.")
                        except ValueError as e:
                            print(f"Warning: Could not parse old format checkpoint line '{part}' in map file. Error: {e}")

        # Filter out empty checkpoint lists that might be created by range but not filled
        self.checkpoints_list = [cp for cp in self.checkpoints_list if cp]
        print(f"Loaded {len(self.checkpoints_list)} checkpoints.")
        for i, cp in enumerate(self.checkpoints_list):
            print(f"Checkpoint {i}: {cp}")


        # Create enemies (Example enemies, adjust as needed for your level)
        EnemyLinear(self, 22, 4.65, 251, 220, [[251, 220], [549, 220]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 549, 260, [[549, 260], [251, 260]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 251, 300, [[251, 300], [549, 300]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 549, 340, [[549, 340], [251, 340]], blue, midnightblue)
        EnemyLinear(self, 22, 4.65, 251, 380, [[251, 380], [549, 380]], blue, midnightblue)

    def create_initial_players(self):
        """
        Creates the first generation of players (all 'random' control)

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        self.player_list = [] # Clear any previous players
        for i in range(self.player_count):
            player = Player(self, 'random', self.startx, self.starty, 2, 28, red, maroon)
            self.player_list.append(player)
        print(f"Generation {self.generation}: Created {len(self.player_list)} initial random players.")


    def new_generation_players(self):
        """
        Creates a new generation of players. Each player inherits the trimmed best_moves
        from the previous generation and then moves randomly.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        self.player_list = [] # Clear previous generation players
        for i in range(self.player_count):
            player = Player(self, 'hybrid', self.checkx, self.checky, 2, 28, red, maroon)
            player.inherited_moves = self.best_moves_for_rewind # Assign the trimmed best_moves
            self.player_list.append(player)
        print(f"Generation {self.generation}: Created {len(self.player_list)} hybrid players, inheriting {len(self.best_moves_for_rewind)} steps.")


    def end_gen(self):
        """
        Sorts the ended generation's moves, begins rewind phase and then makes the next generation

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        print(f"Ending Generation {self.generation}...")

        # End the generation marker
        with open(moves_path, 'a') as file:
            file.write("END OF GENERATION " + str(self.generation) + "\n")

        # Sort moves based on their scores (using Python's built-in sort)
        # The number of lines for this generation is player_count (moves) + 1 (END OF GEN marker)
        start_line_index = self.generation * (self.player_count + 1)
        end_line_index = start_line_index + self.player_count - 1
        
        # Ensure there are enough lines to sort
        try:
            python_sort(start_line_index, end_line_index)
        except IndexError:
            print(f"Warning: Not enough player moves to sort in generation {self.generation}. (Expected {self.player_count} players, found less?)")
            # If sorting fails, just proceed without a new best_move for this gen
            self.best_moves_for_rewind = ''
            self.best_moves_num_for_rewind = 0
            self.generation += 1
            # Reset enemies for next gen
            for enemy in self.enemies:
                enemy.reset()
            self.rewind = True
            # Create a dummy rewinder if no best_move to simulate ending
            self.rewinder = Player(self, 'random', self.startx, self.starty, 2, 28, lime, black)
            self.player_list.append(self.rewinder) # Add to list so it gets updated
            return


        with open(moves_path, 'r') as file:
            data = file.readlines()

        # Add best moves from this generation to best_moves_for_rewind string
        # The best move is at the end of the sorted cluster
        moves_line_index = start_line_index + self.player_count - 1 # Last line of the sorted cluster
        
        full_best_moves_current_gen = '' # Initialize before try block

        if moves_line_index < len(data):
            moves_line = data[moves_line_index]
            # Extract only the moves string
            try:
                # Find "Moves: " and get substring after it
                moves_start_index = moves_line.find("Moves: ")
                if moves_start_index != -1:
                    full_best_moves_current_gen = moves_line[moves_start_index + len("Moves: "):].strip()
                else:
                    # If "Moves: " is not found, treat as empty or invalid
                    print(f"Warning: 'Moves:' not found in best move line: {moves_line.strip()}")
            except Exception as e:
                print(f"Error parsing best move line: {e} in line: {moves_line.strip()}")
                full_best_moves_current_gen = ''
        else:
            print(f"Warning: Best move line index {moves_line_index} out of bounds for data length {len(data)}. No best moves for this gen.")

        # Cắt giảm các bước cuối của full_best_moves_current_gen
        cut_percentage = 0.10  # Cắt 10% cuối cùng
        min_cut_steps = 10     # Tối thiểu 10 bước

        num_to_cut = max(min_cut_steps, int(len(full_best_moves_current_gen) * cut_percentage))
        
        # Đảm bảo không cắt hết moves, ít nhất phải còn 1 bước hoặc tùy bạn
        if len(full_best_moves_current_gen) > num_to_cut:
            self.best_moves_for_rewind = full_best_moves_current_gen[:-num_to_cut]
        elif len(full_best_moves_current_gen) > 0: # If it's too short but not empty, just cut 1 or 2
             self.best_moves_for_rewind = full_best_moves_current_gen[:-1] if len(full_best_moves_current_gen) > 1 else ''
        else:
            self.best_moves_for_rewind = '' # No moves to inherit

        self.best_moves_num_for_rewind = len(self.best_moves_for_rewind)
        print(f"Best moves from Gen {self.generation} (trimmed): {self.best_moves_for_rewind}")
        print(f"Length of trimmed best moves: {self.best_moves_num_for_rewind}")

        # Update most recent checkpoint progress
        # This is already handled by individual players updating self.game.checkpoint_progress

        self.generation += 1
        self.rewind = True
        print(f"Starting Generation {self.generation} rewind phase.")

        # Player to replay best moves up to next generation
        self.rewinder = Player(self, 'random', self.startx, self.starty, 2, 28, lime, black) # Rewinder is a special player
        self.player_list.append(self.rewinder) # Add to list so it gets updated

        # Reset all enemy positions
        for enemy in self.enemies:
            enemy.reset()

    def run(self):
        """
        Primary loop to update and draw game contents

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        # game loop - set self.run = False to end the game
        self.run = True
        while self.run:
            # dt is the time between each frame in seconds
            self.dt = self.clock.tick(FPS) / 1000
            # print(self.dt)

            self.events()

            # New generation logic
            if not self.rewind and len(self.player_list) == 0:
                self.end_gen()
            elif self.rewind and len(self.player_list) == 0: # If rewinder somehow died without creating new gen
                 print("Warning: Rewinder died prematurely without creating new generation. Restarting generation process.")
                 self.rewind = False
                 self.tick = 0
                 self.new_generation_players() # Attempt to create players directly

            # Speed up game
            for i in range(zoom):
                self.update()
            self.draw()

    def update(self):
        """
        Updates all game sprites

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        # update sprites
        self.all_sprites.update()

    def draw_map(self):
        """
        Draws map grid and squares

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        for y in range(0, 15):
            for x in range(0, 20):
                fill = lavender
                # Checkerboard pattern
                if (x + y) % 2 == 0:
                    fill = ghostwhite
                # Draw grid squares
                pygame.draw.rect(self.screen, fill, [0 + x * tile_size, 0 + y * tile_size, tile_size, tile_size])

    def draw(self):
        """
        Draws all game sprites

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        self.screen.fill(black)
        self.draw_map()
        self.all_sprites.draw(self.screen)

        for border in self.borders:
            border.draw()

        # Display generation info
        font = pygame.font.Font(None, 24)
        text_gen = font.render(f"Generation: {self.generation}", True, black)
        text_players = font.render(f"Players Alive: {len(self.player_list) - (1 if self.rewind else 0)}", True, black)
        text_checkpoint = font.render(f"Checkpoint Progress: {self.checkpoint_progress}", True, black)
        self.screen.blit(text_gen, (screen_width - 180, 10))
        self.screen.blit(text_players, (screen_width - 180, 30))
        self.screen.blit(text_checkpoint, (screen_width - 180, 50))


        pygame.display.update()

    def events(self):
        """
        Listens for any events such as keypresses

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        # All events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()

    def quit(self):
        """
        Closes the Pygame window and quits the program

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        pygame.quit()
        sys.exit()