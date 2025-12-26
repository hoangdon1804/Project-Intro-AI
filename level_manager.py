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
            config["enemies"] = [[325,325,3,0], [325,425,3,0], [775,275,-3,0], [775,375,-3,0]]
            config["walls_pts"] = [(250,450), (250,200), (100,200), (100,500), (350,500), (350,450), (800,450), (800,250), (850,250), (850,500), (1000,500), (1000,200), (750,200), (750,250), (300,250), (300,450)]
            config["finish_rect"] = pygame.Rect(850, 200, 150, 300)
            # Grid Level 0
            for x in range(350, 800, 100): config["grid_cells"] += [(x,250), (x,350)]
            for x in range(300, 750, 100): config["grid_cells"] += [(x,300), (x,400)]
            config["grid_cells"] += [(250,450), (800,200)]

        elif lvl == 1:
            config["enemies"] = [[x, 226, 0, 2] for x in range(275, 875, 100)] + [[x, 474, 0, -2] for x in range(325, 925, 100)]
            config["walls_pts"] = [(250,400), (100,400), (100,300), (250,300), (250,200), (850,200), (850,300), (1000,300), (1000,400), (850,400), (850,500), (250,500)]
            config["finish_rect"] = pygame.Rect(850, 300, 150, 100)
            config["coins"] = [[550, 350]]; config["coins_req"] = 1
            # Grid Level 1
            for x in range(300, 850, 100): config["grid_cells"] += [(x, 200), (x, 300), (x, 400)]
            for x in range(250, 800, 100): config["grid_cells"] += [(x, 250), (x, 350), (x, 450)]

        elif lvl == 2:
            config["player_pos"] = (550-15, 350-15)
            config["finish_rect"] = pygame.Rect(500, 300, 100, 100)
            config["enemies"] = [[526,275,1.5,0], [574,275,1.5,0], [625,275,0,1.5], [625,326,0,1.5], [625,374,0,1.5], [625,425,-1.5,0], [574,425,-1.5,0], [526,425,-1.5,0], [475,425,0,-1.5], [475,374,0,-1.5]]
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

        return config