from sys import argv
import pygame as pg
import json
from random import random
from dataclasses import dataclass, field


@dataclass(slots=True)
class Card:
    front: str
    back: str
    true: int
    false: int

    @classmethod
    def load(cls, dict_card: dict):
        return cls(
            dict_card["front"],
            dict_card["back"],
            dict_card["true"],
            dict_card["false"]
        )

    def dump(self):
        return {
            "front": self.front,
            "back": self.back,
            "true": self.true,
            "false": self.false
        }


@dataclass(slots=True)
class Interface:
    width: int
    height: int
    root: str

    def image(self, path: str):
        return pg.transform.smoothscale(
            pg.image.load(f"{self.root}/{path}").convert(),
            (self.width*0.5, self.height*0.5)
        )

    def load(self):
        with open(f"{self.root}/index.json", "r") as file:
            obj = json.load(file)
        # backup
        with open(f"{self.root}/.index.json", "w") as file:
            json.dump(obj, file, indent=4)
        return obj

    def save(self, dict_deck: list[dict]):
        with open(f"{self.root}/index.json", "w") as file:
            return json.dump(dict_deck, file, indent=4)


@dataclass(slots=True)
class Game:
    deck: list[Card]
    choice: int

    @property
    def card(self):
        return self.deck[self.choice]

    @classmethod
    def load(cls, dict_deck: dict):
        deck = [Card.load(dict_card) for dict_card in dict_deck]
        choice = cls.static_choose(len(deck))
        return cls(deck, choice)
            
    def dump(self):
        return [card.dump() for card in self.deck]

    def hit(self):
        self.deck[self.choice].true += 1
            
    def miss(self):
        self.deck[self.choice].false += 1
            
    def choose(self):
        self.choice = self.static_choose(len(self.deck))
        return self.choice

    @staticmethod
    def static_choose(lenght: int):
        return round((lenght - 1) * random())


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

inter = Interface(WIDTH, HEIGHT, root=argv[1])
game = Game.load(inter.load())

timer = 0
question = True
game.choose()
surf_image.blit(inter.image(game.card.front), (0, 0))


while True:
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
            elif question and event.key == pg.K_SPACE:
                question = not question
                surf_image.blit(inter.image(game.card.back), (0, 0))
            elif not question and event.key == pg.K_t:
                question = not question
                game.choose()
                surf_image.blit(inter.image(game.card.front), (0, 0))
                game.hit()
                inter.save(game.dump())
                timer = 0
            elif not question and event.key == pg.K_f:
                question = not question
                game.choose()
                surf_image.blit(inter.image(game.card.front), (0, 0))
                game.miss()
                inter.save(game.dump())
                timer = 0

    # timer-limit
    if timer > TIMEOUT:
        timer = 0
        game.choose()
        surf_image.blit(inter.image(game.card.front), (0, 0))
        game.miss()
        inter.save(game.dump())

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
