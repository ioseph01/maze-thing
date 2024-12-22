import pygame
from units import *
from structures import *

import os
import random as r

WIDTH = 16






class SoundControl:
    
    def __init__(self):
        pygame.mixer.init()
        self.toPlay = []
        self.play_tick = 0
        

    def play_sounds(self):
      
        if self.play_tick == 0:
            sounds = self.toPlay
            for s in sounds:
                print(s)
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
        

    def player_death(self):
        self.load_sound("oof.mp3")
        

    def enemy_death(self):
        self.load_sound("hit.mp3")
        

    def player_shoot(self):
        self.load_sound("quack.mp3")
        

    def player_hurt(self):
        self.load_sound("damage.mp3")


class ScoreBoard:
    
    def __init__(self, game):
        self.screen = game.screen
        self.font = pygame.font.Font("PressStart2P-Regular.ttf", 15)
        self.game = game
        
        
        
    def render(self):
        score = self.font.render(f"{int(self.game.score)}", True, (255,255,255))
        self.screen.blit(score, (WIDTH * (self.game.maze.cols) + self.game.padding * 2, 20))
        
        health = self.font.render(f"{int(4 * self.game.player.hp) }%", True, (255,255,255))
        self.screen.blit(health, (WIDTH * (self.game.maze.cols) + self.game.padding * 11, 20))
        
        invMap = [self.ammo1, self.ammo2, self.mine, self.area_clear]

        for item in range(len(self.game.inventory)):
            text = str(self.game.inventory[item])
            if self.game.inventory[item] < 10:
                text = "0" + text
            invMap[item](text)
            
            
        

    def ammo1(self, text):
        ammo1 = self.font.render(f"O:{text}", True, (255,255,255))
        self.screen.blit(ammo1, (WIDTH * (self.game.maze.cols) + self.game.padding * 2, 70))
        
    def ammo2(self, text):
        ammo2 = self.font.render(f"*:{text}", True, (255,255,255))
        self.screen.blit(ammo2, (WIDTH * (self.game.maze.cols) + self.game.padding * 11, 70))
        
    def mine(self, text):
        mine = self.font.render(f"#:{text}", True, (255,255,255))
        self.screen.blit(mine, (WIDTH * (self.game.maze.cols) + self.game.padding * 2, 120))
                
    def area_clear(self, text):
        clear = self.font.render(f"@:{text}", True, (255,255,255))
        self.screen.blit(clear, (WIDTH * (self.game.maze.cols) + self.game.padding * 11, 120))



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
        self.wall_color = (r.randint(0,255),r.randint(0,255),r.randint(0,255))
        self.fill_color = Fill_color

        self.maze = Maze(self, m, n, (100, 100, 100), self.padding, self.wall_color)
        self.maze.create_center()
        self.screen = pygame.display.set_mode((WIDTH * (self.maze.cols) + 18 * PADDING, 2 * PADDING + (self.maze.rows) * WIDTH))
        self.end_rect = pygame.Rect(1 * WIDTH + PADDING, 1 * WIDTH, WIDTH, WIDTH)
        self.entities = []
        for i in range(1):
            self.entities.append(Entity(self, (PADDING + m * WIDTH // 2, PADDING + n * WIDTH // 2), (0, 255, 0), 20, 1, 2, 100, 1))
        # self.entities = [Stalker(self.screen, self.maze, (PADDING + m * WIDTH // 2, PADDING + n * WIDTH // 2), (0, 255, 0), 20, 1, 2, 100) for i in range(1)]
        for i in range(1):
            self.entities.append(Giant(self, (PADDING + m * WIDTH // 2, PADDING + n * WIDTH // 2), (0, 255, 0), r.randint(60,80), 1, 2, 0, 3))
        # self.support.append(Gift(self.screen, self.maze, (WIDTH + PADDING, PADDING + WIDTH), (r.randint(0, 255),r.randint(0, 255),r.randint(0, 255)), 90, 1, 2, 0, 1))
        
      
        self.traps = []

        self.player = Player(self) 
        self.inventory = [20, 5, 5, 5] # bullets,powered,mines,trap-clear
        self.support = []
       
        self.text = ScoreBoard(self)
        self.score = 0
        self.state = None
        self.lives = 100
        self.muted = -1
        
        self.running = True
        self.hasPowerUp = False


        

    def calc_snakes(self):
        if self.level % 5 == 0 and self.level > 6:
            return r.randint(1, self.level)
        else:
            return r.randint(self.level // 5, self.level)
        
    def calc_cells(self):
        return r.randint(self.level, self.level * 3 // 2)
    
    def calc_giants(self):
        if self.level % 3 == 0 and self.level > 4:
            return r.randint(2, self.level)
        else:
            return r.randint(self.level // 3, self.level)
        

    def start_level(self):
        
        
        while self.lives > 0:
            result = 0
            temp = self.maze.get_layout()
            
            inv = [item for item in self.inventory]
            temp_score = self.score
            print("Level", self.level)
            self.sound.toPlay = []
            x = self.run()
            print("returned", x)
            if x >= 1:
                self.score += x
                self.wall_color = (r.randint(0,255),r.randint(0,255),r.randint(0,255))
                if self.level % 5 == 4:
                    
           
                    self.maze = CourtYard(self, self.m, self.n, (100, 100, r.randint(0, 35)), self.padding, self.wall_color, self.content[r.randrange(0, len(self.content))])
                else:
                    self.maze = Maze(self, self.m, self.n, (r.randint(0, 100), r.randint(0, 100), r.randint(0, 40)), self.padding, self.wall_color)
                self.maze.create_center()
                self.level += 1
                self.inventory = [i + self.level // 2 if i + self.level // 2 < 99 else 99 for i in self.inventory]
                print(self.inventory)
                
            elif x == 0:
                self.lives -= 1
                
                self.maze.layout = temp
                self.inventory = inv
                self.score = temp_score
                
            elif x == -1:
                break
                    
            self.player=  Player(self)
            level_settings = self.level_settings[self.level - 1].strip().split(" ") # Entity Builder Stalker Giant Snake
            self.entities = []  
            self.support = []
            
            # for i in range(1):
            self.entities += [Entity(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 80, 1, 2, 100, 1) for i in range(int(level_settings[0]))]
            self.entities += [Builder(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 80, 1, 2, .15, r.randint(1, 2)) for i in range(int(level_settings[1]))]
            # self.entities += [Entity(self.screen, self.maze, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 80, 1, 2, 0, 1) for i in range(15)]
           
            self.entities += [Giant(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), r.randint(60, 80), 1, 2, 0, r.randint(3,4)) for i in range(int(level_settings[3]))]
            self.entities += [Stalker(self, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 30, 1, 2, r.randint(2, 3)) for i in range(int(level_settings[2]))]
        
            self.entities += [Snake(self, (0, 255, 0), (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), "unravel", 1, 100, 8) for i in range(int(level_settings[4]))]
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
                print("DIED")
                return 0
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                            self.state = "paused"
                    elif e.key == pygame.K_ESCAPE:
                        return -1
                    # elif e.key == pygame.K_t:
                    #     self.player.trace(self.maze.layout, 0, 1)
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
                        print("And 1")
                    # elif e.key == pygame.K_9:
                    #     self.player.incHits()
                    # elif e.key == pygame.K_5:
                    #     self.player.summon(self.player.rect.x, self.player.rect.y)
                    #     self.score -= 400
                    elif e.key == pygame.K_m:
                        self.muted *= -1
                    # elif e.key == pygame.K_a:
                    #     self.player.move_single_axis(-WIDTH, 0)
                    # elif e.key == pygame.K_s:
                    #     self.player.bullets.append(Shield(self.screen, self.maze))
                        
                    elif e.key == pygame.K_x:
                        print(self.DELETE_LATER)
                        with open("f.txt", "a") as f:
                            f.write(str(self.DELETE_LATER) + "\n")
           

                      
    
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
             
            self.text.render()
           
            
           
           
            if self.player.hp < 13:
                for support in self.support:
                    if type(support) == Gift:
                        break
                else:
                    self.support.append(Gift(self, (WIDTH + self.padding, self.padding + WIDTH), (255, 255, 0), 80, 1, 4, 0, 1))
                    print("GIFT!")
                    
            if r.randint(0, 1000) < 10 and False == self.hasPowerUp and self.player.power_tick <= 0 and r.randint(0, 100) < 10:
                self.support.append(PowerUp(self))
                print("ANd 1")
                self.hasPowerUp = True
            #     self.sound.load_sound("power.mp3")
                    
                
            pygame.display.flip()
            if self.muted < 0:
                self.sound.play_sounds()



game = GameState(36, 36, 16, 10, (100, 100), (0,0,0))
game.start_level()
