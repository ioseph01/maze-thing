
import random as r
import os
import pygame
import math
import copy


WIDTH = 8
m,n = 12, 10
SPARSITY = 50

WALL_COLOR = (r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))
FILL_COLOR = (r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))
 

class Maze(object):
    def __init__(self, col, row, SPARSITY):
        if row % 2 == 0:
            row += 1
        if col % 2 == 0:
            col += 1
                   
        self.cols = col
        self.rows = row
        self.layout = [[Wall(((i) * WIDTH, (j) * WIDTH), (WALL_COLOR)) for i in range(col)] for j in range(row)]
        
        if SPARSITY[0] < 0 and SPARSITY[1] < 0:
            self.carve(self.layout)
           
        else:
            layout1 = copy.deepcopy(self.layout)
            self.carve(layout1)
            self.carve(self.layout)
            self.combine(self.layout, layout1, SPARSITY)

      
        self.layout[0][1].kill()
        self.layout[0][1].color = (255, 0, 0)
    
        

    def combine(self, layout, other, sparsity):
        for y in range(len(layout)):
            for x in range(len(layout[y])):
                if layout[y][x].state != "alive" or "alive" != other[y][x].state and r.randrange(0, 100 ) < sparsity[0]:
                    layout[y][x].kill()
                    

                if  r.randrange(0, 100 ) < sparsity[1] and x != 0 and x != len(self.layout[0]) - 1 and y != 0 and y != len(self.layout) - 1 and x % 2 == 0 and y % 2 == 0:
                    layout[y][x].kill()
    
    
    def create_center(self):
        x = math.ceil(self.cols / 2)
        y = math.ceil(self.rows / 2)
        r = min(math.sqrt(self.rows), math.sqrt(self.cols))
        if r % 2 == 0:
            r += 1

        for j in range(-math.floor(r / 2), math.floor(r / 2) + 1):
            for i in range(-math.floor(r / 2), math.floor(r / 2) + 1):
                self.layout[y + j][x + i].kill()

                    

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
                layout[y][x].kill()
                visited.add(toVisit.pop())
                
            else:
                c1, c2 = r.choice(choices)
                toVisit.append(c1)
                layout[c2[1] ][c2[0]].kill()
               
                visited.add((x, y))
                
                
    def render(self, screen):
            for row in self.layout:
                for col in row:
                    try:
                        pygame.draw.rect(screen, col.color, col.rect)
                    except:
                        raise ValueError(f"{col.color}")
            
            
# class Pellet(object):
    
#     def __innit__ (self, x, y, screen):
#         self.screen
#         self.x = x
#         self.y = y
#         self.color = (255, 255, 0)
        
#     def change_color(self):
#         self.color = (r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))

#     def render(self):
#         pygame.draw.circle(self.screen, self.color, self.x, self.y)


class Snake(object):
    
    def __init__(self, screen, segments, color, maze, coords, scale):
        self.screen = screen
        self.color = color
        self.coords = coords
        self.maze = maze
        self.segments = [Entity(self.screen, (coords[0], coords[1]), color, maze, 100, scale) for i in range(segments)]
        self.move_tick = 0
        self.scale = scale
        self.state = "unravel"
        self.unravel_counter = 0

    def doSomething(self):
        
        self.move_tick = (self.move_tick + 1) % 2

        if self.move_tick % 2 == 0:
            if self.state != "unravel":
                coords = (self.segments[0].rect.x, self.segments[0].rect.y)
            
                for segment in range(len(self.segments)):
                    temp = (self.segments[segment].rect.x, self.segments[segment].rect.y) 
                
                    if segment == 0:
                        self.segments[segment].doSomething()
                    
                    else:
                        self.segments[segment].rect.x = coords[0]
                        self.segments[segment].rect.y = coords[1]
                    
                    coords = temp
                    
            else:
                coords = (self.segments[0].rect.x, self.segments[0].rect.y)
                for i in range(0, self.unravel_counter):
                    temp = (self.segments[i].rect.x, self.segments[i].rect.y) 
                    if i == 0:
                        self.segments[i].doSomething()
                    
                    else:
                        self.segments[i].rect.x = coords[0]
                        self.segments[i].rect.y = coords[1]
                    
                    coords = temp
                        
                        
                        
                self.unravel_counter += 1
                if self.unravel_counter == len(self.segments) - 1:
                    self.state = "searching"
                        
                    

 
            

        
        
    def render(self):
        for segment in self.segments:
            pygame.draw.rect(self.screen, segment.color, segment.rect)


