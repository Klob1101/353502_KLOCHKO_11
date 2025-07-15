"""
Module for Task 5: Process real number list
Variant 11 requirements:
a) Count elements in range [A, B]
b) Sum elements after max element
"""

def input_list():
    """Input list of numbers with validation"""
    numbers = []
    print("\nEnter numbers one by one (empty to finish):")
    
    while True:
        inp = input("> ").strip()
        if not inp:
            break
        try:
            num = float(inp)
            numbers.append(num)
        except ValueError:
            print("Please enter valid numbers!")
    
    return numbers

def process_list(numbers):
    """Process list according to variant 11"""
    if not numbers:
        return None
    
    while True:
        try:
            a = float(input("Enter range start (A): "))
            b = float(input("Enter range end (B): "))
            if a > b:
                print("A must be <= B!")
                continue
            break
        except ValueError:
            print("Please enter valid numbers!")
    
    in_range = sum(1 for num in numbers if a <= num <= b)
    
    max_idx = numbers.index(max(numbers))
    sum_after = sum(numbers[max_idx+1:])
    
    return {
        'numbers': numbers,
        'in_range': in_range,
        'sum_after_max': sum_after
    }

def run_task5():
    """Run task 5 interactively"""
    print("\n--- Task 5: Process number list ---")
    numbers = input_list()
    if not numbers:
        print("Empty list!")
        return
    
    result = process_list(numbers)
    print("\nResults:")
    print(f"List: {result['numbers']}")
    print(f"a) Count of numbers in range: {result['in_range']}")
    print(f"b) Sum after max element: {result['sum_after_max']}")