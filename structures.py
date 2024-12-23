
import pygame
from math import ceil, floor, sqrt
from random import choice as r_choice, randint as r_int



WIDTH = 16



class Wall(object):
    
    def __init__(self, game, coords, color):
        self.color = color
        self.state = "alive"
        self.game = game
        self.rect = pygame.Rect(coords[0], coords[1], WIDTH, WIDTH)
        

    @property
    def pos(self):
        return (self.rect.x, self.rect.y)
        

    def doSomething(self):
        self.render()
        

    def render(self):
        pygame.draw.rect(self.game.screen, self.color, self.rect)
        


    def die(self):
        self.state = "dead"
        self.color = (0,0,0)
        

class Breakable_Wall(Wall):
    
    def doSomething(self):
        
        self.render()
        if self.rect.colliderect(self.game.player.rect):
            self.die()
        
        for bullet in self.game.player.bullets:

            if self.rect.colliderect(bullet.rect):
                self.die()
                

class Explosive_Wall(Wall):
    def doSomething(self):
       
        self.render()
     
        for bullet in self.game.player.bullets:

            if self.rect.colliderect(bullet.rect):
                self.die()
                self.game.player.explode(self.pos)
                return
                


        



class Mine(Wall):
    
    def __init__(self, game, coords, color, hp):
       
        super(Mine, self).__init__(game, coords, color)
        self.hp = hp
        
    def doSomething(self):
        if self.hp <= 0:
            self.die()
        else:
            self.render()
        
        
