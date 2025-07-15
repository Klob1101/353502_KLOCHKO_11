"""
Module for Task 2: Process number sequence
Variant 11: Find the smallest number until 0 is entered
"""

def log_execution(func):
    """Decorator to log function execution"""
    def wrapper(*args, **kwargs):
        print(f"Executing {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"{func.__name__} completed. Result: {result}")
        return result
    return wrapper

@log_execution
def find_smallest_decorated():
    """Decorated version for demonstration"""
    return find_smallest()

def find_smallest():
    """
    Finds the smallest number from user input until 0 is entered
    
    Returns:
        int: smallest number or None if no numbers entered
    """
    numbers = []
    print("\nEnter integers one by one (0 to finish):")
    
    while True:
        try:
            num = int(input("> "))
            if num == 0:
                break
            numbers.append(num)
        except ValueError:
            print("Please enter integers only!")
    
    return min(numbers) if numbers else None

def run_task2():
    """Run task 2 interactively"""
    print("\n--- Task 2: Find the smallest number ---")
    print("Enter integers (0 to stop)")
    smallest = find_smallest()
    
    if smallest is not None:
        print(f"The smallest number is: {smallest}")
    else:
        print("No numbers were entered!")