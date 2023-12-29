from functools import wraps
from time import perf_counter
from typing import Callable, Any

type Test_Function_Result = Any

def benchmark_time(title: str, iterations: int) -> Callable:
    """
    This function defines a decorator that is intended for benchmarking crucial functions related to attack detection. 
    As of today, the benchmark tests have been executed on an Intel i5 10th gen processor.
    """
    def decorator(bench_func: Callable):
        @wraps(bench_func)
        def wrapper(*args, **kwargs) -> Test_Function_Result:
            print("-----------------------------------")
            print(f"Performence benchmark: {title}")
            
            total_ms = 0
            total_secs = 0
            
            for _ in range(iterations):
                start = perf_counter()
                _ = bench_func(*args, **kwargs)
                end = perf_counter()
                
                total_secs += end - start
                total_ms += int(round(total_secs * 1_000))
            
            print(f"Ran {iterations} iterations in {total_secs:.5}s") 
            print(f"Avg time for one iteration on {bench_func.__name__} - {total_ms // iterations}ms") 
            
        return wrapper
    return decorator