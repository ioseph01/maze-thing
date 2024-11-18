
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
    

    def getStart(self):
        return self.start
        

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
            
            
class Pellet(object):
    
    def __innit__ (self, x, y, screen):
        self.screen
        self.x = x
        self.y = y
        self.color = (255, 255, 0)
        
    def change_color(self):
        self.color = (r.randint(0, 255), r.randint(0, 255), r.randint(0, 255))

    def render(self):
        pygame.draw.circle(self.screen, self.color, self.x, self.y)
        


class Player(object):
    
    def __init__(self, maze):
        self.rect = pygame.Rect((maze.cols - 2) * WIDTH, WIDTH * (maze.rows - 2), WIDTH // 2, WIDTH // 2)
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
        
        for row in self.maze.layout:
            for wall in row:
                if wall != None:
                    
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


    def trace(self, maze):
        x = 0 + self.rect.x // WIDTH
        y = 0 + self.rect.y // WIDTH
        print(x,y)
        
        
        
        visited = {(x,y)}
        paths = [[(x, y)]]
        
        while len(paths) > 0:
            print(len(visited))
            current = paths.pop(-1)
            x,y = current[-1]
            # print(f"Checking {x,y}")
            
           
            if x == 1 and y == 0:
                self.state = True
                self.path = current
                # print(current)
                self.x, self.y = self.path.pop(0)
                return

                
            
            visited.add((x, y))
            
            if x + 1 < len(maze[0]) and (x + 1, y) not in visited:
            
                try:
                    if maze[y][x + 1].state != "alive":
                        paths.append(current + [(x + 1, y)])
                   
                    
                except IndexError:
                    raise IndexError(f"{x+1}, {y}")
                
            if y + 1 < len(maze) and (x, y + 1) not in visited:
                if maze[y + 1][x].state != "alive":

                    paths.append(current + [(x, y + 1)])
                    
            if x - 1 > -1 and (x - 1, y) not in visited:
                if maze[y][x - 1].state != "alive":
              
                    paths.append(current + [(x - 1, y)])
                   
                   
         
                
            if y - 1 > -1 and (x, y - 1) not in visited:
                # print(maze[y - 1][x].state, x, y- 1 )
                if maze[y - 1][x].state != "alive":
       
                    paths.append(current + [(x, y - 1)])
                    
            
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
        self.screen = pygame.display.set_mode((WIDTH * (self.maze.cols) , (self.maze.rows) * WIDTH))
        self.player = Player(self.maze) 
        self.end_rect = pygame.Rect(1 * WIDTH, 0 * WIDTH, WIDTH, WIDTH)
                                    
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
                      
                        self.player.trace(self.maze.layout)

                    
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
            pygame.display.flip()
        


game = GameState(m * 6, 6 * n, WIDTH, 100, (50, 10), WALL_COLOR, FILL_COLOR)
game.run()


