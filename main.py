import random as r
import os
import pygame
import math


WIDTH = 6
m,n = 15, 10

class Maze(object):
    def __init__(self, col, row):
        if row % 2 == 0:
            row += 1
        if col % 2 == 0:
            col += 1
            
        print(col, row)
            
        self.cols = col
        self.rows = row
        self.layout = [[Wall(((i + 2) * WIDTH, (j + 2) * WIDTH), (255,255,255)) for i in range(col)] for j in range(row)]
        # self.start = (math.ceil(self.cols / 2), math.ceil(self.rows / 2))
        self.start = (3,3)
        self.carve()
        self.layout[0][1].delete()
        self.layout[0][1].color = (255, 0, 0)
        


    

    def getStart(self):
        return self.start
        

    def carve(self):
       
        
        visited = set()
        toVisit = [self.start]
        last = self.start
        print(last)
        
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
                
                
                self.layout[y][x].delete()
                visited.add(toVisit.pop())
                
            else:
                c1, c2 = r.choice(choices)
                toVisit.append(c1)
                self.layout[c2[1] ][c2[0]].delete()
               
                visited.add((x, y))
                
            last = (x,y)
                
                
    def render(self):
            for row in self.layout:
                for col in row:
                    if col != None:
                        pygame.draw.rect(screen, col.color, col.rect)
            
            
            


