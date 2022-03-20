import os
import pygame
import random
import torch

RUNNING = [
    pygame.image.load(os.path.join('Assets/Dino', 'DinoRun1.png')),
    pygame.image.load(os.path.join('Assets/Dino', 'DinoRun2.png'))
]

JUMPING = pygame.image.load(os.path.join('Assets/Dino', 'DinoJump.png'))

DUCKING = [
    pygame.image.load(os.path.join('Assets/Dino', 'DinoDuck1.png')),
    pygame.image.load(os.path.join('Assets/Dino', 'DinoDuck2.png'))
]

SMALL_CACTUS = [
    pygame.image.load(os.path.join('Assets/Cactus', 'SmallCactus1.png')),
    pygame.image.load(os.path.join('Assets/Cactus', 'SmallCactus2.png')),
    pygame.image.load(os.path.join('Assets/Cactus', 'SmallCactus3.png'))
]

LARGE_CACTUS = [
    pygame.image.load(os.path.join('Assets/Cactus', 'LargeCactus1.png')),
    pygame.image.load(os.path.join('Assets/Cactus', 'LargeCactus2.png')),
    pygame.image.load(os.path.join('Assets/Cactus', 'LargeCactus3.png'))
]

BIRD = [
    pygame.image.load(os.path.join('Assets/Bird', 'Bird1.png')),
    pygame.image.load(os.path.join('Assets/Bird', 'Bird2.png'))
]

CLOUD = pygame.image.load(os.path.join('Assets/Other', 'Cloud.png'))

BACKGROUND = pygame.image.load(os.path.join('Assets/Other', 'Track.png'))


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False


    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self, screen_width: int):
        self.SCREEN_WIDTH = screen_width
        self.x = screen_width + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self, game_speed: int):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = self.SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen: pygame.surface):
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type, screen_width):
        self.SCREEN_WDITH = screen_width
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = screen_width

    def update(self, game_speed: int, obstacles: list):
        self.rect.x -= game_speed
        if self.rect.x < - self.rect.width:
            obstacles.pop()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, screen_width: int):
        self.type = random.randint(0, 2)
        super().__init__(SMALL_CACTUS, self.type, screen_width)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, screen_width: int):
        self.type = random.randint(0, 2)
        super().__init__(LARGE_CACTUS, self.type, screen_width)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, screen_width: int):
        self.type = 0
        super().__init__(BIRD, self.type, screen_width)
        self.rect.y = 250
        self.index = 0

    def draw(self, screen: pygame.surface):
        if self.index >= 9:
            self.index = 0
        screen.blit(self.image[self.index // 5], self.rect)
        self.index += 1

