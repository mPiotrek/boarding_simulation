from queue import PriorityQueue
from copy import deepcopy
from definitions import *
from parameters import *


def run(boarding_method, limit=2500, no_shuffles=False, no_stowing=False, mu=10, debug=False):
    board = [[None for _ in range(board_width)]
             for _ in range(board_length)]

    execution_queue = PriorityQueue()

    # here we could do better:
    yield (-1, [agent for _, agent in initialize(board, execution_queue, boarding_method)])
    # recording = deepcopy(initialize(board, execution_queue, boarding_method))

    prev_time = 0
    frame_time_agents = []
    while not execution_queue.empty():
        time, agent = execution_queue.get()
        if time != prev_time:
            yield (prev_time, frame_time_agents)
            frame_time_agents = []
            prev_time = time
        frame_time_agents.append(agent)

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

        # yield (time, agent)
        # recording.append((id(agent), time, deepcopy(agent)))
        if time >= limit:
            break
    yield (prev_time, frame_time_agents)

    if debug:
        while not execution_queue.empty():
            print(execution_queue.get())

    # return recording


if __name__ == '__main__':
    list(run('random_order', debug=True))
    list(run('back_to_front', debug=True))
    list(run('front_to_back', debug=True))
    list(run('back_to_front_four', debug=True))
    list(run('front_to_back_four', debug=True))
    list(run('window_middle_aisle', debug=True))
    list(run('steffen_perfect', debug=True))
    list(run('steffen_modified', debug=True))
