"""
Module for Task 3: Text analysis
Variant 11: Count uppercase English vowels in input string
"""

def log_vowel_count(func):
    """Decorator to log vowel counting"""
    def wrapper(text):
        print(f"Analyzing string: '{text[:20]}...'")
        result = func(text)
        print(f"Found {result} uppercase vowels")
        return result
    return wrapper

@log_vowel_count
def count_uppercase_vowels_decorated(text):
    """Decorated version for demonstration"""
    return count_uppercase_vowels(text)

def count_uppercase_vowels(text):
    """
    Counts uppercase vowels (A, E, I, O, U) in a string
    
    Args:
        text (str): Input string to analyze
    
    Returns:
        int: Number of uppercase vowels
    """
    vowels = {'A', 'E', 'I', 'O', 'U'}
    return sum(1 for char in text if char in vowels)

def run_task3():
    """Run task 3 interactively"""
    print("\n--- Task 3: Count uppercase vowels ---")
    text = input("Enter a string: ")
    count = count_uppercase_vowels(text)
    print(f"Number of uppercase vowels: {count}")