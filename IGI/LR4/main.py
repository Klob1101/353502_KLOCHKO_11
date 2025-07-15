def main_menu():
    while True:
        print("\nГлавное меню:")
        print("1. Задание 1 - Работа с синонимами (CSV и pickle)")
        print("2. Задание 2 - Анализ текста (регулярные выражения)")
        print("3. Задание 3 - Анализ функции sin(x) (ряд Тейлора)")
        print("4. Задание 4 - Квадрат с треугольником (геометрические фигуры)")
        print("5. Задание 5 - Анализ матрицы (NumPy)")
        print("6. Выход")
        
        choice = input("Выберите задание (1-6): ")
        
        if choice == '1':
            from task1 import run_task1
            run_task1()
        elif choice == '2':
            from task2 import run_task2
            run_task2()
        elif choice == '3':
            from task3 import run_task3
            run_task3()
        elif choice == '4':
            from task4 import run_task4
            run_task4()
        elif choice == '5':
            from task5 import run_task5
            run_task5()
        elif choice == '6':
            print("Завершение программы.")
            break
        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 6.")

if __name__ == "__main__":
    show_header()
    main_menu()