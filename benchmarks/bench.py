import os
import sys
from benchmark_dec import benchmark_time

parent = "./.."
module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
sys.path.append(module)

if __name__ == '__main__':
    """
    Benchmarks to be done for crucial functions such as check_sqli, check_xss etc..  
    """
    pass
