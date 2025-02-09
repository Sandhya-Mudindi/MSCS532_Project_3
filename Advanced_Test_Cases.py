import time
import random
import string
import sys
from memory_profiler import memory_usage
from FM_Index import FMIndex as SuffixArray  # Ensure this matches your implementation

def generate_random_string(length):
    """Generates a random string of given length."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def run_test(test_name, text, expected_output=None, log_memory=True):
    """Runs a single test case and logs execution time and memory usage."""
    print(f"\n[Test: {test_name}]")
    
    if not text:  # Check for empty input
        print("Skipping test: Input text is empty (not allowed).")
        return
    
    start_time = time.time()
    
    # Memory profiling must be wrapped in a function
    def profile_func():
        return SuffixArray(text)
    
    mem_usage = memory_usage(profile_func, max_usage=True) if log_memory else None
    
    sa = profile_func()
    suffix_array = sa.suffix_array
    
    execution_time = time.time() - start_time

    if expected_output is not None:
        assert suffix_array == expected_output, f"Test Failed: Expected {expected_output}, Got {suffix_array}"
    
    print(f"Execution Time: {execution_time:.5f} seconds")
    if log_memory:
        print(f"Memory Usage: {mem_usage:.2f} MB")
    print(f"Suffix Array Size: {len(suffix_array)}")

if __name__ == '__main__':
    # Functional Tests
    run_test("Basic Test (banana)", "banana", expected_output=[6, 5, 3, 1, 0, 4, 2])
    run_test("Repetitive Characters (aaaaa)", "aaaaa", expected_output=[5, 4, 3, 2, 1, 0])
    run_test("Unicode Support", "你好世界")  # Unicode check

    # Edge Case Tests
    run_test("Empty String", "")
    run_test("Single Character", "a", expected_output=[1, 0])
    run_test("Large Repetitive String", "a" * 10000)

    # Stress Test
    run_test("100 Thousand Characters", generate_random_string(100000))

    print("\nAll tests completed successfully!")
