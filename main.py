from sys import argv
import pygame as pg
import json
from random import random


TIMEOUT = 120
SIZE = WIDTH, HEIGHT = 800, 600

# Colors
BACKGROUND = "#2222aa"
CARD = "#ffffff"
TEXT = "#000000"

pg.init()
calibri = pg.font.SysFont("Calibri", 24)
pg.display.set_caption("Flashcards")
screen = pg.display.set_mode(SIZE)
clock = pg.time.Clock()

surf_timer = pg.Surface((WIDTH*0.1, HEIGHT*0.1))
surf_timer.fill(CARD)

surf_card = pg.Surface((WIDTH*0.666, HEIGHT*0.666))
surf_card.fill(CARD)

surf_image = pg.Surface((WIDTH*0.5, HEIGHT*0.5))
surf_image.fill(CARD)

PATH_DECK = argv[1]
with open(f"{PATH_DECK}/index.json", "r") as file:
    deck = json.load(file)
# backup file
with open(f"{PATH_DECK}/.index.json", "w") as file:
    json.dump(deck, file, indent=2)

timer = 0

question = True
choice = round(len(deck) * random())
image = pg.image.load(PATH_DECK + '/' + deck[choice]["question" if question else "answer"]).convert()
surf_image.blit(pg.transform.smoothscale(image, (WIDTH*0.5, HEIGHT*0.5)), (0, 0))


while True:
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
            elif question and event.key == pg.K_SPACE:
                question = not question
                choice = round(len(deck) * random())
                image = pg.image.load(PATH_DECK + '/' + deck[choice]["question" if question else "answer"]).convert()
                surf_image.blit(pg.transform.smoothscale(image, (WIDTH*0.5, HEIGHT*0.5)), (0, 0))
            elif not question and event.key == pg.K_t:
                question = not question
                choice = round(len(deck) * random())
                image = pg.image.load(PATH_DECK + '/' + deck[choice]["question" if question else "answer"]).convert()
                surf_image.blit(pg.transform.smoothscale(image, (WIDTH*0.5, HEIGHT*0.5)), (0, 0))
                deck[choice]["true"] += 1
                with open(f"{PATH_DECK}/index.json", "w") as file:
                    json.dump(deck, file, indent=4)
                timer = 0
            elif not question and event.key == pg.K_f:
                question = not question
                choice = round(len(deck) * random())
                image = pg.image.load(PATH_DECK + '/' + deck[choice]["question" if question else "answer"]).convert()
                surf_image.blit(pg.transform.smoothscale(image, (WIDTH*0.5, HEIGHT*0.5)), (0, 0))
                deck[choice]["false"] += 1
                with open(f"{PATH_DECK}/index.json", "w") as file:
                    json.dump(deck, file, indent=4)
                timer = 0

    # timer-limit
    if timer > TIMEOUT:
        timer = 0
        choice = round(len(deck) * random())
        image = pg.image.load(PATH_DECK + '/' + deck[choice]["question" if question else "answer"]).convert()
        surf_image.blit(pg.transform.smoothscale(image, (WIDTH*0.5, HEIGHT*0.5)), (0, 0))
        deck[choice]["false"] += 1
        with open(f"{PATH_DECK}/index.json", "w") as file:
            json.dump(deck, file, indent=4)

    screen.fill(BACKGROUND)

    # Needs centering
    screen.blit(surf_card, (120, 100))

    # Needs centering
    screen.blit(surf_image, (180, 140))

    surf_timer.fill(CARD)
    surf_timer.blit(calibri.render(f"{int(timer)}", antialias=True, color=TEXT), (0, 0))
    screen.blit(surf_timer, (120, 100))

    pg.display.update()
    clock.tick(30)
    if question:
        timer += 1/30
