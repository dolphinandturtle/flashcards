from sys import argv
import pygame as pg
import json
from random import random
from dataclasses import dataclass, field
from enum import Enum, auto
from bisect import bisect_left


pg.init()

path_back = argv[1]
if "_back.png" not in path_back:
    exit("Invalid front image")
text = argv[2]
path_dir = '/'.join(path_back.split('/')[:-1])
title = path_back.split('/')[-1].replace("_back.png", "_front.png")
path_index = f"{path_dir}/index.json"
path_front = f"{path_dir}/{title}"

SIZE = WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode(SIZE)
clock = pg.time.Clock()

def wraplen(msg, width):
    words = msg.split(' ')
    metrics = [font.size(' '.join(words[0:i]))[0] for i in range(len(words))]
    return bisect_left(
        range(len(words)),
        width,
        key=lambda i: metrics[i]
    )

def wraptext(msg, width):
    lines = []
    while True:
        r = wraplen(msg, width)
        words = msg.split(' ')
        lines.append(' '.join(words[:r-1]))
        if r+1 >= len(words):
            lines.append(' '.join(words[r-1:]))
            break
        msg = ' '.join(words[r-1:])
    return lines

font = pg.font.SysFont("Calibri", 48)

card = pg.Surface((WIDTH*0.666, HEIGHT*0.666))
card.fill("#ffffff")
dy = 0
for line in wraptext(text, WIDTH*0.666):
    card.blit(font.render(line, True, "#000000"), (0, dy))
    dy += font.get_height()
pg.image.save(card, path_front)

with open(path_index, "r") as file:
    index = json.load(file)
    index.append({
        "front": path_front.split('/')[-1],
        "back": path_back.split('/')[-1],
        "true": 0,
        "false": 0
    })

with open(path_index, "w") as file:
    json.dump(index, file, indent=4)
