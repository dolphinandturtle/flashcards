from sys import argv
import pygame as pg
import json
import random
from dataclasses import dataclass, field
from enum import Enum, auto


class State(Enum):
    READING = auto()
    REVISING = auto()
    TIMEOUT = auto()


@dataclass(slots=True)
class Card:
    front: str
    back: str
    true: int
    false: int
    interval: int

    @classmethod
    def load(cls, dict_card: dict):
        return cls(
            dict_card["front"],
            dict_card["back"],
            dict_card["true"],
            dict_card["false"],
            dict_card["interval"]
        )

    def dump(self):
        return {
            "front": self.front,
            "back": self.back,
            "true": self.true,
            "false": self.false,
            "interval": self.interval
        }


@dataclass(slots=True)
class Interface:
    width: int
    height: int
    root: str

    def image(self, path: str):
        image = pg.image.load(f"{self.root}/{path}").convert()
        f = min(
            # These scaling parameters 0.8 depend on
            # external values... fix this
            (self.width * 0.8) / image.get_width(),
            (self.height * 0.8) / image.get_height()
        )
        return pg.transform.smoothscale_by(
            pg.image.load(f"{self.root}/{path}").convert(),
            (f, f)
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
    offdeck: list[Card]
    choice: int

    @property
    def card(self):
        return self.deck[self.choice]

    @classmethod
    def load(cls, dict_deck: dict):
        deck = [Card.load(dict_card) for dict_card in dict_deck]
        choice = round((len(deck) - 1) * random.random())
        return cls(deck, [], choice)
            
    def dump(self):
        return [card.dump() for card in self.deck + self.offdeck]

    def hit(self):
        self.deck[self.choice].true += 1
        self.deck[self.choice].interval /= 2
        self.offdeck.append(self.deck.pop(self.choice))
            
    def miss(self):
        self.deck[self.choice].interval *= 3/2
        self.deck[self.choice].false += 1

    def choose(self):
        population = range(len(self.deck))
        weights = [(card.false + 1) / (card.true + 1) for card in self.deck]
        self.choice = random.choices(population, weights)[0]
        return self.choice


SIZE = WIDTH, HEIGHT = 800, 600

# Colors
BACKGROUND = "#2222aa"
CARD = "#ffffff"
TEXT = "#000000"

pg.init()
calibri = pg.font.SysFont("Calibri", 52)
pg.display.set_caption("Flashcards")
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
clock = pg.time.Clock()

surf_timer = pg.Surface((WIDTH*0.1, HEIGHT*0.1))
surf_timer.fill(CARD)

card_size = card_width, card_height = WIDTH*0.8, HEIGHT*0.8
surf_card = pg.Surface(card_size)
surf_card.fill(CARD)

image_size = image_width, image_height = WIDTH*0.8, HEIGHT*0.8
surf_image = pg.Surface((WIDTH*0.8, HEIGHT*0.8))
surf_image.fill(CARD)

inter = Interface(WIDTH, HEIGHT, root=argv[1])
game = Game.load(inter.load())

timer = 0
state = State.READING
game.choose()
surf_image.fill(CARD)
surf_image.blit(inter.image(game.card.front), (0, 0))


while True:
    match state:
        case State.READING:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    print(f"Progressed {len(game.offdeck)}/{len(game.deck) + len(game.offdeck)} cards")
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    surf_image.fill(CARD)
                    surf_image.blit(inter.image(game.card.back), (0, 0))
                    state = State.REVISING

        case State.REVISING:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    print(f"Progressed {len(game.offdeck)}/{len(game.deck) + len(game.offdeck)} cards")
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_t:
                    game.hit()
                    # End condition
                    if len(game.deck) == 0:
                        print("Gg. You won!")
                        pg.quit()
                        exit()
                    game.choose()
                    surf_image.fill(CARD)
                    surf_image.blit(inter.image(game.card.front), (0, 0))
                    inter.save(game.dump())
                    timer = 0
                    state = State.READING
                elif event.type == pg.KEYDOWN and event.key == pg.K_f:
                    game.miss()
                    game.choose()
                    surf_image.fill(CARD)
                    surf_image.blit(inter.image(game.card.front), (0, 0))
                    inter.save(game.dump())
                    timer = 0
                    state = State.READING

        case State.TIMEOUT:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    print(f"Progressed {len(game.offdeck)}/{len(game.deck) + len(game.offdeck)} cards")
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    game.miss()
                    game.choose()
                    surf_image.fill(CARD)
                    surf_image.blit(inter.image(game.card.front), (0, 0))
                    inter.save(game.dump())
                    timer = 0
                    state = State.READING

    # independent transition
    if timer > game.card.interval:
        surf_image.fill(CARD)
        surf_image.blit(inter.image(game.card.back), (0, 0))
        state = State.TIMEOUT

    screen.fill(BACKGROUND)

    surf_timer.fill(CARD)
    surf_timer.blit(calibri.render(f"{game.card.interval - int(timer)}", antialias=True, color=TEXT), (0, 0))
    screen.blit(surf_timer, (0, 0))

    # Needs centering
    x = (WIDTH - card_width)/2
    y = (HEIGHT - card_height)/2
    screen.blit(surf_card, (x, y))

    # Needs centering
    x = (WIDTH - image_width)/2
    y = (HEIGHT - image_height)/2
    screen.blit(surf_image, (x, y))

    match state:
        case State.READING:
            timer += 1/30

    pg.display.update()
    clock.tick(30)
