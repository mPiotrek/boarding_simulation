from dataclasses import dataclass, astuple
from queue import PriorityQueue
from parameters import *
from random import getrandbits, shuffle
from itertools import chain


@dataclass
class Point:
    x: int
    y: int

    def __str__(self):
        return f"(x={self.x}, y={self.y})"

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x+other.x, self.y+other.y)
        elif isinstance(other, tuple):
            return Point(self.x+other[0], self.y+other[1])
        else:
            return NotImplemented


@dataclass
class Agent:
    target: Point
    coords: Point
    group:  str
    state:  str = 'go'

    def __str__(self):
        return f"(t={str(self.target):>13}, c={str(self.coords):>13}, g={self.group}, s={self.state})"

    # this may very well break execution_queue, so disabled for now
    # ensures random ordering in the execution_queue for simultaneous agents.
    def __lt__(self, other):
        # or maybe there should be (self is not other)?
        return (self != other) and bool(getrandbits(1))

    def move(self, board, dx, dy):
        """
        Moves agent if possible. Returns duration in ticks
        """
        x, y = astuple(self.coords)
        if board[x+dx][y+dy] is None:
            board[x+dx][y+dy] = self
            board[x][y] = None
            self.coords += dx, dy
        else:
            raise Exception(
                f"{self}, tried to move by [{dx},{dy}] to the occupied location")

    def act(self, board, execution_queue, time):
        """
        Agent modifies its state based on the board state and returns the duration
        of the current action. Return value None means end of the execution.
        """
        x, y = astuple(self.coords)

        def go():
            if y != aisle_y:
                raise Exception(f"Agent {self} not in aisle in 'go' state")

            if x < self.target.x-1:
                if (board[x+1][y] is None) and no_shuffle_conflict(board, x+1, y):
                    self.move(board, 1, 0)
                    return walk_tick_cnt
                else:
                    return skip_tick_cnt
            elif x == self.target.x-1:
                self.state = 'my_turn'
                return skip_tick_cnt
            else:
                raise Exception(
                    f"Agent {self} went past its target in the 'go' state")

        def my_turn():
            if x != self.target.x-1:
                raise Exception(
                    f"Agent {self} not just before its row in the 'my_turn' state")
            if y != aisle_y:
                raise Exception(
                    f"Agent {self} not in aisle in 'my_turn' state")

            if (board[x+1][y] is None) and no_shuffle_need(board, self.target.x, self.target.y) and no_shuffle_other(board, self.target.x, self.target.y):
                self.move(board, 1, 0)
                self.state = 'luggage'
                return walk_tick_cnt
            else:
                return skip_tick_cnt

            # if (board[x+1][y] is None) and no_shuffle_conflict(board, x+1, y):
            #     to_shuffle = get_shuffle_need(board, self.target.x, self.target.y)
            #     if len(to_shuffle) == 0:
            #         self.move(board, 1, 0)
            #         self.state = 'luggage'
            #         return walk_tick_cnt
            #     elif len(to_shuffle) == 1:
            #         if to_shuffle == (None,):
            #             self.move(board, 1, 0)
            #             self.state = 'luggage'
            #             return walk_tick_cnt
            #         else:
            #             (j,) = to_shuffle
            #             if j.state == 'waiting':
            #                 j.state = 'shuffle_1b'
            #                 execution_queue.put(time+skip_tick_cnt, j)
            #                 return skip_tick_cnt
            #     elif len(to_shuffle) == 2:
            #         if to_shuffle == (None, None):
            #             self.move(board, 1, 0)
            #             self.state = 'luggage'
            #             return walk_tick_cnt
            #         else:
            #             (k,l) = to_shuffle
            #             if k is None:
            #                 if k.state == 'waiting':
            #                     k.state = 'shuffle_1b'
            #                     execution_queue.put(time+skip_tick_cnt, k)
            #                     return skip_tick_cnt
            #             elif l is None:
            #                 if l.state == 'waiting':
            #                     l.state = 'shuffle_1a'
            #                     execution_queue.put(time+skip_tick_cnt, l)
            #                     return skip_tick_cnt
            #             else:
            #                 if k.state == 'waiting' and l.state == 'waiting':
            #                     k.state = 'shuffle_2c'
            #                     execution_queue.put(time+skip_tick_cnt, k)
            #                     l.state = 'shuffle_2a'
            #                     execution_queue.put(time+skip_tick_cnt, l)
            #                     return skip_tick_cnt
            # return skip_tick_cnt

        def luggage():
            if x != self.target.x:
                raise Exception(
                    f"Agent {self} not in its row in the 'luggage' state")
            if y != aisle_y:
                raise Exception(
                    f"Agent {self} not in aisle in 'luggage' state")

            self.state = 'entering'
            return skip_tick_cnt

        def entering():
            if x != self.target.x:
                raise Exception(
                    f"Agent {self} not in its row in the 'entering' state")

            if y != self.target.y:
                dy = (self.target.y - y)
                dy = dy//abs(dy)
                if board[x][y+dy] is None:
                    self.move(board, 0, dy)
                    return walk_tick_cnt
                else:
                    return skip_tick_cnt
            else:
                self.state = 'is_that_all'
                return skip_tick_cnt

        def is_that_all():
            if x != self.target.x:
                raise Exception(
                    f"Agent {self} not in its row in the 'waiting' state")
            if y != self.target.y:
                raise Exception(
                    f"Agent {self} not in its seat in 'waiting' state")

            ys = range(*((seats_left, y, -1) if y >
                         0 else (-seats_right, y, 1)))
            if all(board[x][_y] is not None for _y in ys):
                self.state = 'done'
                return None
            else:
                self.state = 'waiting'
                return skip_tick_cnt

        def waiting():
            if x != self.target.x:
                raise Exception(
                    f"Agent {self} not in its row in the 'waiting' state")
            if y != self.target.y:
                raise Exception(
                    f"Agent {self} not in its seat in 'waiting' state")

            if board[x-1][0] is not None and board[x-1][0].target.x == x:
                ty = board[x-1][0].target.y
                ys = range(0, ty, ty//abs(ty))
                if y in ys:
                    # self.state='shuffleXD'
                    if y in {-1, 1}:
                        if board[x][2*y//abs(y)] is None:
                            self.state = 'shuffle_1b'
                            return skip_tick_cnt
                        elif board[x][2*y//abs(y)].state == 'waiting' or board[x][2*y//abs(y)].state.startswith('shuffle'):
                            self.state = 'shuffle_2c'
                            return skip_tick_cnt
                    elif y in {-2, 2}:
                        if board[x][0] is not None and board[x][0].target.y in ys:
                            return skip_tick_cnt
                        else:
                            if board[x][y//abs(y)] is None:
                                self.state = 'shuffle_1a'
                                return skip_tick_cnt
                            else:
                                self.state = 'shuffle_2a'
                                return skip_tick_cnt
            return skip_tick_cnt

        def shuffle():
            if self.state.endswith('a'):
                dy = -y//abs(y)
                if board[x][y+dy] is None:
                    self.move(board, 0, dy)
                    self.state = self.state[:-1]+'b'
                    return walk_tick_cnt
                else:
                    return skip_tick_cnt
            elif self.state.endswith('b'):
                if y != 0:
                    dy = -y//abs(y)
                    if board[x][y+dy] is None and (self.state.endswith('2b') or no_shuffle_conflict(board, x, 0)):
                        self.move(board, 0, dy)
                        return walk_tick_cnt
                    else:
                        return skip_tick_cnt
                elif x == self.target.x:
                    if self.state.endswith('1b'):
                        if board[x+1][y] is None:
                            self.move(board, 1, 0)
                            return walk_tick_cnt
                        else:
                            return skip_tick_cnt
                    else:  # .endswith('2b')
                        if board[x+1][y] is None:
                            self.move(board, 1, 0)
                            return walk_tick_cnt
                        else:
                            return skip_tick_cnt
                else:  # now shuffle ends
                    if (board[x-2][0] is not None and
                        # in same row
                        board[x-2][0].target.x == self.target.x and
                        # on same side
                        board[x-2][0].target.y * self.target.y > 0 and
                        # it's The One, who elese could it be
                        not self.state.endswith('2b') and
                            not (abs(board[x-2][0].target.y) > abs(self.target.y))):  # either way will be first
                        return skip_tick_cnt
                    else:
                        if board[x-1][0] is None:
                            self.move(board, -1, 0)
                            self.state = 'entering'
                            return walk_tick_cnt
                        else:
                            return skip_tick_cnt
            elif self.state.endswith('c'):
                if y != 0:
                    dy = -y//abs(y)
                    if board[x][y+dy] is None and no_shuffle_conflict(board, x, 0):
                        self.move(board, 0, dy)
                        return walk_tick_cnt
                    else:
                        return skip_tick_cnt
                elif y == 0 and x == self.target.x and no_shuffle_conflict(board, x+1, 0):
                    if board[x+1][0] is None:
                        self.move(board, 1, 0)
                        return walk_tick_cnt
                    else:
                        return skip_tick_cnt
                elif x == self.target.x+1:
                    if (board[x-2][0] is not None and
                        # in same row
                        board[x-2][0].target.x == self.target.x and
                            board[x-2][0].target.y * self.target.y > 0):  # on same side
                        if board[x+1][0] is None:
                            self.move(board, 1, 0)
                            return walk_tick_cnt
                        else:
                            return skip_tick_cnt
                    else:
                        if board[x-1][0] is None:
                            self.move(board, -1, 0)
                            self.state = 'entering'
                            return walk_tick_cnt
                        else:
                            return skip_tick_cnt
                else:
                    if (board[x-3][0] is not None and
                        # in same row
                        board[x-3][0].target.x == self.target.x and
                            board[x-3][0].target.y * self.target.y > 0):  # on same side
                        return skip_tick_cnt
                    else:  # idziemy w lewo
                        if board[x-1][0] is None:
                            self.move(board, -1, 0)
                            return walk_tick_cnt
                        else:
                            return skip_tick_cnt
            else:
                raise Exception(f"Agent {self} in invalid 'shuffle' state")

            return skip_tick_cnt

        if self.state == 'go':
            return go()
        elif self.state == 'my_turn':
            return my_turn()
        elif self.state == 'luggage':
            return luggage()
        elif self.state == 'entering':
            return entering()
        elif self.state == 'is_that_all':
            return is_that_all()
        elif self.state == 'waiting':
            return waiting()
        elif self.state.startswith('shuffle'):
            return shuffle()
        elif self.state == 'done':
            raise Exception(
                "Agent {self} in state 'done' appeared in the 'execution_queue'")
        else:
            return None


def no_shuffle_conflict(board, x, y):
    return all(
        board[x+dx][0] is None
        or
        board[x+dx][0].coords.x <= board[x+dx][0].target.x
        for dx
        in range(1, 1+max_shuffle)
    )


def no_shuffle_other(board, tx, ty):
    # no shuffle for any other agent here
    return all(
        board[tx+dx][0] is None
        or
        board[tx+dx][0].target.x != tx  # not in shuffle here
        or
        board[tx+dx][0].target.y * ty > 0  # target on the same side
        and
        True
        # idę window & shuffle_2 = moje
        # idę window & shuffle_1 & idzie middle = moje
        # idę window & shuffle_1 & idzie ailse = mogę iść, bo jeśli nie moje to poczekam
        # idę middle = jak się wepchnę to będzie spoko
        for dx
        in range(1, 1+max_shuffle)
    )


def no_shuffle_need(board, x, y):
    ys = range(0, y, 1 if y > 0 else -1)

    return all(
        board[x][_y] is None or board[x][_y].target.y not in ys
        for _y
        in ys
    )


def get_shuffle_need(board, x, y):
    ys = range(0, y, 1 if y > 0 else -1)

    if all(
        board[x][_y] is None or board[x][_y].target.y not in ys
        for _y
        in ys
    ):
        return (None, None)
    else:
        return tuple(
            board[x][_y]
            for _y
            in ys
        )


def initialize(board, execution_queue: PriorityQueue, boarding_method):
    """
    Fills board and execution_queue with freshly generated Agents.
    Sets up their target, position, group and puts them in random
    order in the execution_queue as well as in the plane queue.
    """

    if False:
        pass
    elif boarding_method == 'random_order':
        time_agents = [(0, Agent(Point(tx, ty*(2*s-1)), Point(0, 0), 0)) for tx in range(plane_length)
                       for ty in range(1, 4) for s in range(2)]
        shuffle(time_agents)
        for i, (time, agent) in enumerate(time_agents):
            agent.coords.x = i-total_agents
    elif boarding_method == '_test_b2f':
        time_agents = [(0, Agent(Point(tx, ty*(2*s-1)), Point(tx*6+s*3+ty-total_agents, 0), 0)) for tx in range(plane_length)
                       for ty in range(1, 4) for s in range(2)]
    elif boarding_method == '_test_f2b':
        time_agents = [(0, Agent(Point(tx, ty*(2*s-1)), Point(-tx*6-s*3-ty-1, 0), 0)) for tx in range(plane_length)
                       for ty in range(1, 4) for s in range(2)]
    elif boarding_method == '_test_0wr':
        target = Point(0, -seats_right)
        coords = Point(-1, aisle_y)
        x, y = astuple(coords)

        agent = Agent(target, coords, 0)

        board[x][y] = agent
        execution_queue.put((0, agent))
        return [id(agent), 0, agent]
    elif boarding_method == '_test_2r_shuffle':
        t1 = Point(0, -seats_right+0)
        t2 = Point(0, -seats_right+1)
        c1 = Point(-2+0, aisle_y)
        c2 = Point(-2+1, aisle_y)
        agents = []

        for target, coords in [(t1, c1), (t2, c2)]:
            x, y = astuple(coords)
            agent = Agent(target, coords, 0)

            board[x][y] = agent
            execution_queue.put((0, agent))
            agents.append((id(agent), 0, agent))
        return agents
    elif boarding_method == '_test_2s_shuffle':
        t1 = Point(0, -seats_right+0)
        t2 = Point(0, -seats_right+1)
        c1 = Point(-2+1, aisle_y)
        c2 = Point(-2+0, aisle_y)
        agents = []

        for target, coords in [(t1, c1), (t2, c2)]:
            x, y = astuple(coords)
            agent = Agent(target, coords, 0)

            board[x][y] = agent
            execution_queue.put((0, agent))
            agents.append((id(agent), 0, agent))
        return agent
    elif boarding_method == '_test_3r_shuffle':
        t1 = Point(0, -seats_right+0)
        t2 = Point(0, -seats_right+1)
        t3 = Point(0, -seats_right+2)
        c1 = Point(-3+0, aisle_y)
        c2 = Point(-3+1, aisle_y)
        c3 = Point(-3+2, aisle_y)
        agents = []

        for target, coords in [(t1, c1), (t2, c2), (t3, c3)]:
            x, y = astuple(coords)
            agent = Agent(target, coords, 0)

            board[x][y] = agent
            execution_queue.put((0, agent))
            agents.append((id(agent), 0, agent))
        return agents
    elif boarding_method == '_test_3s_shuffle':
        t1 = Point(0, -seats_right+0)
        t2 = Point(0, -seats_right+1)
        t3 = Point(0, -seats_right+2)
        c1 = Point(-3+2, aisle_y)
        c2 = Point(-3+1, aisle_y)
        c3 = Point(-3+0, aisle_y)
        agents = []

        for target, coords in [(t1, c1), (t2, c2), (t3, c3)]:
            x, y = astuple(coords)
            agent = Agent(target, coords, 0)

            board[x][y] = agent
            execution_queue.put((0, agent))
            agents.append((id(agent), 0, agent))
        return agents
    else:
        return NotImplemented

    for time, agent in time_agents:
        board[agent.coords.x][agent.coords.y] = agent
        execution_queue.put((time, agent))

    return [(id(agent), time, agent)for time, agent in time_agents]