class Entity(object):
    def __init__(self, screen, coords, color, maze, trace_commitment, scale : float):
        self.x, self.y = coords
        self.color = color
        self.screen = screen
        self.path = []
        self.rect = pygame.Rect(self.x, self.y, WIDTH // scale, WIDTH // scale)
        self.scale = scale
        self.tick = 0
        self.state = "alive" # chase idle scatter stunned dead
        self.maze = maze
        self.toMove = self.maze.cols // 4
        self.direction = r.choice(["north", "east", "south", "west"])
        self.target = (self.maze.rows, self.maze.cols)
        self.trace_tick = 0
        self.trace_commitment = trace_commitment / 100
        

    def get_scatter(self):
        return r.choice([(3, 3), (math.ceil(self.maze.cols / 2), 3), (self.maze.cols - 2, self.maze.rows - 2), (math.ceil(self.maze.cols / 2), self.maze.rows - 2),
         (self.maze.cols - 2 , math.ceil(self.maze.rows / 2)), (3, math.ceil(self.maze.rows / 2)), (3, self.maze.rows - 2),
        (math.ceil(self.maze.cols / 2), self.maze.rows - 2)])


    def move_single_axis(self, dx, dy):
        
        # Move the rect
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
                        
                        


    def directionMapping(self, given, value):
        directions = {"north": (0, 1), "east" : (1, 0), "south" : (0, -1), "west" : (-1, 0)}
        
        if given == "key":
            return directions[value]
        else:
            for k in directions:
                if directions[k] == value:
                    return k
        

        
        

    def trace(self, targetx, targety):
        maze = self.maze.layout
       
        x = 0 + self.rect.x // WIDTH
        y = 0 + self.rect.y // WIDTH
        
        visited = {(x,y)}
        paths = [[(x, y)]]
        
        while len(paths) > 0:
            
            current = paths.pop(-1)
            x,y = current[-1]

            if x == targetx and y == targety:
                self.state = "chase"
                
                if targetx * WIDTH == game.player.rect.x and targety * WIDTH == game.player.rect.y:
                    self.path = current
                else:
                    self.path = current[:round(len(current) * self.trace_commitment)]
                self.x, self.y = self.path.pop(0)
                try:
                    self.target = (current[-1][0], current[-1][1])
                except IndexError:
                    print("size of current is ", len(current))
                    print("this error occurs when a player is hit by an entity, should be ok")
                    exit()
                return

            visited.add((x, y))
            toAdd = {}
            
            if x + 1 < len(maze[0]) and (x + 1, y) not in visited:
            
                try:
                    if maze[y][x + 1].state != "alive":
                        k = abs(targetx - x - 1) + abs(targety - y)
                        if k not in toAdd:
                            toAdd[k] = []
                        toAdd[k].append((x + 1, y))
                     
                except IndexError:
                    raise IndexError(f"{x+1}, {y}")
                
            if y + 1 < len(maze) and (x, y + 1) not in visited:
                if maze[y + 1][x].state != "alive":
                    k = abs(targetx - x) + abs(targety - y - 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y + 1))
                    
            if x - 1 > -1 and (x - 1, y) not in visited:
                if maze[y][x - 1].state != "alive":
                    k = abs(targetx - x + 1) + abs(targety - y)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x - 1, y))
                          
            if y - 1 > -1 and (x, y - 1) not in visited:
           
                if maze[y - 1][x].state != "alive":
                    k = abs(targetx - x) + abs(targety - y + 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y - 1))

            for key in reversed(dict(sorted(toAdd.items()))):
                for val in toAdd[key]:
                    paths.append(current + [val])


    def doSomething(self):
        if self.rect.colliderect(game.player.rect):
            print("HIT!!!!!!!!!!")

        self.tick = (self.tick + 1) % 2
        if self.tick == 0:
            
            if len(self.path) > 0:
              
                if self.trace_tick == WIDTH - 1:
                    dx, dy = self.path.pop(0)
                else:
                    dx, dy = self.path[0]
                
               
                self.move_single_axis(dx - self.x, dy - self.y)
                
                if self.trace_tick == WIDTH - 1:
                    self.x, self.y = dx, dy
                self.trace_tick = (self.trace_tick + 1) % WIDTH
                
            elif abs(self.rect.x - game.player.rect.x) < 120 and abs(self.rect.y - game.player.rect.y) < 120:
                self.trace(game.player.rect.x // WIDTH, game.player.rect.y // WIDTH)
                print("TRACKING", self.rect.x, game.player.rect.x, self.rect.y, game.player.rect.y, abs(self.rect.x - game.player.rect.x), abs(self.rect.y - game.player.rect.y))
            
                
            else:
                x, y = self.get_scatter()
                self.target = (x, y)
                print(f"SCATTER{x, y}")
                self.trace(x, y)
           
                


        pygame.draw.rect(self.screen, self.color, self.rect)

        
                    
 



class Player(object):
    
    def __init__(self, maze):
        self.rect = pygame.Rect((maze.cols - 2) * WIDTH, WIDTH * (maze.rows - 2), WIDTH // 1, WIDTH // 1)
        self.color = (255, 200, 0)
        self.state = False
        self.path = []
        self.x = None
        self.y = None
        self.maze = maze

    def move(self, dx, dy):
        # Move each axis separately. Note that this checks for collisions both times.
        if self.state and len(self.path) > 0:
            dx, dy = self.path.pop(0)
            tempx, tempy = dx, dy
            dx = (dx - self.x)  * WIDTH
            dy = (dy - self.y) * WIDTH
            self.x, self.y = tempx, tempy


        if dx != 0:
            self.move_single_axis(dx, 0)
        if dy != 0:
            self.move_single_axis(0, dy)
            
   
    def move_single_axis(self, dx, dy):
        
        # Move the rect
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


    def trace(self, maze, targetx, targety):
        x = 0 + self.rect.x // WIDTH
        y = 0 + self.rect.y // WIDTH
        
        visited = {(x,y)}
        paths = [[(x, y)]]
        
        while len(paths) > 0:
            
            current = paths.pop(-1)
            x,y = current[-1]

            if x == 1 and y == 0:
                self.state = True
                self.path = current
                print(current)
                self.x, self.y = self.path.pop(0)
                return

            visited.add((x, y))
            toAdd = {}
            
            if x + 1 < len(maze[0]) and (x + 1, y) not in visited:
            
                try:
                    if maze[y][x + 1].state != "alive":
                        k = abs(targetx - x - 1) + abs(targety - y)
                        if k not in toAdd:
                            toAdd[k] = []
                        toAdd[k].append((x + 1, y))
                     
                except IndexError:
                    raise IndexError(f"{x+1}, {y}")
                
            if y + 1 < len(maze) and (x, y + 1) not in visited:
                if maze[y + 1][x].state != "alive":
                    k = abs(targetx - x) + abs(targety - y - 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y + 1))
                    
            if x - 1 > -1 and (x - 1, y) not in visited:
                if maze[y][x - 1].state != "alive":
                    k = abs(targetx - x + 1) + abs(targety - y)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x - 1, y))
                          
            if y - 1 > -1 and (x, y - 1) not in visited:
           
                if maze[y - 1][x].state != "alive":
                    k = abs(targetx - x) + abs(targety - y + 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y - 1))

            for key in reversed(dict(sorted(toAdd.items()))):
                for val in toAdd[key]:
                    paths.append(current + [val])
        
                    
            
