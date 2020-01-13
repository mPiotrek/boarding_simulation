from dataclasses import dataclass, astuple
from typing      import List, Any
# from random      import getrandbits


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Agent:
    target: Point
    coords: Point
    group:  str
    state:  str = 'go'
    
    # this may very well break execution_queue
    # # ensures random ordering in the execution_queue for simultaneous agents.
    # def __ge__(self, other):
    #     # or maybe there should be (self is other)?
    #     return (self == other) or bool(random.getrandbits(1))
    
    def act(self, board):
        """
        Agent modifies its state based on the board state and returns the duration
        of the current action. Return value None means end of the execution.
        """
        pass


def initialize(board, execution_queue, boarding_method):
    """
    Fills board and execution_queue with newly generated Agents.
    Sets up their target, position, group and puts them in random
    order in the execution_queue as well as in the plane queue.
    """
    pass