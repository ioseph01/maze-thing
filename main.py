
import random as r
import os
import pygame
import math
import copy


WIDTH = 16
m,n = 6, 6
SPARSITY = 50

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
        self.state = state
        self.direction = direction
        self.coords = coords
        self.rect = pygame.Rect(coords[0], coords[1], WIDTH * scale, WIDTH * scale)
        self.scale = scale
        

    def doSomething(self):
        return NotImplementedError
    

    def render(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
    

    def move_single_axis(self, dx, dy):
        return NotImplementedError
        
    


class Bullet(Unit):
    
    def __init__(self, screen, maze, coords, direction, state):
        if state != "powered":
            color = game.player.color
        else:
            color = (255,255,255)
        super(Bullet, self).__init__( screen, maze, color, coords, state, direction, 1)
       
        
        

    def doSomething(self):
        if self.state != "dead":
            toMove = directionCoordMap(self.direction)
            self.move_single_axis(toMove[0] * 2, 2 * toMove[1])
            self.render()
    

    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

        for j in range(self.rect.y // WIDTH - 1, 2 + self.rect.y // WIDTH):
            for i in range(self.rect.x // WIDTH - 1, self.rect.x // WIDTH + 2):
                
                wall = self.maze.layout[j][i][0]
                if self.rect.colliderect(wall.rect) and wall.state == "alive":
                    self.state = "dead"
                    
        for trap in game.traps:
            if trap.rect.colliderect(self.rect):
                self.state = "dead"
                trap.hp -= 1
                    


class Snake(Unit):
    
    def __init__(self, screen, maze, color, coords, state, scale, segments, step):
        super(Snake, self).__init__(screen, maze, color, coords, state, "north", scale)
        self.unravel_counter = 0
        self.step = step
        self.move_tick = 0
        self.destroy_idx = 0

        if type(segments) == list:
            self.segments = segments
        elif type(segments) == int:
            self.segments = [Entity(self.screen, self.maze, self.coords, self.color, r.randint(60, 90), self.scale, self.step, 0) for i in range(segments)]
       
            

    def doSomething(self):
       
        if self.state == "dead":
            return
        
        elif len(self.segments) == 0:
            self.state = "dead"
            return
            
        elif self.state == "dying":
            self.render()
            self.segments.pop(self.destroy_idx)
            game.score += 1
            if len(self.segments) <= 2:
                return
            
        if self.unravel_counter >= len(self.segments):
            self.unravel_counter = len(self.segments)
            if self.state != "dying":
                self.state = "searching"
            
        
            
        self.render()
        self.move_tick = (self.move_tick + 1) % 2
      
        if self.move_tick % 2 == 0:
            
            coords = (self.segments[0].rect.x, self.segments[0].rect.y)
                
            for i in range(self.unravel_counter):
                if self.segments[i].state == "dead":
                    self.segments.pop(0)
                    game.score += 1
                    return
                  
                for bullet in game.player.bullets:
                    if self.segments[i].rect.colliderect(bullet.rect):
                        game.score += 1
                        self.bulletCollision(bullet, i)
                        return
                        
                temp = (self.segments[i].rect.x, self.segments[i].rect.y)
                if i == 0:
                    self.segments[i].doSomething()
                else:
                    self.segments[i].rect.x, self.segments[i].rect.y = coords
                    if self.segments[i].rect.colliderect(game.player.rect):
                        print("Hit!!!!!!!")
                        game.player.hits += 1
                            
                coords = temp
        self.unravel_counter += 1
        if self.unravel_counter >= len(self.segments) and self.state != "dying":
            self.state = "searching"


    def bulletCollision(self, bullet, i):
        self.segments.remove(self.segments[i])
        
        if i > 0 and i < len(self.segments) - 1:
            if bullet.state == "powered":
                state = "dying"
                self.state = state
                self.destroy_idx = -1
            else:
                state = "searching"
            
            game.snakes.append(Snake(self.screen, self.maze, self.color, (WIDTH * self.rect.x // WIDTH, WIDTH * self.rect.y // WIDTH), state, self.scale, self.segments[i:], self.step))
            self.segments = self.segments[:i]
            self.unravel_counter += 1
            
        elif bullet.state == "powered":
            self.state = "dying"
            if i >= len(self.segments):
                self.destroy_idx = -1
            elif i == 0:
                self.destroy_idx = 0
            
        bullet.state = "dead"
       

    def render(self):
        for i in self.segments:
            i.render()
                    

class Player(Unit):
    
    def __init__(self, screen, maze, padding):
        super(Player, self).__init__(screen, maze, (255, 200, 0), (padding + (maze.cols - 2) * WIDTH, padding +(maze.rows - 2) * WIDTH), "alive", "north", 1)
        self.bullets = []
        self.mines = []
        self.stun_tick = 0
        self.fire_tick = 0
        self.clear_tick = 0
        self.hits = 0
        self.paths = []
        

    def clear_traps(self):
        if self.fire_tick != 0:
            return
        
        game.inventory[3] -= 1
        x,y = self.rect.x // WIDTH, self.rect.y // WIDTH
        visited = set((x, y))
        toVisit = [[(x, y)]]
        print("FINDING")
        while len(toVisit) > 0:
            
            current = toVisit.pop(0)
            temp = len(toVisit)
            x, y = current[-1]
            visited.add((x, y))
            if len(current) >= 15:
                visited.add((current[0], current[1]))
                self.paths.append(current)
                continue
            
            if self.maze.layout[y + 1][x][0].state != "alive" and (x, y + 1) not in visited:
                toVisit.append(current + [(x, y + 1)])
            if self.maze.layout[y - 1][x][0].state != "alive" and (x, y - 1) not in visited:
                toVisit.append(current + [(x, y - 1)])
            if self.maze.layout[y][x + 1][0].state != "alive" and (x + 1, y) not in visited:
                toVisit.append(current + [(x + 1, y)])
            if self.maze.layout[y][x - 1][0].state != "alive" and (x - 1, y) not in visited:
                toVisit.append(current + [(x - 1, y)])
            if temp == len(toVisit):
                self.paths.append(current)
         
        self.fire_tick = 30
        # print(self.paths)
        
            


    def shoot(self, state):
        if self.fire_tick == 0:
            self.bullets.append(Bullet(self.screen, self.maze, (self.rect.x, self.rect.y), self.direction, state))
            self.fire_tick = 25
            if state == "powered":
                game.inventory[1] -= 1
            else:
                game.inventory[0] -= 1


    def lay_mine(self, hp):
        if self.fire_tick == 0:
            self.mines.append(Mine((self.rect.x, self.rect.y), self.color, hp))
            self.fire_tick = 30
            game.inventory[2] -= 1
        

    def doSomething(self):
        self.render()
        for bullet in self.bullets:
            if bullet.state == "dead":
                self.bullets.remove(bullet)
                
            else:
                bullet.doSomething()
                
        for mine in self.mines:
            if mine.state == "dead":
                self.mines.remove(mine)
            else:
                mine.doSomething()
                

        for trap in game.traps:
            if self.rect.colliderect(trap.rect) and trap.state == "alive":
                self.stun_tick += 20
                trap.hp -= 1
                            

        if self.stun_tick > 0:
            print(self.stun_tick)
            self.stun_tick -= 1
            
        if self.fire_tick > 0:
            self.fire_tick -= 1
            
        if len(self.paths) > 0:
            
            if self.clear_tick == 0:
                for path in self.paths:
                    if len(path) == 0:
                        self.paths.remove(path)
                    else:
                        x, y = path.pop(0)
                     
                        if len(self.maze.layout[y][x]) >= 2:
                            self.maze.layout[y][x][-1].state = "dead"
                            self.maze.layout[y][x].pop(-1)

            self.clear_tick = (self.clear_tick + 1) % 2
        
                


    def move_single_axis(self, dx, dy):
        if self.stun_tick > 0:
            return
        
        self.rect.x += dx
        self.rect.y += dy

        for j in range(self.rect.y // WIDTH - 1, 2 + self.rect.y // WIDTH):
            for i in range(self.rect.x // WIDTH - 1, self.rect.x // WIDTH + 2):
                
                wall = self.maze.layout[j][i][0]
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
    
    def __init__(self, screen, maze, coords, color, trace_commitment, scale, step, build_rate):
        super(Entity, self).__init__(screen, maze, color, coords, "alive", r.choice(["north", "east", "south", "west"]), scale)
        self.path = []
        self.step = step
        self.trace_commitment = trace_commitment / 100
        self.target = (self.maze.rows, self.maze.cols)
        self.trace_tick = 0
        self.tick = 0
        self.build_rate = 1000 * build_rate
        

    def get_scatter(self):
        return r.choice([(3, 3), (math.ceil(self.maze.cols / 2), 3), (self.maze.cols - 2, self.maze.rows - 2), (math.ceil(self.maze.cols / 2), self.maze.rows - 2),
         (self.maze.cols - 2 , math.ceil(self.maze.rows / 2)), (3, math.ceil(self.maze.rows / 2)), (3, self.maze.rows - 2),
        (math.ceil(self.maze.cols / 2), self.maze.rows - 2)])
    

    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
        for j in range(self.rect.y // WIDTH - self.scale, self.scale + 1 + self.rect.y // WIDTH):
            for i in range(self.rect.x // WIDTH - self.scale, self.rect.x // WIDTH + self.scale + 1):
                
                wall = self.maze.layout[j][i][0]
                if self.rect.colliderect(wall.rect) and wall.state == "alive":
                    if dx > 0: # Moving right; Hit the left side of the wall
                        self.rect.right = wall.rect.left
                        
                    elif dx < 0: # Moving left; Hit the right side of the wall
                        self.rect.left = wall.rect.right
                        
                    if dy > 0: # Moving down; Hit the top side of the wall
                        self.rect.bottom = wall.rect.top
                       
                    elif dy < 0: # Moving up; Hit the bottom side of the wall
                        self.rect.top = wall.rect.bottom
                        

    def mineDetect(self):
        for mine in game.player.mines:
            if self.rect.colliderect(mine.rect) and mine.state != "dead":
                mine.hp -= 1
                self.state = "dead"
    
    
    def bulletDetect(self):
        for bullet in game.player.bullets:
            if self.rect.colliderect(bullet.rect):
                print("SHOT!!!!")
                self.state = "dead"
                bullet.state = "dead"
        
                
    def lay_trap(self):
            if r.randint(1, 1000) < self.build_rate and self.trace_tick == 0 and len(self.maze.layout[self.rect.y // WIDTH][self.rect.x // WIDTH]) < 2:
                game.traps.append(Mine((self.rect.x, self.rect.y), game.wall_color, 1))
                self.maze.layout[self.rect.y // WIDTH][self.rect.x // WIDTH].append(game.traps[-1])
        

    def move_path(self):
        if self.trace_tick == WIDTH // self.step - 1:
            dx, dy = self.path.pop(0)
                    
        else:
            dx, dy = self.path[0]
                    
        self.move_single_axis(self.step * (dx - self.coords[0]), self.step * (dy - self.coords[1]))
                
        if self.trace_tick == WIDTH // self.step - 1:
            self.coords = (dx, dy)
                    
        self.trace_tick = (self.trace_tick + 1) % (WIDTH // self.step)
                


    def doSomething(self):
       
        self.render()
        
        if self.rect.colliderect(game.player.rect):
            print("HIT!!!!!!!")
            game.player.hits += 1
            
        self.bulletDetect()
        self.mineDetect()
      
        if self.tick == 0:

            if len(self.path) > 0:
                self.move_path()

            elif abs(self.rect.x - game.player.rect.x) < 120 and abs(self.rect.y - game.player.rect.y) < 120:
                self.trace(game.player.rect.x // WIDTH, game.player.rect.y // WIDTH)
                
            else:
                x, y = self.get_scatter()
                self.target = (x, y)
                self.trace(x, y)
                
        self.tick = (self.tick + 1) % 2
        
    

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
            
                if self.maze.layout[y][x + 1][0].state != "alive":
                    k = abs(target_x - x - 1) + abs(target_y - y)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x + 1, y))
                     
            if y + 1 < len(self.maze.layout) and (x, y + 1) not in visited:
                if self.maze.layout[y + 1][x][0].state != "alive":
                    k = abs(target_x - x) + abs(target_y - y - 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y + 1))
                    
            if x - 1 > -1 and (x - 1, y) not in visited:
                if self.maze.layout[y][x - 1][0].state != "alive":
                    k = abs(target_x - x + 1) + abs(target_y - y)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x - 1, y))
                          
            if y - 1 > -1 and (x, y - 1) not in visited:
           
                if self.maze.layout[y - 1][x][0].state != "alive":
                    k = abs(target_x - x) + abs(target_y - y + 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y - 1))

            for key in reversed(dict(sorted(toAdd.items()))):
                for val in toAdd[key]:
                    paths.append(current + [val])
            



class Giant(Entity):
    
    def __init__(self, screen, maze, coords, color, trace_commitment, scale, step, hp):
        super(Giant, self).__init__(screen, maze, coords, color, trace_commitment, scale, step, 0)
        self.hp = hp

        
    def bulletDetect(self):
        for bullet in game.player.bullets:
            
            if self.rect.colliderect(bullet.rect):
                bullet.state = "dead"
                print("Giant SHOT!!!!")
                self.step *= 7/5
                self.hp -= 1
                self.scale += 1
                self.rect = pygame.Rect(self.rect.x, self.rect.y , WIDTH * self.scale, WIDTH * self.scale)
                return
                

    def mineDetect(self):
        for mine in game.player.mines:
            if self.rect.colliderect(mine.rect):
                self.hp -= 1
                mine.hp -= 1
                self.scale += 1
                self.rect = pygame.Rect(self.rect.x, self.rect.y , WIDTH * self.scale, WIDTH * self.scale)
                return
     
    
 
    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
  
        for j in range(self.rect.y // WIDTH - self.scale, self.scale + 1 + self.rect.y // WIDTH):
            for i in range(self.rect.x // WIDTH - self.scale, self.rect.x // WIDTH + self.scale + 1):
              
                if i > -1 and i < (len(self.maze.layout[0])) and j < (len(self.maze.layout)) and j > -1:
                    wall = self.maze.layout[j][i][0]
                    if self.rect.colliderect(wall.rect) and wall.state == "alive":
                        
                        if i == len(self.maze.layout[0]) - 1:
                            self.rect.right = wall.rect.left
                      
                        elif i == 0:
                            self.rect.left = wall.rect.right
              
                        
                        elif j == len(self.maze.layout) - 1:
                            self.rect.bottom = wall.rect.top
                       
                        elif j == 0:
                            self.rect.top = wall.rect.bottom
                        else: 
                            wall.die()

        
    def doSomething(self):
        if self.hp <= 0:
            self.state = "dead"
            return
        else:
            super().doSomething()
        
        

class Builder(Entity):
    
    def doSomething(self):
        
        if self.state != "dead":
            self.lay_trap()
            super().doSomething()
            

class Stalker(Giant):
    
    def __init__(self, screen, maze, coords, color, trace_commitment, scale, step, hp):
        super(Stalker, self).__init__(screen, maze, coords, color, trace_commitment, scale, step, hp)
        self.hide_tick = 0
   
    def bulletDetect(self):
        if self.hp == 0:
            self.state = "dead"
        else:
            for bullet in game.player.bullets:
                if self.rect.colliderect(bullet.rect):
                    self.hp -= 1
                    bullet.state = "dead"
                    return

    
    def doSomething(self):
        
        if self.state != "dead":
            if abs(self.rect.x - game.player.rect.x) < 100 and abs(self.rect.y - game.player.rect.y) < 100 and self.hide_tick == 0:
                if self.state != "hiding":
                    self.color = game.wall_color
                    self.state = "hiding"
                    print(self.rect.x, self.rect.y)
                else:
                    self.bulletDetect()
                    self.render()
                    self.hide_tick = self.hide_tick - 1 if self.hide_tick > 0 else 0
                    if self.rect.colliderect(game.player.rect):
                        print("HIT!!!!!!!")
                        game.player.hits += 1
                        self.color = (0,255,0)
                        self.state = "alive"
                        self.hide_tick = 30    
                    
                    
            else:
                self.color = (0, 255, 0)
                self.state = "alive"
                super().doSomething()
                self.hide_tick = self.hide_tick - 1 if self.hide_tick > 0 else 0
                
                
                


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
        


class Mine(Wall):
    
    def __init__(self, coords, color, hp):
        super(Mine, self).__init__(coords, color)
        self.hp = hp
        
    def doSomething(self):
        if self.hp <= 0:
            self.die()
        else:
            self.render()
        
        

class Maze(object):
    
    def __init__(self, row, col, sparsity, padding, WALL_COLOR):
        if row % 2 == 0:
            row += 1
            
        if col % 2 == 0:
            col += 1
            
        self.cols = col
        self.rows = row
        self.layout = [[[Wall((i * WIDTH + padding, padding + j * WIDTH), WALL_COLOR)] for i in range(col)] for j in range(row)]
        
        if sparsity[0] <= 0 and sparsity[1] <= 0:
            self.carve(self.layout)
            
        else:
            temp = copy.deepcopy(self.layout)
            self.carve(temp)
            self.carve(self.layout)
            self.combine(self.layout, temp, sparsity)
            
        self.layout[0][1][0].die()
        self.padding = padding
        


    def combine(self, layout, other, sparsity):
      
        for y in range(len(layout)):
            for x in range(len(layout[y])):
                if layout[y][x][0].state != "alive" or "alive" != other[y][x][0].state and r.randint(0, 100) < sparsity[0]:
                    layout[y][x][0].die()
                    

                if  r.randint(0, 100 ) < sparsity[1] and x != 0 and x != len(self.layout[0]) - 1 and y != 0 and y != len(self.layout) - 1 and x % 2 == 0 and y % 2 == 0:
                    layout[y][x][0].die()
        

    def create_center(self):
        x = math.ceil(self.cols / 2)
        y = math.ceil(self.rows / 2)
        r = min(math.sqrt(self.rows), math.sqrt(self.cols))
        if r % 2 == 0:
            r += 1

        for j in range(-math.floor(r / 2), math.floor(r / 2) + 1):
            for i in range(-math.floor(r / 2), math.floor(r / 2) + 1):
                self.layout[y + j][x + i][0].die()
                

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
                layout[y][x][0].die()
                visited.add(toVisit.pop())
                
            else:
                c1, c2 = r.choice(choices)
                toVisit.append(c1)
                layout[c2[1] ][c2[0]][0].die()
               
                visited.add((x, y))
                

    def doSomething(self):
        self.render()
                
        
    def render(self):
        for row in self.layout:
            for col in row:
                col[0].render()
                

class GameState:
    def __init__(self, m, n, WDITH, PADDING, SPARSITY, Fill_color):

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption("Get to the red square!")
        self.clock = pygame.time.Clock()
        self.m = m
        self.n = n
        
        self.width = WIDTH
        self.sparsity = SPARSITY
        self.padding = PADDING
        self.wall_color = (r.randint(0,255),r.randint(0,255),r.randint(0,255))
        self.fill_color = Fill_color

        self.maze = Maze(m, n, self.sparsity, self.padding, self.wall_color)
        self.maze.create_center()
        self.screen = pygame.display.set_mode((WIDTH * (self.maze.cols) + 18 * PADDING, 2 * PADDING + (self.maze.rows) * WIDTH))
        self.end_rect = pygame.Rect(1 * WIDTH + PADDING, 0 * WIDTH, WIDTH, WIDTH)
        
        self.entities = [Stalker(self.screen, self.maze, (PADDING + m * WIDTH // 2, PADDING + n * WIDTH // 2), (0, 255, 0), 20, 1, 2, 2) for i in range(1)]
        for i in range(0):
            self.entities.append(Giant(self.screen, self.maze, (PADDING + m * WIDTH // 2, PADDING + n * WIDTH // 2), (0, 255, 0), r.randint(60,80), 1, 2, 3))
        
        self.snakes = [Snake(self.screen, self.maze, (0, 255, 0), (PADDING + m * WIDTH // 2, PADDING + n * WIDTH // 2), "unravel", 1, 100, 8) for i in range(0)]
        self.traps = []
        # self.snake = Snake(self.screen, 500, self.entities[0].color, self.maze, (m * WIDTH // 2, n * WIDTH // 2), 2, 4)
        self.player = Player(self.screen, self.maze, PADDING) 
        self.inventory = [99, 5, 5, 99] # bullets,powered,mines,trap-clear
       
        self.font = pygame.font.Font("PressStart2P-Regular.ttf", 15)
        
        self.score = 0
        self.state = None
        self.lives = 100
        self.level = 0
        
        self.running = True
        

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
            temp = copy.deepcopy(self.maze)
            inv = copy.deepcopy(self.inventory)
            print(self.level)
            x = self.run()
            if x >= 1:
                self.score += x // 2 * self.level
                self.wall_color = (r.randint(0,255),r.randint(0,255),r.randint(0,255))
                self.maze = Maze(self.m, self.n, (r.randint(0, 100), r.randint(0, 100)), self.padding, self.wall_color)
                self.maze.create_center()
                self.level += 1
                self.inventory = [i + self.level // 2 if i + self.level // 2 < 99 else 99 for i in self.inventory]
                print(self.inventory)
                
            elif x == 0:
                self.lives -= 1
                self.maze = temp
                self.inventory = inv
                
            elif x == -1:
                break
                    
            self.entities = [Builder(self.screen, self.maze, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 80, 1, 2, .25) for i in range(self.calc_cells())]
            for i in range(self.calc_giants()):
                self.entities.append(Giant(self.screen, self.maze, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), r.randint(60, 80), 1, 2, 3))
            for i in range(3 * self.level // 2):
                self.entities.append(Stalker(self.screen, self.maze, (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), (0, 255, 0), 20, 1, 2, 2))
        
            self.snakes = [Snake(self.screen, self.maze, (0, 255, 0), (self.padding + self.m * WIDTH // 2, self.padding + self.n * WIDTH // 2), "unravel", 1, self.level, 8) for i in range(self.calc_snakes())]
            self.traps = []
            # self.snake = Snake(self.screen, 500, self.entities[0].color, self.maze, (m * WIDTH // 2, n * WIDTH // 2), 2, 4)
            self.player = Player(self.screen, self.maze, self.padding) 
            
     

        pygame.quit()
            
                
                
    def run(self):
        self.running = True
        while self.running:
    
            self.clock.tick(60)
            if self.player.hits >= 25:
                return 0
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        return -1
                    if e.key == pygame.K_t:
                        self.player.trace(self.maze.layout, 0, 1)
                    if e.key == pygame.K_1 and self.inventory[0] > 0:
                        self.player.shoot("alive")
                    if e.key == pygame.K_2 and self.inventory[1] > 0:
                        self.player.shoot("powered")
                    if e.key == pygame.K_3 and self.inventory[2] > 0:
                        self.player.lay_mine(5)
                    if e.key == pygame.K_c:
                        self.player.change_color()
                    if e.key == pygame.K_4 and self.inventory[3] > 0:
                        self.player.clear_traps()

                      
    
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
                return 30 - self.player.hits
    
            self.screen.fill(FILL_COLOR)
     
            self.maze.render()     
            self.player.doSomething()
            
            for entity in self.entities:
                if entity.state == "dead":
                    self.entities.remove(entity)
                    self.score += entity.scale
                else:
                    entity.doSomething()
                    
            for snake in self.snakes:
                if snake.state == "dead":
                    self.snakes.remove(snake)
                else:
                    snake.doSomething()
                
            for trap in self.traps:
                if trap.state == "dead":
                   self.traps.remove(trap)
                else:
                    trap.doSomething()

            text = self.font.render(f"Score:{self.score}", True, (255,255,255))
            self.screen.blit(text, (WIDTH * (self.maze.cols) + self.padding * 3, 20))
            
            
            text = self.font.render(f"{100 - 4 * self.player.hits }% O:{self.inventory[0]}", True, (255,255,255))
            self.screen.blit(text, (WIDTH * (self.maze.cols) + self.padding * 3, 70))
            
            
            text = self.font.render(f"*:{self.inventory[1]} #:{self.inventory[2]}", True, (255,255,255))
            self.screen.blit(text, (WIDTH * (self.maze.cols) + self.padding * 3, 120))

            pygame.display.flip()


    

if 1:
    FILL_COLOR = (0,0,0)

game = GameState(m * 6, 6 * n, WIDTH, 10, (100, 100), FILL_COLOR)
game.start_level()


# input(f"Result : {game.player.hits} hits by enemies!")

#SPLIT GAMESTATE INTO LEVEL MANAGER - to run levels and manage enemies and such, AND GAME MANAGER - to run screen layout font other
