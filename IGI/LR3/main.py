"""
Main module for Lab Work 3
Klochko Aleksandr
353502
Variant 11
"""
from task1 import run_task1
from task2 import run_task2
from task3 import run_task3
from task4 import run_task4
from task5 import run_task5

def main():
    while True:
        print("\n=== Lab Work 3 (Variant 11) ===")
        print("1. Calculate ln(1+x) (Taylor series)")
        print("2. Find the smallest number")
        print("3. Count uppercase English vowels in input string")
        print("4. Analyze text")
        print("5. Process number list")
        print("0. Exit")
        
        choice = input("Select task: ").strip()
        
        if choice == '0':
            print("Goodbye!")
            break
        elif choice == '1':
            run_task1()
        elif choice == '2':
            run_task2()
        elif choice == '3':
            run_task3()
        elif choice == '4':
            run_task4()
        elif choice == '5':
            run_task5()
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()