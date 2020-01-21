import os
import sys
import pygame
from pygame.locals import QUIT, RLEACCEL, KEYDOWN, K_ESCAPE
import runner
from parameters import max_shuffle, seats_right, plane_length
from parameters import display_width, display_height, display_scale, display_framerate
from dataclasses import astuple


def xyconvert(x, y, distance=False):
    if not distance:
        x += max_shuffle
        y += seats_right
    x *= display_scale
    y *= display_scale
    return x, y


def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if colorkey is -2:
        image = image.convert_alpha()
    else:
        image = image.convert()
    image = pygame.transform.smoothscale(image, (display_scale, display_scale))
    if colorkey is not None and colorkey is not -2:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def should_exit():
    return any(
        event.type == QUIT or
        event.type == KEYDOWN and event.key == K_ESCAPE
        for event in pygame.event.get())


class Seat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # https://freesvg.org/jabela-classroom-seat-layouts
        self.image, self.rect = load_image('seat.png', -2)
        self.rect.topleft = xyconvert(x, y)

    def update(self):
        pass


class AgentSprite(pygame.sprite.Sprite):
    def __init__(self, agent):
        pygame.sprite.Sprite.__init__(self)
        # https://freesvg.org/pacman-vector-drawing
        # https://freesvg.org/suitcase-vector-image9897
        self.flsh, rect = load_image('agent_flip_shift.png', -1)
        self.wlgg, rect = load_image('agent_w_luggage.png', -1)
        self.image, self.rect = self.wlgg, rect
        self.agent = agent
        x, y = astuple(self.agent.coords)
        self.rect.topleft = xyconvert(x, y)

    def update(self):
        x, y = astuple(self.agent.coords)
        self.rect.topleft = xyconvert(x, y)
        if self.agent.state in {'luggage', 'ns_luggage'}:
            self.image = self.flsh


def play(boarding_method, limit=2500, debug=False, no_shuffles=False, no_stowing=False):
    pygame.init()
    resolution = xyconvert(display_width, display_height, distance=True)
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption(f"Boarding Simulation: {boarding_method}")

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((224, 224, 224))

    seats = pygame.sprite.Group(Seat(
        tx, ty*s) for tx in range(plane_length) for ty in range(1, 4) for s in {-1, 1})
    seats.draw(background)

    sprite_agents = pygame.sprite.Group()
    id_to_sprite = {}
    clock = pygame.time.Clock()

    screen.blit(background, (0, 0))
    pygame.display.flip()

    for time, agents in runner.run(boarding_method, limit=limit, debug=False, no_shuffles=no_shuffles, no_stowing=no_stowing):
        sprites_to_update = pygame.sprite.Group()
        for agent in agents:
            if id(agent) not in id_to_sprite:
                new_sprite = AgentSprite(agent)
                sprite_agents.add(new_sprite)
                id_to_sprite[id(agent)] = new_sprite

            sprites_to_update.add(id_to_sprite[id(agent)])

        sprites_to_update.update()

        screen.blit(background, (0, 0))
        sprite_agents.draw(screen)
        pygame.display.flip()

        clock.tick(display_framerate)

        if should_exit():
            break
    else:
        while not should_exit():
            pass


if __name__ == '__main__':
    play('random_order', debug=True)
    play('back_to_front', debug=True)
    play('front_to_back', debug=True)
    play('back_to_front_four', debug=True)
    play('front_to_back_four', debug=True)
    play('window_middle_aisle', debug=True)
    play('steffen_perfect', debug=True)
    play('steffen_modified', debug=True)
