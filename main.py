import pygame
from units import *
from structures import *

import os
from math import ceil
from random import randint as r_int, randrange as r_range

WIDTH = 16


def speed():
    x = r_int(0, 1000 - (game.level // 2))
    if x < 5:
        return 8
    elif x < 10:
        return 4
    return 2
    

class SoundControl:
    
    def __init__(self):
        self.muted = False
        pygame.mixer.init()
        self.toPlay = []
        self.play_tick = 0
        

    def play_sounds(self):
        if not self.muted:
            if self.play_tick == 0:
                sounds = self.toPlay
                for s in sounds:
                    if s == "boom.mp3":
                        pygame.mixer.music.load("sounds/" + s)
                        pygame.mixer.music.play()
                    else:
                        pygame.mixer.Sound("sounds/" + s).play()

                self.toPlay = []
            self.play_tick = (self.play_tick + 1) % 10


    def load_sound(self, file):
        if file not in self.toPlay:
            self.toPlay.append(file)



class ScoreBoard:
    
    def __init__(self, game):
        self.font = pygame.font.Font("PressStart2P-Regular.ttf", 13)
        self.small_font = pygame.font.Font("PressStart2P-Regular.ttf", 8)
        self.game = game
        
        
    def text_line(self, text, x, y):
        line = self.font.render(text, True, (255,255,255))
        self.game.screen.blit(line, (x, y))
        

    def small_text_line(self, text, x, y):
        line = self.small_font.render(text, True, (255,255,255))
        self.game.screen.blit(line, (x, y))
        
        
  


    def render(self):
        self.text_line(f"lvl:{self.game.level}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 20) # lvl
        score = str(int(self.game.score))
        while len(score) < 5:
            score = "0" + score
        self.text_line(score, WIDTH * (self.game.maze.cols) + self.game.padding * 11, 20) # score

        self.text_line(f"\u2665:{str(self.game.lives)}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 70) # lives
        self.text_line(f"{int(self.game.player.hp * 4)}%", WIDTH * (self.game.maze.cols) + self.game.padding * 11, 70) # hp
        
        
        self.text_line(f"[1]:{self.game.inventory[0]}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 120) # bullet1
        self.text_line(f"[2]:{self.game.inventory[1]}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 170) # bullet2
        self.text_line(f"[3]:{self.game.inventory[2]}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 220) # bullet2
        self.text_line(f"[4]:{self.game.inventory[3]}", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 270) # bullet2
        
        self.small_text_line("Get to the white", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 360) # bullet2
        self.small_text_line("square.", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 380) # bullet2
        self.small_text_line("Move with arrow keys", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 400) # bullet2
        self.small_text_line("P pause, M mute", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 420)
        self.small_text_line("C change color", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 440)
        self.small_text_line("Esc quit, X die", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 460)
        self.small_text_line("1 Normal bullet", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 500)
        self.small_text_line("2 Strong bullet", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 520)
        self.small_text_line("3 Landmine", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 540)
        self.small_text_line("4 Area Clear", WIDTH * (self.game.maze.cols) + self.game.padding * 1.5, 560)
        


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
        self.entities = [Snake(self, (0, 255, 0), (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), "alive", 1, 200, 16)]

        self.traps = []

        self.player = Player(self) 
        self.inventory = [10, 5, 0, 0] # bullets,powered,mines,trap-clear
        self.support = []
       
        self.text = ScoreBoard(self)
        self.score = 0
        self.state = None
        self.lives = 10
        
        self.running = True
        self.hasPowerUp = False




    def start_level(self):
        
        
        while self.lives > 0:
            result = 0
            self.maze.create_center()
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
                    sparsity = (r_int(0, 100), r_int(0, 100), r_int(0, 40))
                    
                    if self.level % 4 <= 3 and r_int(0,100) <= 10:
                        sparsity = (r_int(0, 15), r_int(0, 15), r_int(90, 100))
                    self.maze = Maze(self, self.m, self.n, sparsity, self.padding, self.wall_color)
                self.maze.create_center()
                self.level += 1
                self.inventory = [1 + i + self.level // 10 if 1 + i + self.level // 10 < 99 else 99 for i in self.inventory]
                if self.level % 3 != 0:
                    self.inventory[1] -= 1
                    self.inventory[3] -= 1
                
            elif x == 0:
                self.lives -= 1
                
                self.maze.layout = temp
                self.inventory = inv
                self.score = temp_score
                
            elif x == -1:
                pygame.quit()
                return
                    
            self.player=  Player(self)
            try:
                level_settings = self.level_settings[self.level - 1].strip().split(" ") # Entity Builder Stalker Giant Snake
            except IndexError:
                level_settings = [r_int(10, self.level // 2) for i in range(6)]
                
            self.entities = []  
            self.support = []
            self.entities += [Entity(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 75, 1, speed(), 100, 1) for i in range(int(level_settings[0]))]
            self.entities += [Builder(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 80, 1, speed(), r_int(5, 30) * .01, 1) for i in range(int(level_settings[2]))]
            # self.entities += [Entity(self.screen, self.maze, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 80, 1, 2, 0, 1) for i in range(15)]
           
            self.entities += [Giant(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), r_int(60, 80), 1, speed(), 0, r_choice((3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4))) for i in range(int(level_settings[3]))]
            self.entities += [Stalker(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), r_int(30, 76), 1, speed(), r_int(2, 3)) for i in range(int(level_settings[1]))]
            try:
                self.entities += [Snake(self, (0, 255, 0), (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), "unravel", 1, (r_int(1, self.level) if len(self.entities) < 10 else r_int(100, 200)), (8 if r_int(0, 100) < 95 else r_choice((4,4,4,4,4,8)))) for i in range(int(level_settings[4]))]
            except ValueError:
                pass
            
            self.entities += [Chaser(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 75, 1, 1, r_int(1,2)) for i in range(int(level_settings[5]))]
            
            self.traps = []
          


       
    def end(self):

        pygame.draw.rect(self.screen, (0,0,0), pygame.Rect( WIDTH * (self.maze.cols) + self.padding * 1.5, 20, 200, 600))
        self.text.text_line("Final Score", WIDTH * (self.maze.cols) + self.padding * 1.5, 20)
        self.text.text_line(str(int(self.score)), WIDTH * (self.maze.cols) + self.padding * 1.5, 40)
        self.text.text_line("Final Level", WIDTH * (self.maze.cols) + self.padding * 1.5, 90)
        self.text.text_line(str(self.level), WIDTH * (self.maze.cols) + self.padding * 1.5, 110)
        self.text.font = pygame.font.Font("PressStart2P-Regular.ttf", 9)
        self.text.text_line("Press esc to quit", WIDTH * (self.maze.cols) + self.padding * 1.5, 360)
        pygame.display.flip()
        
        while True:
                
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:    
                    if e.key == pygame.K_ESCAPE: 
                        pygame.quit()
                        return -1

            
                
    def run(self):
        self.running = True
        self.hasPowerUp = False
        
        
        while self.running:
    
            self.clock.tick(60)
            

        
            if self.state == "paused":

                for e in pygame.event.get():
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_p:
                            self.state = "unpaused"
                        elif e.key == pygame.K_ESCAPE:
                            return -1
                        elif e.key == pygame.K_m:
                            self.sound.muted = not self.sound.muted
                        elif e.key == pygame.K_c:
                            self.maze.change_color()
                continue

            if self.player.hp <= 0:
                if not self.sound.muted:
                    pygame.mixer.music.load("sounds/death.mp3")
                    pygame.mixer.music.play()
                if self.lives <= 1:
                    self.end()
                    return -1
                else:
                    return 0
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                            self.state = "paused"
                            continue
                    elif e.key == pygame.K_ESCAPE:
                        return -1
                    elif (e.key == pygame.K_1) and self.inventory[0] > 0:
                        self.player.shoot("alive")
                        self.sound.load_sound("quack.mp3")
                    elif (e.key == pygame.K_2) and self.inventory[1] > 0:
                        self.player.shoot("powered")
                        self.sound.load_sound("quack.mp3")
                    elif (e.key == pygame.K_3) and self.inventory[2] > 0:
                        self.player.lay_mine(self.player.rect.x, self.player.rect.y, 2 + (self.level // 10))
                    elif e.key == pygame.K_c:
                        self.maze.change_color()
                    elif (e.key == pygame.K_4) and self.inventory[3] > 0:
                        self.player.clear_traps(15)
                        self.sound.load_sound("boom.mp3")
                    elif e.key == pygame.K_m:
                        self.sound.muted = not self.sound.muted
                    elif e.key == pygame.K_x:
                        if self.lives <= 1:
                            self.end()
                            return -1
                        else:
                            return 0
                    # elif e.key == pygame.K_l:
                    #     return 100
           

                      
    
        # Move the player if an arrow key is pressed

            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                self.player.move_single_axis(-1, 0)
                self.player.direction = "west"
            if key[pygame.K_RIGHT] or key[pygame.K_d]:
                self.player.move_single_axis(1, 0)
                self.player.direction = "east"
            if key[pygame.K_UP] or key[pygame.K_w]:
                self.player.move_single_axis(0, -1)
                self.player.direction = "south"
            if key[pygame.K_DOWN] or key[pygame.K_s]:
                self.player.move_single_axis(0, 1)
                self.player.direction = "north"
               
                
            
        
            if self.player.rect.colliderect(self.end_rect):
                self.running = False
                if not self.sound.muted:
                    pygame.mixer.music.load("sounds/complete.mp3")
                    pygame.mixer.music.play()
                if self.level % 5 == 0:
                    self.lives += 1 * ceil(self.level / 100)
                return 4 * self.player.hp
                
    
            self.screen.fill(self.fill_color)
     
             
            self.player.doSomething()
            
            for support in self.support:
                if support.hp <= 0 or support.state == "dead":
                    self.support.remove(support)    
                else:    
                    support.doSomething()
            
            for entity in self.entities:
               
                if entity.state == "dead" or entity.hp <= 0:
                 
                    self.score += entity.scale
                    self.entities.remove(entity)
                else:
                    entity.doSomething()
         
                    
        
            self.maze.doSomething()    
            for trap in self.traps:
                if trap.state == "dead" or trap.hp <= 0:
                   self.traps.remove(trap)
             
           
            
           
           
            if self.player.hp < 13:
                if len(self.support) < 1 and( self.player.rect.x - 16 > 80 or self.player.rect.y - 16 > 80):
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
                self.sound.load_sound("power.mp3")
                    
            self.text.render()
            pygame.display.flip()
            self.sound.play_sounds()
                
            if self.level == 0 and self.state == None:
                self.state = "paused"
            



game = GameState(36, 36, 16, 10, (100, 100), (0,0,0))
game.start_level()