class Maze(object):
    
    def __init__(self, game, row, col, sparsity, padding, WALL_COLOR):
        
        if row % 2 == 0:
            row += 1
            
        if col % 2 == 0:
            col += 1
        
        self.game = game
        self.padding = padding
        self.sparsity = sparsity
        self.cols = col
        self.rows = row
        self.layout = [[[Wall(self.game, (i * WIDTH + padding, padding + j * WIDTH), WALL_COLOR)] for i in range(col)] for j in range(row)]
        
        if sparsity[0] <= 0 and sparsity[1] <= 0 and sparsity[2] <= 0:
            self.carve(self.layout)
            
        else:
            temp = [[[Wall(self.game, (i * WIDTH + padding, padding + j * WIDTH), WALL_COLOR)] for i in range(col)] for j in range(row)]
            self.carve(temp)
            self.carve(self.layout)
            self.combine(self.layout, temp, sparsity)
            
        
        
        
        
        self.s = [(1, 1), (floor(self.cols / 2), 1), (self.cols - 2, self.rows - 2), (floor(self.cols / 2), self.rows - 2),
         (self.cols - 2 , floor(self.rows / 2)), (1, floor(self.rows / 2)), (1, self.rows - 2), (self.cols - 2, 1),
        (floor(self.cols / 2), self.rows - 2)]
        for i in self.s:
            self.layout[i[0]][i[1]][0].color = (255, 0, 0)
            self.layout[i[0]][i[1]][0].die()
            
        self.layout[1][1][0].color = (255, 0, 0)


    def get_layout(self):
        copy = []
        color_ = ((self.layout[0][0][0].color[0]) // 2, (+ self.layout[0][0][0].color[1]) // 2, (self.layout[0][0][0].color[2]) // 2)
        
        for row in range(len(self.layout)):
            copy.append([])
            for col in range(len(self.layout[row])):
                if isinstance(self.layout[row][col][0], Breakable_Wall):
                    copy[row].append([Breakable_Wall(self.game, (self.layout[row][col][0].rect.x, self.layout[row][col][0].rect.y), color_)])
                elif isinstance(self.layout[row][col][0], Explosive_Wall):
                    copy[row].append([Explosive_Wall(self.game, self.layout[row][col][0].pos, (255, 0, 0))])
                
                elif isinstance(self.layout[row][col][0], Wall):
                    copy[row].append([Wall(self.game, (self.layout[row][col][0].rect.x, self.layout[row][col][0].rect.y), self.layout[row][col][0].color)])
                    if self.layout[row][col][0].state == "dead":
                            copy[row][col][0].die()
                      

        copy[1][1][0].color = (255,0,0)
                
        return copy


    def combine(self, layout, other, sparsity):

        color_ = ((self.layout[0][0][0].color[0]) // 2, (+ self.layout[0][0][0].color[1]) // 2, (self.layout[0][0][0].color[2]) // 2)
        if 6 <= self.game.level % 8 <= 8:
            explosive_ = r_int(10, 40)
        else:
            explosive_ = 200

        if 1 == self.game.level % 2:
            glass_ = r_int(1, 30)
        elif 13 == self.game.level % 15 or 19 == self.game.level % 20:
            glass_ = r_int(80, 100)

        else:
            glass_ = sparsity[2]
        for y in range(1, len(layout) - 1):
            for x in range(1, len(layout[y]) - 1):
                
                   
                if layout[y][x][0].state != "alive" or "alive" != other[y][x][0].state and r_int(0, 100) < sparsity[0]:
                    layout[y][x][0].die()
                elif r_int(0, 100) < glass_:
                    layout[y][x][0] = Breakable_Wall(self.game, layout[y][x][0].pos, color_)
                    

                if  r_int(0, 100 ) < sparsity[1] and x != 0 and x != len(self.layout[0]) - 1 and y != 0 and y != len(self.layout) - 1 and x % 2 == 0 and y % 2 == 0:
                    layout[y][x][0].die()
                elif r_int(0, explosive_) < 10 and x % 2 == 0 and y % 2 == 0:
                    layout[y][x][0] = Explosive_Wall(self.game, self.layout[y][x][0].pos, (255, 0, 0))
                    
        
                

    def create_center(self):
        x = ceil(self.cols / 2)
        y = ceil(self.rows / 2)
        r = int(min(sqrt(self.rows), sqrt(self.cols)))
        if r % 2 == 0:
            r += 1
        for j in range(-floor(r / 2) - 1 , floor(r / 2)):
            for i in range(-floor(r / 2) - 1, floor(r / 2)):
                
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
                c1, c2 = r_choice(choices)
                toVisit.append(c1)
                layout[c2[1] ][c2[0]][0].die()
               
                visited.add((x, y))
                

    def change_color(self):
        color = (r_int(0, 255), r_int(0, 255), r_int(0, 255))
        self.game.wall_color = color
     
        for row in self.layout:
            for wall in row:
                if wall[0].state != "dead":
                    wall[0].color = color
                if len(wall) == 2:
                    wall[1].color = color
                
        for trap in self.game.traps:
            trap.color = color

    def doSomething(self):
        self.layout[1][1][0].render()
        for row in self.layout:
            for col in row:
                if col[0].state != "dead":
                    col[0].doSomething()
                if len(col) == 2:
                    if col[1].hp == 0 or col[1].state == "dead":
                        col.remove(col[1])
                
                    else:
                        col[1].doSomething()
                    
                
        
    def render(self):
        return NotImplementedError
                


class CourtYard(Maze):
    
    def __init__(self, game, row, col, sparsity, padding, WALL_COLOR, settings):
       
        self.settings = settings.strip("()[]\n").split(", ")
        self.settings[0] = (int(self.settings[0].strip("()")), int(self.settings[1].strip("()")))
        self.settings[1] = (int(self.settings[2].strip("()")), int(self.settings[3].strip("()")))
        sparsity = (int(self.settings[4].strip("()")), int(self.settings[5].strip("()")), sparsity[2])
    
        self.layout_idx = 0
      
        super(CourtYard, self).__init__(game, row, col, sparsity, padding, WALL_COLOR)
        
       
        

    def carve(self, x):
        width = self.settings[self.layout_idx][0]
        spacing = self.settings[self.layout_idx][1]
        self.layout_idx += 1

        for i in range(1, self.rows - 1):
            for j in range(1, self.cols - 1):
                
                if (i % spacing not in range(width, spacing)) or (j % spacing not in range(width, spacing)):
                    self.layout[i][j][0].die()
