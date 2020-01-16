from queue import PriorityQueue
from copy import deepcopy
from definitions import *
from parameters import *
from random import randint
import pickle


def run(boarding_method, limit=2500, debug=False):
    board = [[None for _ in range(board_width)]
             for _ in range(board_length)]

    execution_queue = PriorityQueue()

    yield from initialize(board, execution_queue, boarding_method)
    # recording = deepcopy(initialize(board, execution_queue, boarding_method))

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

        yield (id(agent), time, agent)
        # recording.append((id(agent), time, deepcopy(agent)))
        if time >= limit:
            break

    if True or debug:
        while not execution_queue.empty():
            print(execution_queue.get())

    # return recording


if __name__ == '__main__':
    # while True:
    randid = randint(0,999999)
    for i in range(200):
        d = dict()
        for boarding_mode in ['random_order', 'back_to_front', 'front_to_back', 'back_to_front_four', 'front_to_back_four', 'window_middle_aisle', 'steffen_perfect', 'steffen_modified']:
            ret = list(run(boarding_mode, limit=2500, debug=True))
            d[boarding_mode] = None
            if ret[-1][2].state != 'done':
                continue
            d[boarding_mode] = max(time for _,time,_ in ret if time is not None)
        with open(f"./pickle_dumps/stats_{randid}_{i}.pkl", 'wb') as f:
            pickle.dump(d, f)
