"""
Module for Task 1: Calculate ln(1+x) using Taylor series
Variant 11
"""

import math

def generator(x) :
    n = 1
    while True:
        yield ((-1)**(n-1)) * (x**n) / n
        n += 1

def calculate_series(x, eps=1e-6):
    """
    Calculate ln(1+x) using Taylor series expansion.
    
    Args:
        x (float): Input value (-1 < x < 1)
        eps (float): Calculation precision
    
    Returns:
        tuple: (result, terms, math_value)
    """

    gen = generator(x)

    if abs(x) >= 1:
        raise ValueError("x must be in (-1, 1)")
    
    result = 0.0
    term = x
    n = 1
    max_iter = 500
    
    while abs(term) > eps and n <= max_iter:
        result += term
        n += 1
        term = next(gen)
    
    return result, n-1, math.log(1+x)

def run_task1():
    """Run task 1 interactively"""
    print("\n--- Task 1: Calculate ln(1+x) using Taylor series ---")
    try:
        x = float(input("Enter x (-1 < x < 1): "))
        res, terms, math_val = calculate_series(x)
        print(f"Result: {res:.6f}")
        print(f"Terms needed: {terms}")
        print(f"Math library value: {math_val:.6f}")
        print(f"Difference: {abs(res - math_val):.2e}")
    except ValueError as e:
        print(f"Error: {e}")