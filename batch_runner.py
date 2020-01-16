from parameters import *
from definitions import *
from runner import run
from itertools import product as cartesian
import pickle
import concurrent.futures as futures

n = int(input("How many time samples for different boarding methods?\n"))
m = int(input("How many time samples for shuffling and stowing comparison?\n"))
o = int(input("How many processes should be spawned?\n"))


boarding_methods = ['random_order', 'back_to_front', 'front_to_back', 'back_to_front_four',
                    'front_to_back_four', 'window_middle_aisle', 'steffen_perfect', 'steffen_modified']
datapoints = {bm: list() for bm in boarding_methods}


def append_run_time(boarding_method, limit=2500, debug=False):
    ret = list(run(boarding_method, limit=limit, debug=debug))
    if ret[-1][2].state not in {'done', 'ns_done'}:
        print(f"Run exceeded the tick limit={limit}")
        datapoints[boarding_method].append(None)
        return
    datapoints[boarding_method].append(
        next(time for _, time, _ in reversed(ret) if time is not None))


with futures.ProcessPoolExecutor(max_workers=o) as executor:
    for _ in range(n):
        for boarding_method in boarding_methods:
            executor.submit(append_run_time, boarding_method)
pickle_as(f"batch_methods_{n}", datapoints)
del append_run_time
del datapoints
del boarding_methods

print("done batch_methods")

boarding_methods = ['random_order', 'back_to_front_four']
no_shuffles = [False, True]
no_stowing = [False, True]
datapoints = {(bm, nsh, nst): list() for bm, nsh, nst in cartesian(
    boarding_methods, no_shuffles, no_stowing)}


def append_run_time(boarding_method, no_shuffles, no_stowing, limit=2500, debug=False):
    ret = list(run(boarding_method, no_shuffles=no_shuffles,
                   no_stowing=no_stowing, limit=limit, debug=debug))
    if ret[-1][2].state not in {'done', 'ns_done'}:
        print(f"Run exceeded the tick limit={limit}")
        datapoints[(boarding_method, no_shuffles, no_stowing)].append(None)
        return
    datapoints[boarding_method].append(
        next(time for _, time, _ in reversed(ret) if time is not None))


with futures.ProcessPoolExecutor(max_workers=o) as executor:
    for _ in range(m):
        for boarding_method in boarding_methods:
            for nsh in no_shuffles:
                for nst in no_stowing:
                    executor.submit(append_run_time, boarding_method, nsh, nst)
pickle_as(f"batch_comparison_{m}", datapoints)
del append_run_time
del datapoints
del boarding_methods

print("done batch_comparison")
