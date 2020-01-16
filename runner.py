from queue import PriorityQueue
from copy import deepcopy
from definitions import *
from parameters import *


def run(boarding_method, limit=2500, no_shuffles=False, no_stowing=False, mu=10, debug=False):
    board = [[None for _ in range(board_width)]
             for _ in range(board_length)]

    execution_queue = PriorityQueue()

    yield from initialize(board, execution_queue, boarding_method)
    # recording = deepcopy(initialize(board, execution_queue, boarding_method))

    while not execution_queue.empty():
        time, agent = execution_queue.get()
        if debug:
            print(f"{id(agent)%10000:>4} {time} : {agent}", end='')
        ret = agent.act(board, execution_queue, time,
                        no_shuffles=no_shuffles, no_stowing=no_stowing, mu=mu)
        if debug:
            print(f" -> {agent}")

        if ret is not None:
            execution_queue.put(
                (time+ret, agent)
            )

        yield (id(agent), time, agent)
        # recording.append((id(agent), time, deepcopy(agent)))
        if time >= limit:
            break

    if True or debug:
        while not execution_queue.empty():
            print(execution_queue.get())

    # return recording


if __name__ == '__main__':
    pass