# Class for the orange dude
class Player(object):
    
    def __init__(self):
        self.rect = pygame.Rect((maze.cols) * WIDTH, WIDTH * (maze.rows), WIDTH // 1, WIDTH // 1)

        self.state = False
        self.path = []
        self.x = None
        self.y = None

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
        
        # x = self.rect.x // WIDTH
        # y = self.rect.y // WIDTH
        # print(x,y)

        # If you collide with a wall, move out based on velocity
        for row in maze.layout:
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
                    

    def trace(self, maze):
        x = -2 + self.rect.x // WIDTH
        y = -2 + self.rect.y // WIDTH
        print(x,y)
        
        
        
        visited = {(x,y)}
        paths = [[(x, y)]]
        
        while len(paths) > 0:
            current = paths.pop(0)
            x,y = current[-1]
            print(f"Checking {x,y}")
            
           
            if x == 1 and y == 0:
                self.state = True
                self.path = current
                print(current)
                self.x, self.y = self.path.pop(0)
             
                print(self.x, self.y)
                return

                
            
            visited.add((x, y))
            
            if x + 1 < len(maze[0]) and (x + 1, y) not in visited:
            
                try:
                    if maze[y][x + 1].state != "alive":
                        paths.append(current + [(x + 1, y)])
                   
                    
                except IndexError:
                    raise IndexError(f"{x+1}, {y}")
                    
            if x - 1 > -1 and (x - 1, y) not in visited:
                if maze[y][x - 1].state != "alive":
              
                    paths.append(current + [(x - 1, y)])
                   
                   
         
                
            if y - 1 > -1 and (x, y - 1) not in visited:
                print(maze[y - 1][x].state, x, y- 1 )
                if maze[y - 1][x].state != "alive":
       
                    paths.append(current + [(x, y - 1)])
                    
            
                    
            if y + 1 < len(maze) and (x, y + 1) not in visited:
                if maze[y + 1][x].state != "alive":

                    paths.append(current + [(x, y + 1)])
                    

                 
 
    
              

# Nice class to hold a wall rect
class Wall(object):
    
    def __init__(self, pos, color):
        # walls.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], WIDTH, WIDTH)
        self.color = color
        self.state = "alive"


    def delete(self):
        self.color = (0,0,0)
        self.state = "dead"

# Initialise pygame
os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()



clock = pygame.time.Clock()
walls = [] # List to hold the walls



# Holds the level layout in a list of strings.
# level = [
# "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
# "W      W                       WWWWWWW",
# "W         WWWWWW   WWWWW  WWW        W",
# "W   WWWW       W       WWW WWWWWW WWWW",
# "W   W        WWWW  WWWWWW  WWWWW  WWWW",
# "W WWW  WWWW        W   W W  WW      WW",
# "W   W     W W      WWW W WW WWWW  WWWW",
# "W   W     W   WWW WWWW W    W WWW WWWW",
# "W   WWW WWW   W W  WWW WWWWW   WW WWWW",
# "W     W   W   W W       W           WW",
# "WWW   W   WWWWW W  WW WWWWWWWWWW WWWWW",
# "W W      WW        WW      WWW   WWWWW",
# "W W   WWWW   WWW   WW  WW  WW  W  W WW",
# "W     W    E   W   WWWWWWW      WW  WW",
# "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
# ]



# Parse the level string above. W = wall, E = exit
# x = y = 0
# for row in level:
#     for col in row:
#         if col == "W":
#             Wall((x, y))
#         if col == "E":
#             end_rect = pygame.Rect(x, y, WIDTH, WIDTH)
#         x += WIDTH
#     y += WIDTH
#     x = 0
    
# Set up the display
pygame.display.set_caption("Get to the red square!")

# screen = pygame.display.set_mode((len(level[0]) * WIDTH, len(level) * WIDTH))


# maze = Maze(m, n)
# screen = pygame.display.set_mode((WIDTH * (maze.cols + 4) , (4 + maze.rows) * WIDTH))
# player = Player() # Create the player
# end_rect = pygame.Rect(3 * WIDTH , 2 * WIDTH, WIDTH, WIDTH)

# print(len(level[0]), len(level))

# for l in range(len(level)):
#     for i in range(len(level[l])):
#         if level[l][i] == "E":
#             print(i, l)
            
# print(len(walls))

# running = True
# while running:
    
#     clock.tick(60)
    
#     for e in pygame.event.get():
#         if e.type == pygame.QUIT:
#             running = False
#         if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
#             running = False

#         if e.type == pygame.KEYDOWN:
#             if e.key == pygame.K_SPACE:
#                 print("'SPACE' HIT")
#                 player.trace(maze.layout)
                
#             if e.key == pygame.K_a:
                
#                 player.move(0,0)
#                 print(player.rect.x, player.rect.y)
    
#     # Move the player if an arrow key is pressed

#     key = pygame.key.get_pressed()
#     if key[pygame.K_LEFT]:
#         player.move(-1, 0)
#     if key[pygame.K_RIGHT]:
#         player.move(1, 0)
#     if key[pygame.K_UP]:
#         player.move(0, -1)
#     if key[pygame.K_DOWN]:
#         player.move(0, 1)
        
#     if key[pygame.K_z]:
#         m.p()
        
 

    
    
#     # Just added this to make it slightly fun ;)
#     if player.rect.colliderect(end_rect):
#         raise SystemExit( "You win!")
    
#     # Draw the scene
#     screen.fill((0, 0, 0))
#     # for wall in walls:
#     #     pygame.draw.rect(screen, (255, 255, 255), wall.rect)
#     pygame.draw.rect(screen, (255, 0, 0), end_rect)
#     maze.render()
#     pygame.draw.rect(screen, (255, 200, 0), player.rect)
#     pygame.display.flip()
    

for l in range(1,65 // WIDTH):
    
    maze = Maze(m * l * 2, l * n)
    screen = pygame.display.set_mode((WIDTH * (maze.cols + 4) , (4 + maze.rows) * WIDTH))
    player = Player() # Create the player
    end_rect = pygame.Rect(3 * WIDTH , 2 * WIDTH, WIDTH, WIDTH)


        
    running = True
    while running:
    
        clock.tick(60)
    
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    print("'SPACE' HIT")
                    player.trace(maze.layout)
                
                if e.key == pygame.K_a:
                
                    player.move(-WIDTH,0)
                    print(player.rect.x, player.rect.y)
    
    # Move the player if an arrow key is pressed

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            player.move(-2, 0)
        if key[pygame.K_RIGHT]:
            player.move(2, 0)
        if key[pygame.K_UP]:
            player.move(0, -2)
        if key[pygame.K_DOWN]:
            player.move(0, 2)
        
        if key[pygame.K_z]:
            m.p()
        
 

    
    
        # Just added this to make it slightly fun ;)
        if player.rect.colliderect(end_rect):
            running = False
    
        # Draw the scene
        screen.fill((0, 0, 0))
        # for wall in walls:
        #     pygame.draw.rect(screen, (255, 255, 255), wall.rect)
        pygame.draw.rect(screen, (255, 0, 0), end_rect)
        maze.render()
        pygame.draw.rect(screen, (255, 200, 0), player.rect)
        pygame.display.flip()
