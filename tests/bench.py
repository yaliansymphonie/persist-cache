"""Benchmark persist-cache against other popular persistent caching libraries."""
import random
import time
from typing import Callable

import cachier
import locache
from joblib import Memory

import persist_cache


def time_consuming_function(seed: int) -> float:
    random.seed(seed)
    return random.randint(0, 100000)

def time_function(func: Callable, iterations: int) -> float:
    """Time an instance of the time consuming function."""

    time_taken = 0
    
    for i in range(iterations):
        start = time.perf_counter()
        func(i)
        time_taken += time.perf_counter() - start
            
    return time_taken

# Initialise a `joblib.Memory` instance.
memory = Memory(".joblib", verbose=0)

# Map cachers to themselves wrapped around the time consuming function and functions to remove their caches.
cachers = {
    'persist-cache': (
        persist_cache.cache(time_consuming_function),
        lambda cache: cache.clear_cache(),
    ),

    'cachier': (
        cachier.cachier(cache_dir='.cachier')(time_consuming_function),
        lambda cache: cache.clear_cache(),
    ),
    
    'joblib': (
        memory.cache(time_consuming_function),
        lambda _: memory.clear(),
    ),
    
    'locache': (
        locache.persist(time_consuming_function),
        lambda _: ...,
    )
}

if __name__ == '__main__':
    benchmarks = []
    iterations = 5000
    
    uncached_time = time_function(time_consuming_function, iterations)/iterations
    
    for cacher, (func, emptier) in cachers.items():
        print(f'=== {cacher} ===')
        # Empty the cache.
        emptier(func)
        
        # Time how long it take to cache a function call.
        set_time = time_function(func, iterations)
        print(f'Average set time: {(set_time/iterations)-uncached_time} seconds')
        
        # Time how long it takes to retrieve a cached function call.
        get_time = time_function(func, iterations)
        print(f'Average get time: {get_time/iterations} seconds')