# Nice class to hold a wall rect
class Wall(object):
    
    def __init__(self, pos, color):
        # walls.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], WIDTH, WIDTH)
        self.color = color
        self.state = "alive"

    def revive(self):
        self.color = WALL_COLOR
        self.state = "alive"

    def kill(self):
        self.color = FILL_COLOR
        self.state = "dead"



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

        self.maze = Maze(m, n, SPARSITY)
        self.maze.create_center()
        self.screen = pygame.display.set_mode((WIDTH * (self.maze.cols) , (self.maze.rows) * WIDTH))
        self.player = Player(self.maze) 
        self.end_rect = pygame.Rect(1 * WIDTH, 0 * WIDTH, WIDTH, WIDTH)
        self.entities = [Entity(self.screen, (m * WIDTH // 2, n * WIDTH // 2), (0, 255, 0), self.maze, r.randint(30, 80), 2) for i in range(40)]
        self.snake = Snake(self.screen, 500, (0, 0, 0), self.maze, (m * WIDTH // 2, n * WIDTH // 2), 1)
                                    
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


                    if e.key == pygame.K_SPACE:
                      
                        self.player.trace(self.maze.layout, 0, 1)

                    
                    if e.key == pygame.K_c:
                        self.player.change_color()
    
        # Move the player if an arrow key is pressed

            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.player.move(-2, 0)
            if key[pygame.K_RIGHT]:
                self.player.move(2, 0)
            if key[pygame.K_UP]:
                self.player.move(0, -2)
            if key[pygame.K_DOWN]:
                self.player.move(0, 2)
        
            if self.player.rect.colliderect(self.end_rect):
                self.running = False
                break
    
            self.screen.fill(FILL_COLOR)
            
            pygame.draw.rect(self.screen, (255, 0, 0), self.end_rect)
            self.maze.render(self.screen)
            pygame.draw.rect(self.screen, self.player.color, self.player.rect)
            for entity in self.entities:
                entity.doSomething()
                
            self.snake.doSomething()
            self.snake.render()
            pygame.display.flip()
        


game = GameState(m * 6, 6 * n, WIDTH, 100, (80, 20), WALL_COLOR, FILL_COLOR)
game.run()


