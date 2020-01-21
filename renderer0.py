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


red_color = (255, 0, 0, 1)
blue_color = (0, 255, 0, 1)


def get_seat_entity() -> Dict:
    # https://www.pygame.org/docs/ref/surface.html
    seat_surface = Surface(
        (parameters.display_scale, parameters.display_scale))
    seat_surface.fill(blue_color)
    return {"surface": seat_surface}


def get_passenger_entity() -> Dict:
    passenger_surface = Surface(
        (parameters.display_scale, parameters.display_scale))
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
        screen.blit(entity[2]['surface'], [entity[0] * parameters.display_scale,
                                           entity[1] * parameters.display_scale])
    # update
    pygame.display.update()


def play(boarding_method, limit=2500, debug=False) -> None:
    seats = []
    agents = defaultdict(lambda: [None, None, get_passenger_entity()])

    clock = pygame.time.Clock()
    # grid size 3 * 2 * scale
    screen = pygame.display.set_mode([(parameters.plane_length+2*parameters.max_shuffle) * parameters.display_scale,
                                      parameters.plane_width * parameters.display_scale])

    for time, updated_agents in runner.run(boarding_method, limit=limit, debug=debug):
        for agent in updated_agents:
            x, y = astuple(agent.coords)
            # just because of the symmetry
            agents[id(agent)][0] = x + parameters.max_shuffle
            agents[id(agent)][1] = y + parameters.seats_right
        # rendering
        clock.tick(parameters.display_framerate)
        render(chain(seats, agents.values()), screen)

        # handle events
        if any(is_esc_down(event)
                or
                is_window_close_button_clicked(event)
                for event in pygame.event.get()):
            break
    else:
        clock.tick(4)
        while not any(is_esc_down(event)
                      or
                      is_window_close_button_clicked(event)
                      for event in pygame.event.get()):
            pass


play('random_order', debug=True)
play('back_to_front', debug=True)
play('front_to_back', debug=True)
play('back_to_front_four', debug=True)
play('front_to_back_four', debug=True)
play('window_middle_aisle', debug=True)
play('steffen_perfect', debug=True)
play('steffen_modified', debug=True)
