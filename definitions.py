from dataclasses import dataclass, astuple
from typing      import List


@dataclass
class Point:
    x: int = None
    y: int = None


@dataclass
class Agent:
    target: Point = None
    coords: Point = None
    group:  str   = None
    state:  str   = None

@dataclass
class Board:
    def __init__(self, w: int, h: int):
        self.content = [[None for _ in h] for _ in w]
    content: List[List] = None
