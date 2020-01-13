from dataclasses import dataclass, astuple
from typing      import List, Any


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Agent:
    target: Point
    coords: Point
    group:  str
    state:  str
