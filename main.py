import pygame
from units import *
from structures import *

import os
from math import ceil
from random import randint as r_int, randrange as r_range

WIDTH = 16


def speed():
    x = r_int(0, 1000)
    if x < 5:
        return 8
    elif x < 10:
        return 4
    return 2
    

class SoundControl:
    
    def __init__(self):
        pygame.mixer.init()
        self.toPlay = []
        self.play_tick = 0
        

    def play_sounds(self):
      
        if self.play_tick == 0:
            sounds = self.toPlay
            for s in sounds:
                if s == "boom.mp3":
                    pygame.mixer.music.load(s)
                    pygame.mixer.music.play()
                else:
                    pygame.mixer.Sound(s).play()

            self.toPlay = []
        self.play_tick = (self.play_tick + 1) % 10


    def load_sound(self, file):
        if file not in self.toPlay:
            self.toPlay.append(file)



class ScoreBoard:
    
    def __init__(self, game):
        self.font = pygame.font.Font("PressStart2P-Regular.ttf", 13)
        self.game = game
        
        
    def text_line(self, text, x, y):
        line = self.font.render(text, True, (255,255,255))
        self.game.screen.blit(line, (x, y))
        
    def render(self):
        self.text_line(f"lvl:{self.game.level}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 20) # lvl
        score = str(int(self.game.score))
        while len(score) < 5:
            score = "0" + score
        self.text_line(score, WIDTH * (self.game.maze.cols) + self.game.padding * 10, 20) # score

        self.text_line(f"\u2665:{str(self.game.lives)}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 70) # lives
        self.text_line(f"{int(self.game.player.hp * 4)}%", WIDTH * (self.game.maze.cols) + self.game.padding * 10, 70) # hp
        
        
        self.text_line(f"[1]:{self.game.inventory[0]}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 120) # bullet1
        self.text_line(f"[2]:{self.game.inventory[1]}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 170) # bullet2
        self.text_line(f"[3]:{self.game.inventory[2]}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 220) # bullet2
        self.text_line(f"[4]:{self.game.inventory[3]}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 270) # bullet2
        


class GameState:
    def __init__(self, m, n, WDITH, PADDING, SPARSITY, Fill_color):


        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        self.sound = SoundControl()
        self.clock = pygame.time.Clock()
        
        self.m = m
        self.n = n

        file = open('CourtYard_Settings.txt') 
        self.content = file.readlines() 
        file = open('level_settings.txt')
        self.level_settings = file.readlines()
        
        self.level = 0
        self.width = WIDTH
        self.sparsity = SPARSITY
        self.padding = PADDING
        self.wall_color = (r_int(0,255),r_int(0,255),r_int(0,255))
        self.fill_color = Fill_color

        self.maze = Maze(self, m, n, (0, 0, 100), self.padding, self.wall_color)
        self.maze.create_center()
        self.screen = pygame.display.set_mode((WIDTH * (self.maze.cols) + 18 * PADDING, 2 * PADDING + (self.maze.rows) * WIDTH))
        self.end_rect = pygame.Rect(1 * WIDTH + PADDING, 1 * WIDTH, WIDTH, WIDTH)
        self.entities = [Snake(self, (0,255,0), (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), "alive", 1, 200, 16)]

        self.traps = []

        self.player = Player(self) 
        self.inventory = [10, 5, 5, 1] # bullets,powered,mines,trap-clear
        self.support = []
       
        self.text = ScoreBoard(self)
        self.score = 0
        self.state = None
        self.lives = 100
        self.muted = -1
        
        self.running = True
        self.hasPowerUp = False



    def start_level(self):
        
        
        while self.lives > 0:
            result = 0
            temp = self.maze.get_layout()
            
            inv = [item for item in self.inventory]
            temp_score = self.score
            self.sound.toPlay = []
            x = self.run()
            if x >= 1:
                self.score += x * ceil(self.level / 100)
                self.wall_color = (r_int(0,255),r_int(0,255),r_int(0,255))
                if self.level % 5 == 4:
                    
           
                    self.maze = CourtYard(self, self.m, self.n, (100, 100, r_int(0, 35)), self.padding, self.wall_color, self.content[r_range(0, len(self.content))])
                else:
                    self.maze = Maze(self, self.m, self.n, (r_int(0, 100), r_int(0, 100), r_int(0, 40)), self.padding, self.wall_color)
                self.maze.create_center()
                self.level += 1
                self.inventory = [1 + i if 1 + i < 99 else 99 for i in self.inventory]
                if self.level % 2 == 0:
                    self.inventory[1] -= 1
                    self.inventory[3] -= 1
                
            elif x == 0:
                self.lives -= 1
                
                self.maze.layout = temp
                self.inventory = inv
                self.score = temp_score
                
            elif x == -1:
                break
                    
            self.player=  Player(self)
            try:
                level_settings = self.level_settings[self.level - 1].strip().split(" ") # Entity Builder Stalker Giant Snake
            except IndexError:
                level_settings = [r_int(10, self.level // 2) for i in range(5)]
                
            self.entities = []  
            self.support = []
            
            # for i in range(1):
            self.entities += [Entity(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 75, 1, speed(), 100, 1) for i in range(int(level_settings[0]))]
            self.entities += [Builder(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 80, 1, speed(), .15, r_int(1, 2)) for i in range(int(level_settings[1]))]
            # self.entities += [Entity(self.screen, self.maze, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 80, 1, 2, 0, 1) for i in range(15)]
           
            self.entities += [Giant(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), r_int(60, 80), 1, speed(), 0, r_int(3,4)) for i in range(int(level_settings[3]))]
            self.entities += [Stalker(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), r_int(30, 76), 1, speed(), r_int(2, 3)) for i in range(int(level_settings[2]))]
            try:
                self.entities += [Snake(self, (0, 255, 0), (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), "unravel", 1, r_int(1, self.level), 8) for i in range(int(level_settings[4]))]
            except ValueError:
                pass
            self.traps = []
          
  
        pygame.quit()
            
                
                
    def run(self):
        self.running = True
        self.hasPowerUp = False
        while self.running:
    
            self.clock.tick(60)
        
            if self.state == "paused":
                for entity in self.entities:
                    entity.render()
                self.player.render()

                self.text.render()
                pygame.display.flip()
                for e in pygame.event.get():
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_p:
                            self.state = None
                        elif e.key == pygame.K_ESCAPE:
                            return -1
                        elif e.key == pygame.K_m:
                            self.muted *= -1
                continue

            if self.player.hp <= 0:
                # pygame.mixer.music.load("death.mp3")
                # pygame.mixer.music.play()
                return 0
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                            self.state = "paused"
                    elif e.key == pygame.K_ESCAPE:
                        return -1
                    elif e.key == pygame.K_1 and self.inventory[0] > 0:
                        self.player.shoot("alive")
                    #     self.sound.player_shoot()
                    elif e.key == pygame.K_2 and self.inventory[1] > 0:
                        self.player.shoot("powered")
                    #     self.sound.player_shoot()
                    elif e.key == pygame.K_3 and self.inventory[2] > 0:
                        self.player.lay_mine(self.player.rect.x, self.player.rect.y, 5)
                    # elif e.key == pygame.K_c:
                    #     self.maze.change_color()
                    elif e.key == pygame.K_4 and self.inventory[3] > 0:
                        self.player.clear_traps(15)
                    #     self.sound.load_sound("boom.mp3")
                    elif e.key == pygame.K_l:
                        return 100
                    elif e.key == pygame.K_0:
                        self.support.append(Gift(self, (WIDTH + self.padding, self.padding + WIDTH), (255, 255, 0), 75, 1, 4, 0, 1))
                    elif e.key == pygame.K_m:
                        self.muted *= -1

           

                      
    
        # Move the player if an arrow key is pressed

            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.player.move_single_axis(-1, 0)
                self.player.direction = "west"
            if key[pygame.K_RIGHT]:
                self.player.move_single_axis(1, 0)
                self.player.direction = "east"
            if key[pygame.K_UP]:
                self.player.move_single_axis(0, -1)
                self.player.direction = "south"
            if key[pygame.K_DOWN]:
                self.player.move_single_axis(0, 1)
                self.player.direction = "north"
                
            
        
            if self.player.rect.colliderect(self.end_rect):
                self.running = False
                # pygame.mixer.music.load("complete.mp3")
                # pygame.mixer.music.play()
                return 4 * self.player.hp
                
    
            self.screen.fill(self.fill_color)
     
             
            self.player.doSomething()
            
            for support in self.support:
                if support.hp <= 0 or support.state == "dead":
                    self.support.remove(support)    
                else:    
                    support.doSomething()
            
            for entity in self.entities:
                if entity.state == "dead":
                 
                    self.score += entity.scale
                    self.entities.remove(entity)
                else:
                    entity.doSomething()
                    
        
            self.maze.doSomething()    
            for trap in self.traps:
                if trap.state == "dead" or trap.hp == 0:
                   self.traps.remove(trap)
             
           
            
           
           
            if self.player.hp < 13:
                if len(self.support) < 1:
                    self.support.append(Gift(self, (WIDTH + self.padding, self.padding + WIDTH), (255, 255, 0), 80, 1, 4, 0, 1))
                    
                else:
                    for support in self.support:
                        if isinstance(support, Gift):
                            break
                    else: 
                        if self.player.rect.x - 16 > 80 or self.player.rect.y - 16 > 80:
                            self.support.append(Gift(self, (WIDTH + self.padding, self.padding + WIDTH), (255, 255, 0), 80, 1, 4, 0, 1))
                        
                    
            if r_int(0, 1000) < 10 and False == self.hasPowerUp and self.player.power_tick <= 0 and r_int(0, 100) < 10:
                self.support.append(PowerUp(self))
                self.hasPowerUp = True
            #     self.sound.load_sound("power.mp3")
                    
            self.text.render()
            pygame.display.flip()
            if self.muted < 0:
                self.sound.play_sounds()



game = GameState(36, 36, 16, 10, (100, 100), (0,0,0))
game.start_level()
