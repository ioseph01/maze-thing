from structures import Breakable_Wall, Explosive_Wall, Mine, Wall
from random import choice as r_choice, randint as r_int
import pygame
from math import ceil, floor, sqrt


WIDTH = 16




class Unit(object):
    
    def __init__(self, game, color, coords, state, direction, scale, step, hp):
        self.game = game
        self.color = color
        self.state = state
        self.direction = direction
        self.rect = pygame.Rect(coords[0], coords[1], WIDTH * scale, WIDTH * scale)
        self.scale = scale
        self.hp = hp
        self.step = step
        
    
    @property
    def pos(self):
        return (self.rect.x, self.rect.y)

    def doSomething(self):
        return NotImplementedError
    

    def render(self):
        pygame.draw.rect(self.game.screen, self.color, self.rect)
    

    def move_single_axis(self, dx, dy):
        return NotImplementedError
        
    
class Entity(Unit):
    
    def __init__(self, game, coords, color, trace_commitment, scale, step, build_rate, hp):
        super(Entity, self).__init__(game, color, coords, "alive", r_choice(["north", "east", "south", "west"]), scale, step, hp)
        self.path = []
        self.trace_commitment = trace_commitment / 100
        self.target = (self.game.maze.rows, self.game.maze.cols)
        self.trace_tick = 0
        self.tick = 0
        self.build_rate = 1000 * build_rate
        

    def get_scatter(self):
        return r_choice( [(1, 1), (ceil(self.game.maze.cols / 2), 1), (self.game.maze.cols - 2, self.game.maze.rows - 2), (ceil(self.game.maze.cols / 2), self.game.maze.rows - 2),
         (self.game.maze.cols - 2 , ceil(self.game.maze.rows / 2)), (1, ceil(self.game.maze.rows / 2)), (1, self.game.maze.rows - 2), (self.game.maze.cols - 2, 1),
        (ceil(self.game.maze.cols / 2), self.game.maze.rows - 2)] )
    

    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
        for j in range((self.rect.y - self.game.padding) // WIDTH - self.scale, self.scale + 1 + (self.rect.y - self.game.padding) // WIDTH):
            for i in range((self.rect.x - self.game.padding) // WIDTH - self.scale, (self.rect.x - self.game.padding) // WIDTH + self.scale + 1):
                if i >= len(self.game.maze.layout[0]) or i < 0 or j >= len(self.game.maze.layout) or j < 0:
                    continue
                    
                wall = self.game.maze.layout[j][i][0]
                

                if self.rect.colliderect(wall.rect) and wall.state == "alive":
                    if dx > 0: # Moving right; Hit the left side of the wall
                        self.rect.right = wall.rect.left
                        
                    elif dx < 0: # Moving left; Hit the right side of the wall
                        self.rect.left = wall.rect.right
                        
                    if dy > 0: # Moving down; Hit the top side of the wall
                        self.rect.bottom = wall.rect.top
                       
                    elif dy < 0: # Moving up; Hit the bottom side of the wall
                        self.rect.top = wall.rect.bottom
                        

    def playerDetect(self):
        if self.rect.colliderect(self.game.player.rect):
            # self.game.sound.player_hurt()
            self.game.player.hp -= 1
                        

    def mineDetect(self):
        for mine in self.game.player.mines:
            if self.rect.colliderect(mine.rect) and mine.state != "dead":
                mine.hp -= 1
                self.state = "dead"
                # self.game.sound.load_sound("shot.mp3")

    
    
    def bulletDetect(self):
        for bullet in self.game.player.bullets:
            if self.rect.colliderect(bullet.rect):
                self.state = "dead"
                bullet.hp -= 1
                # self.game.sound.load_sound("shot2.mp3")
        

                
    def lay_trap(self):
            if r_int(1, 1000) < self.build_rate and self.trace_tick == 0 and len(self.game.maze.layout[self.rect.y // WIDTH][self.rect.x // WIDTH]) < 2:
                self.game.traps.append(Mine(self.game, self.pos, self.game.maze.layout[0][0][0].color, 1))
                self.game.maze.layout[self.rect.y // WIDTH][self.rect.x // WIDTH].append(self.game.traps[-1])

        

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
        
        self.playerDetect()           
        self.bulletDetect()
        self.mineDetect()
      
        if self.tick == 0:

            if len(self.path) > 0:
                self.move_path()

            elif abs(self.rect.x - self.game.player.rect.x) < 120 and abs(self.rect.y - self.game.player.rect.y) < 120 and self.game.player.state == "alive":
                self.trace(self.game.player.rect.x // WIDTH, self.game.player.rect.y // WIDTH)
                
            else:
                x, y = self.get_scatter()
                self.target = (x, y)
                self.trace(x, y)
                
        self.tick = (self.tick + 1) % 2
        
    

    def trace(self, target_x, target_y):
        x = (-self.game.padding + self.rect.x) // WIDTH
        y = (-self.game.padding + self.rect.y) // WIDTH
        
        visited = {(x, y)}
        paths = [[(x, y)]]
        
        while len(paths) > 0 :
            
            current = paths.pop(-1)
            x, y = current[-1]
            
            if x == target_x and y == target_y:
                self.state = "chasing"
                
                if target_x * WIDTH == self.game.player.rect.x and target_y * WIDTH == self.game.player.rect.y:
                    self.path = current
                else:
                    self.path = current[:round(len(current) * self.trace_commitment)]
                    
                if len(self.path) > 0:
                    self.coords = self.path.pop(0)
                    
                try:
                    self.target = (current[-1][0], current[-1][1])
                except IndexError:
                    print(f"Virus upload progress .......... {r_int(0, 100)}%")
                    
                return
            
            visited.add((x, y))
            toAdd = {}
            
            if x + 1 < len(self.game.maze.layout[0]) and (x + 1, y) not in visited:
            
                if self.game.maze.layout[y][x + 1][0].state == "dead":
                    k = abs(target_x - x - 1) + abs(target_y - y)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x + 1, y))
                     
            if y + 1 < len(self.game.maze.layout) and (x, y + 1) not in visited:
                if self.game.maze.layout[y + 1][x][0].state == "dead":
                    k = abs(target_x - x) + abs(target_y - y - 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y + 1))
                    
            if x - 1 > -1 and (x - 1, y) not in visited:
                if self.game.maze.layout[y][x - 1][0].state == "dead":
                    k = abs(target_x - x + 1) + abs(target_y - y)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x - 1, y))
                          
            if y - 1 > -1 and (x, y - 1) not in visited:
           
                if self.game.maze.layout[y - 1][x][0].state == "dead":
                    k = abs(target_x - x) + abs(target_y - y + 1)
                    if k not in toAdd:
                        toAdd[k] = []
                    toAdd[k].append((x, y - 1))

            for key in reversed(dict(sorted(toAdd.items()))):
                for val in toAdd[key]:
                    paths.append(current + [val])
            



class Giant(Entity):
  

    def bulletDetect(self):
        for bullet in self.game.player.bullets:
            
            if self.rect.colliderect(bullet.rect):
                bullet.hp -= 1
                self.step *= 7/5
                self.hp -= 1
                self.scale += 1
                # game.sound.load_sound("boom.mp3")
                self.rect = pygame.Rect(self.pos[0], self.pos[1],  WIDTH * self.scale, WIDTH * self.scale)
                return
                

    def mineDetect(self):
        for mine in self.game.player.mines:
            if self.rect.colliderect(mine.rect):
                # game.sound.load_sound("boom.mp3")
                self.hp -= 1
                mine.hp -= 1
                self.scale += 1
                self.step *= 7/5
                self.rect = pygame.Rect(self.pos[0], self.pos[1], WIDTH * self.scale, WIDTH * self.scale)
                return
     
    
 
    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
  
        for j in range(self.rect.y // WIDTH - self.scale, self.scale + 1 + self.rect.y // WIDTH):
            for i in range(self.rect.x // WIDTH - self.scale, self.rect.x // WIDTH + self.scale + 1):
              
                if i > -1 and i < (len(self.game.maze.layout[0])) and j < (len(self.game.maze.layout)) and j > -1:
                    wall = self.game.maze.layout[j][i][0]
                    if self.rect.colliderect(wall.rect) and wall.state == "alive":
                        
                        if i == len(self.game.maze.layout[0]) - 1:
                            self.rect.right = wall.rect.left
                      
                        elif i == 0:
                            self.rect.left = wall.rect.right
              
                        
                        elif j == len(self.game.maze.layout) - 1:
                            self.rect.bottom = wall.rect.top
                       
                        elif j == 0:
                            self.rect.top = wall.rect.bottom
                        else:
                            if isinstance(wall, Explosive_Wall):
                                self.game.player.explode(self.pos)
                            wall.die()

        
    def doSomething(self):
        if self.hp <= 0:
            self.state = "dead"
            return
        else:
            super().doSomething()
            

class Stalker(Entity):
    
    def __init__(self, game, coords, color, trace_commitment, scale, step, hp):
        super(Stalker, self).__init__(game, coords, color, trace_commitment, scale, step, 0, hp)
        self.hide_tick = 0
        
    def playerDetect(self):
        if self.rect.colliderect(self.game.player.rect):
            self.game.player.hp -= 1
   
    def bulletDetect(self):
        if self.hp <= 0:
            self.state = "dead"
            # game.sound.load_sound("shot2.mp3")
        else:
            for bullet in self.game.player.bullets:
                if self.rect.colliderect(bullet.rect):
                    self.hp -= 1
                    bullet.hp -= 1
                    return

    
    def doSomething(self):
        
        if self.state != "dead":
            if abs(self.rect.x - self.game.player.rect.x) < 120 and abs(self.rect.y - self.game.player.rect.y) < 120 and self.hide_tick == 0 and self.game.player.state == "alive":
                if self.state != "hiding":
                    m = self.game.maze.layout[0][0][0].color
                    self.color = r_choice( (( m[0] // 2, m[1] // 2, m[2] // 2), self.game.wall_color))
                    self.state = "hiding"
                else:
                    self.bulletDetect()
                    self.render()
                    self.hide_tick = self.hide_tick - 1 if self.hide_tick > 0 else 0
                    if self.rect.colliderect(self.game.player.rect):
                        # self.game.sound.toPlay.insert(1, "found.mp3")
                        self.game.player.hp -= 1
                        self.color = (0,255,0)
                        self.state = "alive"
                        self.hide_tick = 50
                        self.trace(self.game.player.rect.x, self.game.player.rect.y)
                        
                    
                    
            else:
                self.color = (0, 255, 0)
                self.state = "alive"
                super().doSomething()
                self.hide_tick = self.hide_tick - 1 if self.hide_tick > 0 else 0
                

        
        

class Builder(Entity):
    
    def doSomething(self):
        
        if self.state != "dead":
            self.lay_trap()
            super().doSomething()




class Snake(Unit):
    
    def __init__(self, game, color, coords, state, scale, segments, step):
        super(Snake, self).__init__(game, color, coords, state, "north", scale, step, segments)
        self.unravel_counter = 0
      
        self.move_tick = 0
        self.destroy_idx = 0

        if type(segments) == list:
            self.segments = segments
        elif type(segments) == int:
            self.segments = [Entity(game, self.pos, self.color, r_int(60, 90), self.scale, self.step, 0, 1) for i in range(segments)]
       
            

    def doSomething(self):
       
        if self.state == "dead":
            return
        
        elif len(self.segments) == 0:
            self.state = "dead"
            return
            
        elif self.state == "dying":
            self.render()
            self.segments.pop(self.destroy_idx)
            # game.sound.load_sound("shot.mp3")
            self.game.score += 1
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
                    self.game.score += 1
                    return
                  
                for bullet in self.game.player.bullets:
                    if self.segments[i].rect.colliderect(bullet.rect):
                        self.game.score += 1
                        self.bulletCollision(bullet, i)
                        return
                        
                temp = (self.segments[i].rect.x, self.segments[i].rect.y)
               
                if i == 0:
                    self.segments[i].doSomething()
                else:
                   
                    self.segments[i].rect.x, self.segments[i].rect.y = coords
                    if self.segments[i].rect.colliderect(self.game.player.rect):
                        # self.game.sound.player_hurt()
                        self.game.player.hp -= 1

                            
                coords = temp
        self.unravel_counter += 1
        self.render()
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
            
            self.game.entities.insert(0, Snake(self.game, self.color, (WIDTH * self.rect.x // WIDTH, WIDTH * self.rect.y // WIDTH), state, self.scale, self.segments[i:], self.step))
            self.segments = self.segments[:i]
            self.unravel_counter += 1
            
        elif bullet.state == "powered":
            self.state = "dying"
            if i >= len(self.segments):
                self.destroy_idx = -1
            elif i == 0:
                self.destroy_idx = 0
            
        bullet.hp -= 1
       

    def render(self):
        # for i in range(min(len(self.segments), self.unravel_counter)):
        #     self.segments[i].render()
            
        for i in self.segments:
            i.render()



class Bullet(Unit):
    
    def __init__(self, game, coords, direction, state):
        if state != "powered":
            color = (255, 200, 0)
            # self.death_sound = "bullet_death.mp3"
            hp = 1
        else:
            color = (255,255,255)
            self.death_sound = "powered_bullet_death.mp3"
            hp = 3
        super(Bullet, self).__init__(game, color, coords, state, direction, 1, 2, hp)

       
        
        
    def directionCoordMap(self, val):
    
        m = {"north" : (0, 1), "east" : (1, 0), "south" : (0, -1), "west" : (-1, 0)}
        if val in m:
            return m[val]
    
        for k in m:
            if m[k] == val:
                return k
        

        

    def doSomething(self):
        if self.state != "dead" and self.hp > 0:
            toMove = self.directionCoordMap(self.direction)
            self.move_single_axis(toMove[0] * self.step, self.step * toMove[1])
            self.render()
    

    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

        for j in range(self.rect.y // WIDTH - 1, 2 + self.rect.y // WIDTH):
            for i in range(self.rect.x // WIDTH - 1, self.rect.x // WIDTH + 2):
                
                wall = self.game.maze.layout[j][i][0]
                if isinstance(wall, Breakable_Wall) and self.rect.colliderect(wall.rect) and self.state == "powered":
                    continue
                elif self.rect.colliderect(wall.rect) and wall.state == "alive":
 
                    self.hp = 0
                    
        for trap in self.game.traps:
            if trap.rect.colliderect(self.rect):
                # self.game.sound.load_sound("broken.mp3")
                self.hp = 0
                trap.hp -= 1
                    



class Player(Unit):
    
    def __init__(self, game):
        super(Player, self).__init__(game, (255, 200, 0), (game.padding + (game.maze.cols - 2) * WIDTH, game.padding + (game.maze.rows - 2) * WIDTH), "alive", "north", 1, 1.25, 25)
        self.bullets = []
        self.mines = []
        self.stun_tick = 0
        self.fire_tick = 0
        self.clear_tick = 0
        self.power_tick = 0
        self.paths = []
        

    def incHits(self):
        self.hp -= 1

    def clear_traps(self, size):
        if self.fire_tick != 0:
            return
        
        self.game.inventory[3] -= 1
        x,y = self.rect.x // WIDTH, self.rect.y // WIDTH
        visited = set((x, y))
        toVisit = [[(x, y)]]
        while len(toVisit) > 0:
            
            current = toVisit.pop(0)
            temp = len(toVisit)
            x, y = current[-1]
            visited.add((x, y))
            if len(current) >= size:
                visited.add((current[0], current[1]))
                self.paths.append(current)
                continue
            
            if self.game.maze.layout[y + 1][x][0].state == "dead" and (x, y + 1) not in visited:
                toVisit.append(current + [(x, y + 1)])
            if self.game.maze.layout[y - 1][x][0].state == "dead" and (x, y - 1) not in visited:
                toVisit.append(current + [(x, y - 1)])
            if self.game.maze.layout[y][x + 1][0].state == "dead" and (x + 1, y) not in visited:
                toVisit.append(current + [(x + 1, y)])
            if self.game.maze.layout[y][x - 1][0].state == "dead" and (x - 1, y) not in visited:
                toVisit.append(current + [(x - 1, y)])
            if temp == len(toVisit):
                self.paths.append(current)

        
            
    def explode(self, coords):
        
        self.bullets.append(Explosion(self.game, (255,255,255), coords, 4, 5))

    def shoot(self, state): 
        if self.fire_tick <= 0:
            self.bullets.append(Bullet(self.game, (self.pos), self.direction, state))
            self.fire_tick = 10
            if state == "powered":
                self.game.inventory[1] -= 1
            else:
                self.game.inventory[0] -= 1


    def lay_mine(self, x, y, hp):
        if self.fire_tick <= 0:
            self.mines.append(Mine(self.game, (x, y), (255, 200, 0), hp))
            self.fire_tick = 10
            self.game.inventory[2] -= 1
            


    def summon(self, x, y):
        if self.fire_tick <= 0:
            self.bullets.append( Summon(self.game, (1 * WIDTH + self.game.padding, self.game.padding + 1 * WIDTH), (255, 255, 255), 100, 1, 8, 99999, (x// WIDTH, y // WIDTH)) )
            self.fire_tick = 10
        

    def doSomething(self):
     
        
                
        for mine in self.mines:
            if mine.hp <= 0 or mine.state == "dead":
                self.mines.remove(mine)
            else:
                mine.doSomething()
                

        for bullet in self.bullets:
            if bullet.hp <= 0 or bullet.state == "dead":
                # self.game.sound.load_sound(bullet.death_sound)
                self.bullets.remove(bullet)
            else:
                bullet.doSomething()

        if self.state != "ghost":
            for trap in self.game.traps:
                if self.rect.colliderect(trap.rect) and trap.hp > 0:
                    # self.game.sound.load_sound("stuck.mp3")
                    self.stun_tick += 20
                    trap.hp -= 1
                            

        if self.power_tick > 0:
            self.power_tick -= 1
        elif self.power_tick == 0:
            self.power_tick -= 1
            self.game.hasPowerUp = False
            if self.state == "ghost":
                self.state = "alive"
                self.color = (255, 200, 0)
                self.step = 1.1
        
        self.render()

        if self.stun_tick > 0:
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
                     
                        if len(self.game.maze.layout[y][x]) >= 2:
                            
                            self.game.maze.layout[y][x][-1].state = "dead"
                            self.game.maze.layout[y][x].pop(-1)

            self.clear_tick = (self.clear_tick + 1) % 2



    def move_single_axis(self, dx, dy):
        if self.stun_tick > 0:
            return
        
       
        self.rect.x += dx * self.step
        self.rect.y += dy * self.step
        
        if self.state == "alive":
            for j in range(self.rect.y // WIDTH - 1, 2 + self.rect.y // WIDTH):
                for i in range(self.rect.x // WIDTH - 1, self.rect.x // WIDTH + 2):
                    wall = self.game.maze.layout[j][i][0]
                    if self.rect.colliderect(wall.rect) and wall.state == "alive" and (type(wall) == Wall or isinstance(wall, Explosive_Wall)):
                        if dx > 0: # Moving right; Hit the left side of the wall
                                self.rect.right = wall.rect.left
                        if dx < 0: # Moving left; Hit the right side of the wall
                            self.rect.left = wall.rect.right
                        if dy > 0: # Moving down; Hit the top side of the wall
                            self.rect.bottom = wall.rect.top
                        if dy < 0: # Moving up; Hit the bottom side of the wall
                            self.rect.top = wall.rect.bottom
                        
      
        if self.rect.y <= 26:
            self.rect.y = 26
        if self.rect.y >= 570:
            self.rect.y = 570
        if self.rect.x <= 26:
            self.rect.x = 26
        if self.rect.x >= 570:
            self.rect.x = 570
    


class Summon(Entity):

    def __init__(self, game, coords, color, trace_commitment, scale, step, hp, target):
        super(Summon, self).__init__(game, coords, color, trace_commitment, scale, step, 0, hp)
        self.trace(target[0], target[1])
        self.death_sound = "powered_bullet_death.mp3"
        self.state = "powered"

    def mineDetect(self):
        pass
    

    def bulletDetect(self):
        pass
    

    def playerDetect(self):
        if self.rect.colliderect(self.game.player.rect):
            self.game.player.hp += 12
            self.die()
            

    def die(self):
        self.hp = 100
        self.scale = 5
        self.rect = pygame.Rect(self.pos[0], self.pos[1], WIDTH * self.scale, WIDTH * self.scale)
        self.rect.x -= 30
        self.rect.y -= 30

    def doSomething(self):
        
        if self.hp <= 100:
            self.hp -= 20
            return

        if self.target[0]  == self.rect.x // WIDTH and self.target[1] == self.rect.y // WIDTH:
            self.die()        
       
            
        if len(self.game.maze.layout[self.rect.y // WIDTH][self.rect.x // WIDTH]) > 1:
            self.game.maze.layout[self.rect.y // WIDTH][self.rect.x // WIDTH][-1].state = "dead"
            # self.game.sound.load_sound("broken.mp3")
        super().doSomething()



class Explosion(Unit):
    
    def __init__(self, game, color, coords, scale, hp):
        
        a = (scale - 1) / 2
        
        super(Explosion, self).__init__(game, color, (coords[0] - WIDTH * a, coords[1] - WIDTH * a), "powered", None, scale, 0, hp)
     

        x,y = (self.rect.x - 10) // WIDTH, (self.rect.y - 10) // WIDTH
        for i in range(self.scale):
            for j in range(self.scale):

                if j + x >= len(self.game.maze.layout) - 1 or j + x <= 1 or i + y <= 1 or i + y >= len(self.game.maze.layout) - 1:
                    continue
                current = self.game.maze.layout[i + y][j + x]
                if isinstance(current[0], Wall) and current[0].state == "alive":
                    current[0].die()
                if len(current) == 2:
                    current[1].hp = 0
                        

    def doSomething(self):
        if self.hp > 0 :
            self.hp -= 1
            self.render()
            
                       
        else:
            self.state = "dead"


class Gift(Entity):

    def mineDetect(self):
        pass
    

    def reward(self):
        for i in range(len(self.game.inventory)):
            if self.game.inventory[i] >= 15:
                self.game.inventory[i] = self.game.inventory[i] + 1 if self.game.inventory[i] + 1 < 99 else 99
            else:
                self.game.inventory[i] = self.game.inventory[i] + 3 if self.game.inventory[i] + 3 < 99 else 99
            
        self.game.player.hp += 5
            
    
    def playerDetect(self):
        if self.rect.colliderect(self.game.player.rect):
            self.reward()
            self.state = "dead"
            # self.game.sound.load_sound("shot.mp3")
           
            
    
    def bulletDetect(self):
        for bullet in self.game.player.bullets:
            if self.rect.colliderect(bullet.rect):
                self.state = "dead"
                self.reward()
                # self.game.sound.load_sound("shot.mp3")
                return
            
    def get_scatter(self):
        return (self.game.player.rect.x // WIDTH, self.game.player.rect.y // WIDTH)
                



class PowerUp(Unit):
    
    def __init__(self, game):
        super(PowerUp, self).__init__(game, (255, 255, 0), (game.padding + game.m * WIDTH // 2, game.padding + game.n * WIDTH // 2),  "alive", "north", 1, 1, 1)
        

    def doSomething(self):
        self.render()
        if self.rect.colliderect(self.game.player.rect):
            self.hp = 0
            self.reward()
        
            

    def reward(self):
        # self.game.sound.load_sound("complete.mp3")
        self.game.player.hp += 10
        r_choice((self.shield, self.ghost, self.strike))()
   
        
    def shield(self):
     
        self.game.player.bullets.append(Shield(self.game))
        
    def ghost(self):
        self.game.player.power_tick = 400
        self.game.player.hp += 15
   
        self.game.player.state = "ghost"
        self.game.player.color = (26, 26, 26)
        
        self.game.player.step = 2


    def strike(self):
        if len(self.game.entities) > 0:
         
            
            for i in range(5):
                choice = r_choice(self.game.entities)
                self.game.player.summon(choice.rect.x, choice.rect.y)
                self.game.player.fire_tick = 0
        self.game.player.power_tick = 400
        
        x = ceil(self.game.maze.cols / 2)
        y = ceil(self.game.maze.rows / 2)
        radius = int(min(sqrt(self.game.maze.rows), sqrt(self.game.maze.cols)))
        if radius % 2 == 0:
            radius += 1
        for j in range(-floor(radius / 2) - 1 , floor(radius / 2)):
            for i in range(-floor(radius / 2) - 1, floor(radius / 2)):
                self.game.player.mines.append(Mine(self.game, ((y + j) * WIDTH + self.game.padding, (x + i) * WIDTH + self.game.padding), (0, 0, 0), 2))
               
        
class Shield(Unit):
    
    def __init__(self, game):
        super(Shield, self).__init__(game, (255, 255, 255), (game.player.rect.x, game.player.rect.y), "alive", "north", 2, 1, 100)
        self.player_health = game.player.hp
        self.regen_tick = 0
        self.game.player.color = (255, 255, 255)
        self.game.player.power_tick = 400
        self.death_sound = "death.mp3"
        
    def doSomething(self):
        self.hp = self.game.player.power_tick
        if self.hp > 2:
            
            self.rect.x = self.game.player.rect.x - WIDTH / 2
            self.rect.y = self.game.player.rect.y - WIDTH / 2
            
            for trap in self.game.traps:
                if trap.rect.colliderect(self.rect):
                    # self.game.sound.load_sound("broken.mp3")
                    self.hp -= 1
                    trap.hp -= 1

            if self.game.player.hp < self.player_health and self.regen_tick == 0:
                self.game.player.hp += .25
                
            self.regen_tick = (self.regen_tick + 1) % 5
            
            
        else:
            self.game.player.color = (255, 200, 0)


