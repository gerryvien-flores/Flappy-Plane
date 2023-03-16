#!/usr/bin/python3

import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 998
screen_height = 660

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird Remake')


#load images
bg = pygame.image.load('design/city/city_bg.png')
ground_img = pygame.image.load('design/city/bg_grnd.png')
button_img = pygame.image.load('design/restart.png')

#define font
font = pygame.font.SysFont('Bauhaus 93', 60)

#define colors
white = (255,255,255)

#Game Variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
obs_gap = 350
obs_frequency = 1500 #milliseconds
last_obs = pygame.time.get_ticks() - obs_frequency
score = 0
pass_obs = False

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height /2)
    score = 0
    return score

class Plane(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'design/plane{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0

        self.boom_images = []
        self.boom_index = 0
        for i in range(1, 18):
            boom = pygame.image.load(f'design/explosion/f{i}.png')
            self.boom_images.append(boom)


    def update(self):

        if flying == True:
            #gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 550:
                self.rect.y += int(self.vel)

        if game_over == False:

            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #Animation
            self.counter += 1
            boost_cooldown = 5

            if self.counter > boost_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #rotation
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            #Death Animation
            self.counter += 1
            explosion_fr = 5

            if self.counter > explosion_fr:
                self.counter = 0
                self.boom_index += 1
                if self.boom_index >= len(self.boom_images):
                    self.boom_index = 0
            self.image = self.boom_images[self.boom_index]

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('design/city/building.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x,y - int(obs_gap / 2)]
        if position == -1:
            self.rect.topleft = [x,y]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right< 0:
            self.kill()

class Button():
    def __init__(self, x, y ,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)

    def draw(self):

        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check if mouse is over the button

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True


        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

plane_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Plane(100, int(screen_height / 2))
plane_group.add(flappy)

#create restart button instance
button = Button(screen_width // 2 - 60, screen_height // 2 - 100, button_img)

run = True
while run:

    clock.tick(fps)

    #Background
    screen.blit(bg, (0,0))
    plane_group.draw(screen)
    plane_group.update()
    pipe_group.draw(screen)



    #draw the ground
    screen.blit(ground_img, (ground_scroll, 548))

    #Check Score
    if len(pipe_group) > 0:
        if plane_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and plane_group.sprites()[0].rect.right > pipe_group.sprites()[0].rect.right\
            and pass_obs == False:
            pass_obs = True
        if pass_obs == True:
            if plane_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_obs = False

    draw_text(str(int(score/18)), font, white, int(screen_width/2), 20)

    #Collision
    if pygame.sprite.groupcollide(plane_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True


    #Check if plane had crashed
    if flappy.rect.bottom >= 550:
        game_over = True
        flying = False

    if game_over == False and flying == True:
        #Generate Obstacles
        time_now = pygame.time.get_ticks()
        if time_now - last_obs > obs_frequency:
            obs_height = random.randint(-100, 100)
            btm_obs = Pipe(screen_width, int(screen_height / 2) + obs_height, -1)
            top_obs = Pipe(screen_width, int(screen_height / 2) + obs_height, 1)
            pipe_group.add(btm_obs)
            pipe_group.add(top_obs)
            last_obs = time_now

        #Draw and Scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 30:
            ground_scroll = 0

        pipe_group.update()

    #Check for game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()

pygame.quit()
