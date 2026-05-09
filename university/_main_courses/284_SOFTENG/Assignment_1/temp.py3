import bisect  # Import bisect module for efficient binary search operations

# Read the number of elements in the array
n = int(input())  # For example: 10

# Read the array elements and convert them to a list of integers
# Example input: 1 5 5 5 6 10 25 25 101 101
A = list(map(int, input().split()))

# Read the number of queries
m = int(input())  # For example: 5

# Read m queries, each containing two integers (low, high), and store them as tuples
queries = [tuple(map(int, input().split())) for _ in range(m)]

# For each query, count how many elements in A are within the inclusive range [low, high]
for low, high in queries:
    # Index of the first element >= low
    left_index = bisect.bisect_left(A, low)

    # Index of the first element > high
    right_index = bisect.bisect_right(A, high)

    # Number of elements in the range [low, high] is (right_index - left_index)
    print(right_index - left_index)
