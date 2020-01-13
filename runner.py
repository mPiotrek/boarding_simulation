from queue import PriorityQueue
from definitions import *
from parameters import *


def run(boarding_method):
    # People will wait outside the plane
    board = [[None for _ in range(plane_width + total_seats)]
             for _ in range(plane_length)]

    execution_queue = PriorityQueue()

    initialize(execution_queue, board, boarding_method)

    while not execution_queue.empty():
        time, agent = execution_queue.get()
        ret = agent.act(board)

        if ret is not None:
            execution_queue.put(
                (time+ret, agent)
            )
