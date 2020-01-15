from queue import PriorityQueue
from copy import deepcopy
from definitions import *
from parameters import *


def run(boarding_method, limit=1000, debug=False):
    board = [[None for _ in range(board_width)]
             for _ in range(board_length)]

    execution_queue = PriorityQueue()

    recording = deepcopy(initialize(board, execution_queue, boarding_method))

    while not execution_queue.empty():
        time, agent = execution_queue.get()
        if debug:
            print(f"{id(agent)%10000:>4} {time} : {agent}", end='')
        ret = agent.act(board, execution_queue, time)
        if debug:
            print(f" -> {agent}")

        if ret is not None:
            execution_queue.put(
                (time+ret, agent)
            )

        recording.append((id(agent), time, deepcopy(agent)))
        if time >= limit:
            break

    if debug:
        while not execution_queue.empty():
            print(execution_queue.get())

    return recording


if __name__ == '__main__':
    run('_test_b2f', limit=1000, debug=True)
