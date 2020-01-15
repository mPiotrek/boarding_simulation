import parameters
import runner
import definitions
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT
from pygame import Surface
from pygame.event import Event
from typing import List, Dict
from collections import defaultdict
from itertools import chain
from dataclasses import astuple


# run it first
pygame.init()


object_size = 64
red_color = (255, 0, 0, 1)
blue_color = (0, 255, 0, 1)


def get_seat_entity() -> Dict:
    # https://www.pygame.org/docs/ref/surface.html
    seat_surface = Surface((object_size, object_size))
    seat_surface.fill(blue_color)
    return {"surface": seat_surface}


def get_passenger_entity() -> Dict:
    passenger_surface = Surface((object_size, object_size))
    passenger_surface.fill(red_color)
    return {"surface": passenger_surface}


# grid size 3 * 2
simulation_objects = [
    (0, 0, get_passenger_entity()), (2, 0, get_passenger_entity()),
    (0, 1, get_seat_entity()), (1, 1, get_seat_entity()), (2, 1, get_seat_entity())
]


def is_esc_down(event: Event) -> bool:
    return event.type == KEYDOWN and event.key == K_ESCAPE


def is_window_close_button_clicked(event: Event) -> bool:
    return event.type == QUIT


def render(entites, screen: Surface) -> None:
    # clear screen
    screen.fill((255, 255, 255, 1))
    # draw
    for entity in entites:
        screen.blit(entity[2]['surface'], [entity[0] * object_size,
                                           entity[1] * object_size])
    # update
    pygame.display.update()


seats = []
agents = defaultdict(lambda: [None, None, get_passenger_entity()])


def play(boarding_mode) -> None:
    clock = pygame.time.Clock()
    # grid size 3 * 2 * scale
    screen = pygame.display.set_mode([(parameters.plane_length+2*parameters.max_shuffle) * object_size,
                                      parameters.plane_width * object_size])

    prev_time = 0
    curr_time = 0
    for agent_id, time, agent in runner.run(boarding_mode, limit=10000):
        # simulation logic
        if time is not None:
            curr_time = time
        x, y = astuple(agent.coords)
        y += parameters.seats_right

        # just because of symmetry
        agents[agent_id][0] = x + parameters.max_shuffle
        agents[agent_id][1] = y
        if (time is not None) and (time > prev_time):
            # rendering
            render(chain(seats, agents.values()), screen)

            # handle events
            if any(is_esc_down(event)
                   or
                   is_window_close_button_clicked(event)
                   for event in pygame.event.get()):
                break

            clock.tick(60)
        prev_time = curr_time
    clock.tick(4)
    while not any(is_esc_down(event)
                  or
                  is_window_close_button_clicked(event)
                  for event in pygame.event.get()):
        pass


play('random_order')
