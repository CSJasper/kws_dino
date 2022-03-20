import pygame
from Objects import Dinosaur
from Objects import Cloud
from Objects import BACKGROUND
from Objects import SmallCactus
from Objects import LargeCactus
from Objects import Bird
import random
from Objects import RUNNING


import numpy as np
import pyaudio
import threading
from multiprocessing import Queue
import torchaudio
import torch
import time


import sys

pygame.init()

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
TEST = True
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

points = 0
run = True
record = False
SR = 16000
CHUNK_SIZE = SR // 4
Queue_audio = Queue()
command_queue = Queue()
now_recording = False

## -- 1. load model
model_path = "./results/best_model.pt"
model = torch.load(model_path)
model.eval()

## -- 2. load support data
support_path = "./support.pt"
xs = torch.load(support_path)  # [3, 10, 1, 51, 40], [3-way, 10-shots, 1, T, f]


def inference(input_chunk, model: torch.nn.Module):
    # normalize
    input_chunk = input_chunk.astype(np.float32)
    input_chunk = input_chunk / (np.max(input_chunk) - np.min(input_chunk))

    # numpy to tensor, extract mfcc feature
    input_chunk = torch.tensor(input_chunk)
    xq = extract_features(input_chunk)  # [1. 51. 40] , [1 , T, f]
    xq = xq.unsqueeze(0)
    xq = xq.unsqueeze(0)  # [1,1,1,51,40]

    sample = {}
    sample['xs'] = xs
    sample['xq'] = xq

    output = model.loss(sample)
    return output


def generate_input_chunk(input_chunk_segment):
    for i in range(len(input_chunk_segment)):
        if i == 0:
            input_chunk = input_chunk_segment[i]
        else:
            input_chunk = np.concatenate([input_chunk, input_chunk_segment[i]], axis = 1)
    return input_chunk


def get_vad_flag(input_chunk):
    power = np.abs(input_chunk).mean()
    if power >= 1000:
        vad = True
    else:
        vad = False
    return vad


def start_KWS(Queue_audio, model: torch.nn.Module):
    chunk_list = []
    while not command_queue.empty():
        command_queue.get_nowait()
    print('Listening start')
    while record:
        chunk = Queue_audio.get()
        chunk_list.append(chunk)

        if len(chunk_list) >= 4:
            input_chunk = generate_input_chunk(chunk_list[:4]) # select last 4 chunk and concat them so as to make 1 sec input
            del chunk_list[0]

            vad = get_vad_flag(input_chunk)
            #print(vad)

            if vad:
                output = inference(input_chunk, model)
            else:
                output = torch.tensor([4])
            #print(output)
            command_queue.put(output.numpy())
    print('Listening stopped')


def start_stream(Queue_audio, stream):
    global now_recording
    if now_recording:
        return
    while record:
        now_recording = True
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        data = np.fromstring(data, dtype=np.int16)
        data = np.expand_dims(data, axis=0) # [1, 4000]

        Queue_audio.put(data)
    now_recording = False


## hyperparameters used for extracting MFCC feature
window_size_ms = 40
window_stride_ms = 20
sample_rate = 16000
feature_bin_count = 40


def build_mfcc_extractor():
    frame_len = window_size_ms / 1000
    stride = window_stride_ms / 1000
    mfcc = torchaudio.transforms.MFCC(sample_rate,
                                    n_mfcc=feature_bin_count,
                                    melkwargs={
                                        'hop_length' : int(stride*sample_rate),
                                        'n_fft' : int(frame_len*sample_rate)})
    return mfcc


mfcc = build_mfcc_extractor()


def extract_features(sound):
    features = mfcc(sound)[0] # just one channel
    features = features.T # f x t -> t x f
    features = torch.unsqueeze(features, 0)
    return features


def check_audio_env(pypy):
    print('============================================')
    print(pypy.get_device_count())
    print('============================================')
    for index in range(pypy.get_device_count()):
        desc = pypy.get_device_info_by_index(index)
        print("DEVICE: %s INDEX: %s RATE:%s"%(desc['name'],index,int(desc["defaultSampleRate"])))


def get_audio_env_list(pypy):
    audio_env_list = []
    for index in range(pypy.get_device_count()):
        desc = pypy.get_device_info_by_index(index)
        audio_env_list.append(f'DEVICE: {desc["name"]} INDEX: {index}, SR: {int(desc["defaultSampleRate"])}')
    return audio_env_list


def main(screen: pygame.Surface):
    global SCREEN_WIDTH, points, run, record
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud(SCREEN_WIDTH)
    points = 0
    font = pygame.font.SysFont('arial', 25, True, True)

    game_speed = 14

    obstacles = []

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False


        screen.fill((255, 255, 255))
        userInput = {pygame.K_UP: False, pygame.K_DOWN: False}
        # 점프 0 뛰어 1 숙여 2 nothing 4
        if time.time() - start_time >= 1.0:
            command = command_queue.get()
            if command == 0 or command == 1:
                userInput[pygame.K_UP] = True
            elif command == 2:
                userInput[pygame.K_DOWN] = True
            start_time = time.time()

        print(f'keyUP: {userInput[pygame.K_UP]}, keyDown: {userInput[pygame.K_DOWN]}')


        background()

        player.draw(screen)
        player.update(userInput)

        cloud.draw(screen)
        cloud.update(game_speed)

        score()

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
                pygame.draw.rect(screen, (255, 0, 0), player.dino_rect, 2)
                '''
                pygame.time.delay(200)
                death_count += 1
                menu(death_count)
                '''


        clock.tick(30)
        pygame.display.update()


def menu(death_count: int):
    global points, run, record

    record = False
    stream = pypy.open(format=pyaudio.paInt16, channels=1, rate=SR, input=True, input_device_index=device_index, frames_per_buffer=CHUNK_SIZE)
    streaming = threading.Thread(target=start_stream, args=(Queue_audio, stream))
    kws_spotting = threading.Thread(target=start_KWS, args=(Queue_audio, model))
    
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
                record = True
                streaming.start()
                kws_spotting.start()
                main(screen)
                streaming.join()
                kws_spotting.join()
                

pypy = pyaudio.PyAudio()
check_audio_env(pypy)

print('Enter recording device number:', end='')
device_index = int(sys.stdin.readline())

menu(death_count=0)
pygame.quit()
