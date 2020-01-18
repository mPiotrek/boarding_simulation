from parameters import *
from definitions import *
from runner import run
from itertools import product as cartesian, repeat
import pickle
import concurrent.futures as futures

n = int(input("How many time samples for different boarding methods?\n"))
m = int(input("How many time samples for shuffling and stowing comparison?\n"))
o = int(input("How many processes should be spawned?\n"))
r = randint(0, 999999)

if n > 0:
    boarding_methods = ['random_order', 'back_to_front', 'front_to_back', 'back_to_front_four',
                        'front_to_back_four', 'window_middle_aisle', 'steffen_perfect', 'steffen_modified']

    def get_methods_run_time(boarding_method, limit=2500, debug=False):
        ret = list(run(boarding_method, limit=limit, debug=debug))
        if ret[-1][2].state not in {'done', 'ns_done'}:
            print(f"Run exceeded the tick limit={limit}")
            return None

        return next(time for _, time, _ in reversed(ret) if time is not None)

    datapoints = {}
    with futures.ProcessPoolExecutor(max_workers=o) as executor:
        for boarding_method in boarding_methods:
            datapoints[boarding_method] = list(executor.map(
                get_methods_run_time, repeat(boarding_method, n)))
            print(f"{boarding_method}x{n} done")

    pickle_as(f"batch_methods_{n}_{r}", datapoints)
    print(f"pickled as 'batch_methods_{n}_{r}'")
    del get_methods_run_time
    del datapoints
    del boarding_methods


if m > 0:
    boarding_methods = ['random_order', 'back_to_front_four']
    no_shuffles = [False, True]
    no_stowing = [False, True]

    datapoints = {}

    def get_comparison_run_time(boarding_method, no_shuffles, no_stowing, limit=2500, debug=False):
        ret = list(run(boarding_method, no_shuffles=no_shuffles,
                       no_stowing=no_stowing, limit=limit, debug=debug))
        if ret[-1][2].state not in {'done', 'ns_done'}:
            print(f"Run exceeded the tick limit={limit}")
            return None

        return next(time for _, time, _ in reversed(ret) if time is not None)

    with futures.ProcessPoolExecutor(max_workers=o) as executor:
        for bmt in boarding_methods:
            datapoints[bmt] = {}
            for nsh in no_shuffles:
                datapoints[bmt][nsh] = {}
                for nst in no_stowing:
                    datapoints[bmt][nsh][nst] = list(executor.map(
                        get_comparison_run_time, repeat(bmt, m), repeat(nsh, m), repeat(nst, m)))
                    print(
                        f"({bmt}, no_shuffles={nsh}, no_stowing={nst})x{m} done")

    pickle_as(f"batch_comparison_{m}_{r}", datapoints)
    print(f"pickled as 'batch_comparison_{m}_{r}'")
    del get_comparison_run_time
    del datapoints
    del boarding_methods
