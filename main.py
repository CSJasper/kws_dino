import os.path

import pygame
from Objects import Dinosaur
from Objects import Cloud
from Objects import BACKGROUND
from Objects import SmallCactus
from Objects import LargeCactus
from Objects import Bird
import random
from Objects import RUNNING

from audiocapture import AudioCapture

from detect import detect, _detect
from detect import load_on_memory

import threading
import time

pygame.init()

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
TEST = True
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

points = 0
run = True

AUDIO_FILE_NAME = ''  # name for recorded audio file (*.wav)

if not TEST:
    model = load_on_memory()  # model to be loaded on memory

CAPTURE1_FILENAME = './audio1.wav'
CAPTURE2_FILENAME = './audio2.wav'
CAPTURE3_FILENAME = './audio3.wav'
CAPTURE4_FILENAME = './audio4.wav'
capture_dict = {'capture1': AudioCapture(filename=CAPTURE1_FILENAME, sr=16000, channel_num=1),
                'capture2': AudioCapture(filename=CAPTURE2_FILENAME, sr=16000, channel_num=1),
                'capture3': AudioCapture(filename=CAPTURE3_FILENAME, sr=16000, channel_num=1),
                'capture4': AudioCapture(filename=CAPTURE4_FILENAME, sr=16000, channel_num=1)}
threads_list = []



def main(screen: pygame.Surface):
    global SCREEN_WIDTH, points, run, model, capture_dict
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud(SCREEN_WIDTH)
    points = 0
    font = pygame.font.SysFont('arial', 25, True, True)

    game_speed = 14

    obstacles = []

    death_count = 0

    x_pos_background = 0
    y_pos_background = 380

    def score():
        global points
        nonlocal game_speed, font
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render('Points: ' + str(points), True, (0, 0, 0))
        textRect= text.get_rect()
        textRect.center = (1000, 40)
        screen.blit(text, textRect)

    def background():
        nonlocal game_speed, x_pos_background, y_pos_background
        image_width = BACKGROUND.get_width()
        screen.blit(BACKGROUND, (x_pos_background, y_pos_background))
        screen.blit(BACKGROUND, (x_pos_background + image_width, y_pos_background))
        if x_pos_background < -image_width:
            screen.blit(BACKGROUND, (x_pos_background + image_width, y_pos_background))
            x_pos_background = 0
        x_pos_background -= game_speed

    start_time = time.time()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        screen.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        background()

        player.draw(screen)
        player.update(userInput)

        cloud.draw(screen)
        cloud.update(game_speed)

        score()

        # start recording
        if time.time() - start_time >= 0.25:
            


        # do depending on output result

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SCREEN_WIDTH))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(SCREEN_WIDTH))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(SCREEN_WIDTH))

        for obstacle in obstacles:
            obstacle.draw(screen)
            obstacle.update(game_speed, obstacles)
            if player.dino_rect.colliderect(obstacle.rect):
                #pygame.draw.rect(screen, (255, 0, 0), player.dino_rect, 2)
                pygame.time.delay(200)
                death_count += 1
                menu(death_count)

        clock.tick(30)
        pygame.display.update()


def menu(death_count: int):
    global points, run, capture_dict, threads_list

    # capture = AudioCapture(filename='./test.wav', sr=16000, channel_num=1)

    while run:
        screen.fill((255, 255, 255))
        font = pygame.font.SysFont('arial', 25, True, True)

        if death_count == 0:
            text = font.render('Press any Key to Start', True, (0, 0, 0))
        elif death_count > 0:
            text = font.render('Press any key to Restart', True, (0, 0, 0))
            score = font.render(f'Your Scores : {points}', True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            screen.blit(score, scoreRect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        screen.blit(text, textRect)
        screen.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                for i, capture in enumerate(capture_dict.values()):
                    capture.capture_audio = True
                    capture.capture_audio = True
                    AudioCapture.ready_queue.append(capture)
                    threads_list.append(threading.Thread(target=capture.listen, args=(1, ), name=f'listen_{i}'))
                for listener in threads_list:
                    listener.start()
                main(screen)
                for capture in capture_dict.values():
                    capture.capture_audio = False
                for listener in threads_list:
                    listener.join()


menu(death_count=0)
pygame.quit()
