import pygame
from settings import *

class LevelManager:
    @staticmethod
    def get_config(lvl):
        config = {
            "player_pos": (160, 335),
            "enemies": [], "coins": [], "walls_pts": [], "grid_cells": [],
            "finish_rect": pygame.Rect(0,0,0,0), "checkpoints": [], "coins_req": 0
        }

        if lvl == 0:
            config["enemies"] = [[325,325,6,0], [325,425,6,0], [775,275,-6,0], [775,375,-6,0]]
            config["walls_pts"] = [(250,450), (250,200), (100,200), (100,500), (350,500), (350,450), (800,450), (800,250), (850,250), (850,500), (1000,500), (1000,200), (750,200), (750,250), (300,250), (300,450)]
            config["finish_rect"] = pygame.Rect(850, 200, 150, 300)
            # Grid Level 0
            for x in range(350, 800, 100): config["grid_cells"] += [(x,250), (x,350)]
            for x in range(300, 750, 100): config["grid_cells"] += [(x,300), (x,400)]
            config["grid_cells"] += [(250,450), (800,200)]

        elif lvl == 1:
            config["enemies"] = [[x, 226, 0, 6] for x in range(275, 875, 100)] + [[x, 474, 0, -6] for x in range(325, 925, 100)]
            config["walls_pts"] = [(250,400), (100,400), (100,300), (250,300), (250,200), (850,200), (850,300), (1000,300), (1000,400), (850,400), (850,500), (250,500)]
            config["finish_rect"] = pygame.Rect(850, 300, 150, 100)
            config["coins"] = [[550, 350]]; config["coins_req"] = 1
            # Grid Level 1
            for x in range(300, 850, 100): config["grid_cells"] += [(x, 200), (x, 300), (x, 400)]
            for x in range(250, 800, 100): config["grid_cells"] += [(x, 250), (x, 350), (x, 450)]

        elif lvl == 2:
            MOVE_SPEED = 3.0 
            
            config["enemies"] = [
                [526, 275, MOVE_SPEED, 0],   
                [574, 275, MOVE_SPEED, 0],   
                [625, 275, 0, MOVE_SPEED],   
                [625, 326, 0, MOVE_SPEED],   
                [625, 374, 0, MOVE_SPEED],   
                [625, 425, -MOVE_SPEED, 0],  
                [574, 425, -MOVE_SPEED, 0],  
                [526, 425, -MOVE_SPEED, 0],  
                [475, 425, 0, -MOVE_SPEED],  
                [475, 374, 0, -MOVE_SPEED]
            ]
            config["player_pos"] = (550-15, 350-15)
            config["finish_rect"] = pygame.Rect(500, 300, 100, 100)
            config["walls_pts"] = [(500,250), (650,250), (650,450), (450,450), (450,200), (500,200)]
            config["coins"] = [[475, 225]]; config["coins_req"] = 1
            # Grid Level 2
            config["grid_cells"] = [(450,250), (450,350), (550,250), (600,300), (500,400), (600,400)]

        elif lvl == 3:
            config["player_pos"] = (550-15, 125-15)
            config["finish_rect"] = pygame.Rect(200, 350, 150, 100)
            config["coins"] = [[550, 250], [700, 400], [550, 550]]; config["coins_req"] = 3
            center = (550, 400)
            for r in [175, 140, 105, 70, 35]:
                for off in [0, 1.6, 3.2, 4.8]: config["enemies"].append([center[0], center[1], r, off])
            config["walls_pts"] = [(500,200), (500,50), (600,50), (600,200), (650,200), (650,250), (700,250), (700,300), (750,300), (750,500), (700,500), (700,550), (650,550), (650,600), (450,600), (450,550), (400,550), (400,500), (350,500), (350,450), (200,450), (200,350), (350,350), (350,300), (400,300), (400,250), (450,250), (450,200)]
            # Grid Level 3 (Checkerboard loops)
            for x in range(500,650,100): config["grid_cells"].append((x,200))
            for x in range(450,700,100): config["grid_cells"].append((x,250))
            for x in range(400,750,100): config["grid_cells"].append((x,300))
            for x in range(350,700,100): config["grid_cells"].append((x,350))
            for x in range(400,750,100): config["grid_cells"].append((x,400))
            for x in range(350,700,100): config["grid_cells"].append((x,450))
            for x in range(400,650,100): config["grid_cells"].append((x,500))
            for x in range(450,600,100): config["grid_cells"].append((x,550))

        elif lvl == 4:
            config["player_pos"] = (150-15, 125-15)
            config["finish_rect"] = pygame.Rect(650, 300, 50, 100)
            config["checkpoints"] = [pygame.Rect(900, 100, 50, 50), pygame.Rect(100, 200, 50, 50)]
            center = (550, 350)
            for r in [375, 275, 175, 75]:
                for off in [0, 1.6, 3.2, 4.8]: config["enemies"].append([center[0], center[1], r, off])
            config["walls_pts"] = [(100,150), (100,100), (950,100), (950,150), (900,150), (900,600), (200,600), (200,250), (100,250), (100,200), (800,200), (800,500), (300,500), (300,300), (700,300), (700,400), (400,400), (400,350), (350,350), (350,450), (750,450), (750,250), (250,250), (250,550), (850,550), (850,150)]
            # Grid Level 4
            for x in range(200,850,100): config["grid_cells"].append((x,100))
            for y in range(150,600,100): config["grid_cells"].append((850,y))
            for x in range(250,800,100): config["grid_cells"].append((x,550))
            for y in range(200,600,100): config["grid_cells"].append((200,y))
            for x in range(300,800,100): config["grid_cells"].append((x,200))
            for y in range(250,500,100): config["grid_cells"].append((750,y))
            for x in range(350,750,100): config["grid_cells"].append((x,450))
            for y in range(300,450,100): config["grid_cells"].append((300,y))
            for x in range(400,650,100): config["grid_cells"].append((x,300))
            for x in range(450,600,100): config["grid_cells"].append((x,350))

        elif lvl == 5:
            config["player_pos"] = (150-15, 150-15)
            config["finish_rect"] = pygame.Rect(100, 500, 100, 100)
            config["checkpoints"] = [pygame.Rect(800, 300, 200, 100)]
            config["coins"] = [[225,425], [425,425], [625,425], [825,425]]
            config["coins_req"] = 4
            config["walls_pts"] = [(100,100), (1000,100), (1000,600), (100,600), (100,500), (200,500), (200,400), (800,400), (800,300), (200,300), (200,200), (100,200)]
            for x in range(200,950,100): config["grid_cells"] += [(x,100), (x,200), (x,400), (x,500)]
            for x in range(250,1000,100): config["grid_cells"] += [(x,150), (x,250), (x,450), (x,550)]
            # Enemies: 8 tâm xoay và các chấm xoay quanh
            centers = [(300,200), (500,200), (700,200), (900,200), (300,500), (500,500), (700,500), (900,500)]
            for cx, cy in centers:
                config["enemies"].append([cx, cy, 0, 0]) # Chấm tâm đứng yên
                for r in [86, 43]:
                    for off in [0, 1.6, 3.2, 4.8]: config["enemies"].append([cx, cy, r, off])

        elif lvl == 6:
            config["player_pos"] = (175-15, 350-15)
            config["finish_rect"] = pygame.Rect(850, 300, 150, 100)
            config["walls_pts"] = [(100,300), (250,300), (250,150), (850,150), (850,300), (1000,300), (1000,400), (850,400), (850,550), (250,550), (250,400), (100,400)]
            config["coins"] = [[275,175], [275,525], [825,175], [825,525]]
            config["coins_req"] = 4
            for x in range(250,850,100): config["grid_cells"] += [(x,150), (x,250), (x,350), (x,450)]
            for x in range(300,850,100): config["grid_cells"] += [(x,200), (x,300), (x,400), (x,500)]
            for i, x in enumerate(range(275, 875, 50)):
                dy = 8 if i % 2 == 0 else -8
                config["enemies"].append([x, 170 if i % 2 == 0 else 530, 0, dy])

        elif lvl == 7:
            config["player_pos"] = (325-15, 175-15)
            config["finish_rect"] = pygame.Rect(750, 300, 100, 100)
            config["walls_pts"] = [(250,100), (450,100), (450,150), (550,150), (550,100), (750,100), (750,300), (850,300), (850,400), (750,400), (750,600), (550,600), (550,550), (450,550), (450,600), (250,600), (250,100)]
            config["coins"] = [[275, 575], [725, 125], [725, 575]]; config["coins_req"] = 3
            # Grid Level 7
            for y in range(150, 650, 100): config["grid_cells"] += [(250, y), (550, y)]
            for y in range(100, 600, 100): config["grid_cells"] += [(400, y), (700, y)]
            for x, y in [(300,100), (350,250), (300,400), (350,550), (450,150), (500,500), (600,100), (650,250), (600,400), (650,550)]:
                config["grid_cells"].append((x, y))
            # Enemies: [x, y, dx, dy]
            config["enemies"] = [[274, 124, 4, 0], [274, 274, 4, 0], [274, 424, 4, 0], [726, 124, -4, 0], [726, 274, -4, 0], [726, 424, -4, 0], [424, 174, 4, 0]]

        elif lvl == 8:
            config["player_pos"] = (150-15, 150-15)
            config["finish_rect"] = pygame.Rect(900, 300, 100, 100)
            config["checkpoints"] = [pygame.Rect(500, 400, 100, 100)]
            config["walls_pts"] = [(100,100), (200,100), (200,200), (300,200), (300,100), (600,100), (600,400), (700,400), (700,100), (1000,100), (1000,400), (900,400), (900,200), (800,200), (800,500), (1000,500), (1000,600), (700,600), (700,500), (400,500), (400,600), (100,600), (100,100)]
            config["coins"] = [[950, 550]]; config["coins_req"] = 1
            # Grid Level 8
            for y in range(200, 600, 100): config["grid_cells"] += [(100, y), (700, y)]
            for y in range(250, 650, 100): config["grid_cells"] += [(150, y), (750, y)]
            for y in range(100, 400, 100): config["grid_cells"] += [(500, y)]
            for y in range(150, 450, 100): config["grid_cells"] += [(550, y)]
            for x, y in [(200,200), (250,250), (300,200), (350,250), (300,100), (350,150), (400,100), (450,150), (200,500), (250,550), (300,500), (350,550), (300,400), (350,450), (400,400), (450,450), (600,400), (650,450), (800,100), (850,150), (900,100), (950,150), (900,200), (950,250), (800,500), (850,550), (900,500), (950,550)]:
                config["grid_cells"].append((x, y))
            # Enemies: Static + Moving
            statics = [[250,225], [325,150], [450,175], [525,250], [175,350], [125,450], [250,525], [325,450], [400,425], [475,475], [725,550], [725,350], [775,250], [850,175], [925,250]]
            config["enemies"] = [[s[0], s[1], 0, 0] for s in statics]
            config["enemies"] += [[125,225,5,0], [375,275,-5,0], [575,175,-5,0], [175,575,-5,0], [375,575,-5,0], [725,425,5,0], [725,125,5,0], [975,175,-5,0], [525,376,5,0], [901,575,0,-5]]

        elif lvl == 9:
            config["player_pos"] = (475-15, 150-15)
            config["finish_rect"] = pygame.Rect(600, 100, 150, 100)
            config["walls_pts"] = [(400,100), (550,100), (550,200), (450,200), (450,250), (500,250), (500,450), (400,450), (400,500), (650,500), (650,450), (550,450), (550,250), (600,250), (600,100), (750,100), (750,200), (650,200), (650,400), (750,400), (750,550), (650,550), (650,600), (400,600), (400,550), (300,550), (300,400), (400,400)]
            config["coins_req"] = 0
            # Grid Level 9
            for x in range(300, 800, 100): config["grid_cells"].append((x, 500))
            for x, y in [(400,200), (450,250), (400,300), (450,350), (400,400), (300,400), (350,450), (450,550), (550,550), (650,450), (700,400), (600,400), (550,350), (600,300), (550,250), (600,200)]:
                config["grid_cells"].append((x, y))
            config["enemies"] = [[486,275,-2,0], [486,375,-2,0], [386,475,-2,0], [736,525,-2,0], [736,425,-2,0], [636,425,-2,0], [636,325,-2,0], [414,325,2,0], [414,425,2,0], [314,425,2,0], [314,525,2,0], [664,475,2,0], [564,375,2,0], [564,275,2,0], [425,514,0,2], [525,514,0,2], [625,514,0,2], [475,586,0,-2], [575,586,0,-2]]

        elif lvl == 10:
            config["player_pos"] = (900-15, 300-15)
            config["finish_rect"] = pygame.Rect(150, 350, 100, 100)
            config["walls_pts"] = [(350,150), (950,150), (950,350), (850,350), (850,200), (750,200), (750,550), (150,550), (150,350), (250,350), (250,500), (350,500), (350,150)]
            config["coins"] = [[375, 175], [725, 525]]; config["coins_req"] = 2
            # Grid Level 10
            for x in range(350, 950, 100): config["grid_cells"].append((x, 150))
            for x in range(400, 800, 100): config["grid_cells"].append((x, 200))
            for x in range(350, 750, 100): config["grid_cells"].append((x, 250))
            for x in range(400, 800, 100): config["grid_cells"].append((x, 300))
            for x in range(350, 750, 100): config["grid_cells"].append((x, 350))
            for x in range(400, 800, 100): config["grid_cells"].append((x, 400))
            for x in range(350, 750, 100): config["grid_cells"].append((x, 450))
            for x in range(200, 800, 100): config["grid_cells"].append((x, 500))
            config["grid_cells"] += [(150, 450), (900, 200)]
            # Enemies
            center = (550, 350)
            for r in [250, 215, 180, 145, 110, 75, 40]:
                for off in [0, 1.6, 3.2, 4.8]: config["enemies"].append([center[0], center[1], r, off])
        return config