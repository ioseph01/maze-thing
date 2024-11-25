
import random as r
import os
from symbol import return_stmt
import trace
import pygame
import math
import copy


WIDTH = 8
m,n = 12, 12
SPARSITY = 50

WALL_COLOR = (r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))
FILL_COLOR = (r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))


def directionCoordMap(val):
    
    m = {"north" : (0, 1), "east" : (1, 0), "south" : (0, -1), "west" : (-1, 0)}
    if val in m:
        return m[val]
    
    for k in m:
        if m[k] == val:
            return k
        


class Unit(object):
    
    def __init__(self, screen, maze, color, coords, state, direction, scale):
        self.screen = screen
        self.maze = maze
        self.color = color
        self.state = ""
        self.direction = direction
        self.coords = coords
        self.rect = pygame.Rect(coords[0], coords[1], WIDTH //scale, WIDTH //scale)
        self.scale = scale
        

    def doSomething(self):
        return NotImplementedError
    

    def render(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
    

    def move_single_axis(self, dx, dy):
        return NotImplementedError
        
    


class Bullet(Unit):
    
    def __init__(self, screen, maze, coords, direction):
        super(Bullet, self).__init__( screen, maze, (0,0,0), coords, "alive", direction, 1)
        
        

    def doSomething(self):
        if self.state != "dead":
            toMove = directionCoordMap(self.direction)
            self.move_single_axis(toMove[0], toMove[1])
            self.render()
    

    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

        for j in range(self.rect.y // WIDTH - 1, 2 + self.rect.y // WIDTH):
            for i in range(self.rect.x // WIDTH - 1, self.rect.x // WIDTH + 2):
                
                wall = self.maze.layout[j][i]
                if self.rect.colliderect(wall.rect) and wall.state == "alive":
                    self.state = "dead"
                    


class Snake(Unit):
    
    def __init__(self, screen, maze, color, coords, state, scale, segments, step):
        super(Snake, self).__init__(screen, maze, color, coords, state, "north", scale)
        self.unravel_counter = 0
        self.step = step
        self.move_tick = 0
        
        if type(segments) == list:
            self.segments = segments
        elif type(segments) == int:
            self.segments = [Entity(self.screen, self.maze, self.coords, self.color, r.randint(20, 40), self.scale, self.step) for i in range(segments)]
            

    def doSomething(self):
       
        if self.state == "dead":
            return
        
        elif len(self.segments) == 0:
            self.state = "dead"
            
        elif self.unravel_counter >= len(self.segments):
            self.unravel_counter = len(self.segments)
            self.state = "searching"
            
        self.render()
        self.move_tick = (self.move_tick + 1) % 2
      
        if self.move_tick % 2 == 0:
            
            coords = (self.segments[0].rect.x, self.segments[0].rect.y)
                
            for i in range(self.unravel_counter):
                
                
                    
                for bullet in game.player.bullets:
                    if self.segments[i].bulletDetect(bullet):
                            
                        self.segments.remove(self.segments[i])
                        if i != 0 and i != len(self.segments) - 2:
                            game.snakes.append(Snake(self.screen, self.maze, self.color, self.coords, "searching", self.scale, self.segments[i:], self.step))
                            self.segments = self.segments[:i]
                        self.unravel_counter += 1
                        return
                        
                temp = (self.segments[i].rect.x, self.segments[i].rect.y)
                if i == 0:
                    self.segments[i].doSomething()
                else:
                    self.segments[i].rect.x, self.segments[i].rect.y = coords
                    if self.segments[i].rect.colliderect(game.player.rect):
                        print("Hit!!!!!!!")
                            
                coords = temp
        self.unravel_counter += 1
        if self.unravel_counter >= len(self.segments):
            self.state = "searching"


    def render(self):
        for i in self.segments:
            i.render()
                    

class Player(Unit):
    
    def __init__(self, screen, maze):
        super(Player, self).__init__(screen, maze, (255, 200, 0), ((maze.cols - 2) * WIDTH, (maze.rows - 2) * WIDTH), "alive", "north", 1)
        self.bullets = []
        

    def shoot(self):
        self.bullets.append(Bullet(self.screen, self.maze, (self.rect.x, self.rect.y), self.direction))
        

    def doSomething(self):
        self.render()
        for bullet in self.bullets:
            if bullet.state == "dead":
                self.bullets.remove(bullet)
                
            else:
                bullet.doSomething()
    


    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

        for j in range(self.rect.y // WIDTH - 1, 2 + self.rect.y // WIDTH):
            for i in range(self.rect.x // WIDTH - 1, self.rect.x // WIDTH + 2):
                
                wall = self.maze.layout[j][i]
                if self.rect.colliderect(wall.rect) and wall.state == "alive":
                    if dx > 0: # Moving right; Hit the left side of the wall
                            self.rect.right = wall.rect.left
                    if dx < 0: # Moving left; Hit the right side of the wall
                        self.rect.left = wall.rect.right
                    if dy > 0: # Moving down; Hit the top side of the wall
                        self.rect.bottom = wall.rect.top
                    if dy < 0: # Moving up; Hit the bottom side of the wall
                        self.rect.top = wall.rect.bottom
                        

    def change_color(self):
        self.color = (r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))
        


class Entity(Unit):
    
    def __init__(self, screen, maze, coords, color, trace_commitment, scale, step):
        super(Entity, self).__init__(screen, maze, color, coords, "alive", r.choice(["north", "east", "south", "west"]), scale)
        self.path = []
        self.step = step
        self.trace_commitment = trace_commitment / 100
        self.target = (self.maze.rows, self.maze.cols)
        self.trace_tick = 0
        self.tick = 0
        

    def get_scatter(self):
        return r.choice([(3, 3), (math.ceil(self.maze.cols / 2), 3), (self.maze.cols - 2, self.maze.rows - 2), (math.ceil(self.maze.cols / 2), self.maze.rows - 2),
         (self.maze.cols - 2 , math.ceil(self.maze.rows / 2)), (3, math.ceil(self.maze.rows / 2)), (3, self.maze.rows - 2),
        (math.ceil(self.maze.cols / 2), self.maze.rows - 2)])
    

    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
        for j in range(self.rect.y // WIDTH - 1, 2 + self.rect.y // WIDTH):
            for i in range(self.rect.x // WIDTH - 1, self.rect.x // WIDTH + 2):
                
                wall = self.maze.layout[j][i]
                if self.rect.colliderect(wall.rect) and wall.state == "alive":
                    if dx > 0: # Moving right; Hit the left side of the wall
                        self.rect.right = wall.rect.left
                        
                    elif dx < 0: # Moving left; Hit the right side of the wall
                        self.rect.left = wall.rect.right
                        
                    if dy > 0: # Moving down; Hit the top side of the wall
                        self.rect.bottom = wall.rect.top
                       
                    elif dy < 0: # Moving up; Hit the bottom side of the wall
                        self.rect.top = wall.rect.bottom
                        


    def doSomething(self):
        self.render()

        if self.rect.colliderect(game.player.rect):
            print("HIT!!!!!!!")
            
        for bullet in game.player.bullets:
            if self.bulletDetect(bullet):
                return
            
        self.tick = (self.tick + 1) % 2
        
        if self.tick == 0:
            if len(self.path) > 0:
                if self.trace_tick == WIDTH // self.step - 1:
                    dx, dy = self.path.pop(0)
                    
                else:
                    dx, dy = self.path[0]
                    
                self.move_single_axis(self.step * (dx - self.coords[0]), self.step * (dy - self.coords[1]))
                
                if self.trace_tick == WIDTH // self.step - 1:
                    self.coords = (dx, dy)
                    
                self.trace_tick = (self.trace_tick + 1) % (WIDTH // self.step)
                

            elif abs(self.rect.x - game.player.rect.x) < 120 and abs(self.rect.y - game.player.rect.y) < 120:
                self.trace(game.player.rect.x // WIDTH, game.player.rect.y // WIDTH)
                
            else:
                x, y = self.get_scatter()
                self.target = (x, y)
                self.trace(x, y)
                


    def bulletDetect(self, bullet):
        if self.rect.colliderect(bullet.rect):
            print("SHOT!!!!")
            bullet.state = "dead"
            self.state = "dead"
            return True
        return False
    

    def trace(self, target_x, target_y):
        x = 0 + self.rect.x // WIDTH
        y = 0 + self.rect.y // WIDTH
        
        visited = {(x, y)}
        paths = [[(x, y)]]
        
        while len(paths) > 0 :
            
            current = paths.pop(-1)
            x, y = current[-1]
            
            if x == target_x and y == target_y:
                self.state = "chasing"
                
                if target_x * WIDTH == game.player.rect.x and target_y * WIDTH == game.player.rect.y:
                    self.path = current
                else:
                    self.path = current[:round(len(current) * self.trace_commitment)]
                    
                if len(self.path) > 0:
                    self.coords = self.path.pop(0)
                    
                try:
                    self.target = (current[-1][0], current[-1][1])
                except IndexError:
                    print("size of current is ", len(current))
                    print("this error occurs when a player is hit by an entity, should be ok")
                    exit()
                    
                return
            
            visited.add((x, y))
            toAdd = {}
            
            if x + 1 < len(self.maze.layout[0]) and (x + 1, y) not in visited:
            
                if self.maze.layout[y][x + 1].state != "alive":
                    k = abs(target_x - x - 1) + abs(target_y - y)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x + 1, y))
                     
             
                
            if y + 1 < len(self.maze.layout) and (x, y + 1) not in visited:
                if self.maze.layout[y + 1][x].state != "alive":
                    k = abs(target_x - x) + abs(target_y - y - 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y + 1))
                    
            if x - 1 > -1 and (x - 1, y) not in visited:
                if self.maze.layout[y][x - 1].state != "alive":
                    k = abs(target_x - x + 1) + abs(target_y - y)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x - 1, y))
                          
            if y - 1 > -1 and (x, y - 1) not in visited:
           
                if self.maze.layout[y - 1][x].state != "alive":
                    k = abs(target_x - x) + abs(target_y - y + 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y - 1))

            for key in reversed(dict(sorted(toAdd.items()))):
                for val in toAdd[key]:
                    paths.append(current + [val])
            



class Wall(object):
    
    def __init__(self, coords, color):
        self.color = color
        self.state = "alive"
        self.rect = pygame.Rect(coords[0], coords[1], WIDTH, WIDTH)
        

    def render(self):
        pygame.draw.rect(game.screen, self.color, self.rect)
        


    def die(self):
        self.state = "dead"
        self.color = FILL_COLOR
        

    def revive(self):
        self.state = "alive"
        self.color = WALL_COLOR
        


class Maze(object):
    
    def __init__(self, row, col, sparsity):
        if row % 2 == 0:
            row += 1
            
        if col % 2 == 0:
            col += 1
            
        self.cols = col
        self.rows = row
        self.layout = [[Wall((i * WIDTH, j * WIDTH), WALL_COLOR) for i in range(col)] for j in range(row)]
        
        if sparsity[0] <= 0 and sparsity[1] <= 0:
            self.carve(self.layout)
            
        else:
            temp = copy.deepcopy(self.layout)
            self.carve(temp)
            self.carve(self.layout)
            self.combine(self.layout, temp, sparsity)
            
        self.layout[0][1].die()
        


    def combine(self, layout, other, sparsity):
      
        for y in range(len(layout)):
            for x in range(len(layout[y])):
                if layout[y][x].state != "alive" or "alive" != other[y][x].state and r.randint(0, 100) < sparsity[0]:
                    layout[y][x].die()
                    

                if  r.randint(0, 100 ) < sparsity[1] and x != 0 and x != len(self.layout[0]) - 1 and y != 0 and y != len(self.layout) - 1 and x % 2 == 0 and y % 2 == 0:
                    layout[y][x].die()
        

    def create_center(self):
        x = math.ceil(self.cols / 2)
        y = math.ceil(self.rows / 2)
        r = min(math.sqrt(self.rows), math.sqrt(self.cols))
        if r % 2 == 0:
            r += 1

        for j in range(-math.floor(r / 2), math.floor(r / 2) + 1):
            for i in range(-math.floor(r / 2), math.floor(r / 2) + 1):
                self.layout[y + j][x + i].die()
                

    def carve(self, layout):
        visited = set()
        toVisit = [(3,3)]       
        
        while len(toVisit) > 0:
            
            x,y = toVisit[-1]
            choices = []
            if x + 2 < self.cols and (x + 2, y) not in visited:
                choices.append([(x+2, y), (x+1,y)])
            if x - 2 > -1 and (x - 2, y) not in visited:
                choices.append([(x-2, y), (x-1,y)])
            if y + 2 < self.rows  and (x, y + 2) not in visited:
                choices.append([(x, y + 2), (x, y + 1)])
            if y - 2 > -1 and (x, y - 2) not in visited:
                choices.append([(x, y - 2), (x, y - 1)])
            

            if len(choices) == 0:
                layout[y][x].die()
                visited.add(toVisit.pop())
                
            else:
                c1, c2 = r.choice(choices)
                toVisit.append(c1)
                layout[c2[1] ][c2[0]].die()
               
                visited.add((x, y))
                

    def doSomething(self):
        self.render()
                
        
    def render(self):
        for row in self.layout:
            for col in row:
                col.render()
                


class GameState:
    def __init__(self, m, n, WDITH, PADDING, SPARSITY, Wall_color, Fill_color):

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption("Get to the red square!")
        self.clock = pygame.time.Clock()
        
        self.width = WIDTH
        self.sparsity = SPARSITY
        self.padding = PADDING
        self.wall_color = Wall_color
        self.fill_color = Fill_color

        self.maze = Maze(m, n, self.sparsity)
        self.maze.create_center()
        self.screen = pygame.display.set_mode((WIDTH * (self.maze.cols) , (self.maze.rows) * WIDTH))
        self.player = Player(self.screen, self.maze) 
        self.end_rect = pygame.Rect(1 * WIDTH, 0 * WIDTH, WIDTH, WIDTH)
        self.entities = [Entity(self.screen, self.maze, (m * WIDTH // 2, n * WIDTH // 2), (0, 255, 0), r.randint(20, 80), 1, 2) for i in range(20)]
        
        self.snakes = [Snake(self.screen, self.maze, (0, 255, 0), (m * WIDTH // 2, n * WIDTH // 2), "unravel", 1, 6, 4) for i in range(10)]
        # self.snake = Snake(self.screen, 500, self.entities[0].color, self.maze, (m * WIDTH // 2, n * WIDTH // 2), 2, 4)
       
        
                                    
        self.running = True

        

    def run(self):
        
        while self.running:
    
            self.clock.tick(60)
    
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.running = False


                    if e.key == pygame.K_t:
                      
                        self.player.trace(self.maze.layout, 0, 1)

                    
                    if e.key == pygame.K_c:
                        self.player.change_color()
                        
                    if e.key == pygame.K_SPACE:
                        self.player.shoot()
                        

                    
    
        # Move the player if an arrow key is pressed

            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.player.move_single_axis(-2, 0)
                self.player.direction = "west"
            if key[pygame.K_RIGHT]:
                self.player.move_single_axis(2, 0)
                self.player.direction = "east"
            if key[pygame.K_UP]:
                self.player.move_single_axis(0, -2)
                self.player.direction = "south"
            if key[pygame.K_DOWN]:
                self.player.move_single_axis(0, 2)
                self.player.direction = "north"
                
            
        
            if self.player.rect.colliderect(self.end_rect):
                self.running = False
                break
    
            self.screen.fill(FILL_COLOR)
     
            self.maze.render()     
            self.player.doSomething()
            
            for entity in self.entities:
                if entity.state == "dead":
                    self.entities.remove(entity)
                else:
                    entity.doSomething()
                    
            for snake in self.snakes:
                if snake.state == "dead":
                    self.snakes.remove(snake)
                else:
                    snake.doSomething()
                
         
            pygame.display.flip()
        


game = GameState(m * 6, 6 * n, WIDTH, 100, (40, 0), WALL_COLOR, FILL_COLOR)
game.run()
