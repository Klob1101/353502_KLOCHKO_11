import numpy as np
from statistics import median

class MatrixAnalyzer:
    """Класс для анализа матриц по заданию 5 (вариант 11)"""
    
    def __init__(self, rows=5, cols=5, min_val=-100, max_val=100):
        """Инициализация матрицы случайными значениями"""
        self.rows = rows
        self.cols = cols
        self.matrix = np.random.randint(min_val, max_val, (rows, cols))
        self.threshold = None
        self.filtered_elements = None
    
    def set_matrix(self, matrix):
        """Установка пользовательской матрицы"""
        self.matrix = np.array(matrix)
        self.rows, self.cols = self.matrix.shape
    
    def find_elements_above_threshold(self, B):
        """Поиск элементов, превышающих по модулю заданное число B"""
        self.threshold = abs(B)
        self.filtered_elements = self.matrix[np.abs(self.matrix) > self.threshold]
        return self.filtered_elements
    
    def count_elements_above_threshold(self):
        """Подсчет количества элементов, превышающих порог"""
        return len(self.filtered_elements) if self.filtered_elements is not None else 0
    
    def calculate_median(self):
        """Вычисление медианы двумя способами"""
        if self.filtered_elements is None or len(self.filtered_elements) == 0:
            return None, None
        
        # Способ 1: Использование стандартной функции
        median_std = median(self.filtered_elements)
        
        # Способ 2: Ручной расчет
        sorted_elements = np.sort(self.filtered_elements)
        n = len(sorted_elements)
        
        if n % 2 == 1:
            median_manual = sorted_elements[n // 2]
        else:
            median_manual = (sorted_elements[n // 2 - 1] + sorted_elements[n // 2]) / 2
        
        return median_std, median_manual
    
    def display_matrix(self):
        """Вывод матрицы на экран"""
        print("\nМатрица:")
        for row in self.matrix:
            print(" ".join(f"{elem:5}" for elem in row))
    
    def display_results(self):
        """Вывод результатов анализа"""
        if self.filtered_elements is None:
            print("Сначала выполните поиск элементов с find_elements_above_threshold(B)")
            return
        
        print(f"\nЧисло B (по модулю): {self.threshold}")
        print(f"Количество элементов > |B|: {self.count_elements_above_threshold()}")
        print(f"Элементы, превышающие |B|: {self.filtered_elements}")
        
        median_std, median_manual = self.calculate_median()
        print(f"\nМедиана (стандартная функция): {median_std:.2f}")
        print(f"Медиана (ручной расчет): {median_manual:.2f}")

def input_int(prompt, min_val=1):
    """Безопасный ввод целого числа"""
    while True:
        try:
            value = int(input(prompt))
            if value >= min_val:
                return value
            print(f"Значение должно быть не меньше {min_val}")
        except ValueError:
            print("Пожалуйста, введите целое число")

def input_float(prompt):
    """Безопасный ввод числа с плавающей точкой"""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Пожалуйста, введите число")

def run_task5():
    print("\n=== Задание 5: Анализ матрицы ===")
    print("Поиск элементов матрицы, превышающих по модулю заданное число B\n")
    
    # Настройка матрицы
    rows = input_int("Введите количество строк матрицы (>=1): ", 1)
    cols = input_int("Введите количество столбцов матрицы (>=1): ", 1)
    min_val = input_int("Минимальное значение элементов: ")
    max_val = input_int("Максимальное значение элементов: ")
    
    analyzer = MatrixAnalyzer(rows, cols, min_val, max_val)
    analyzer.display_matrix()
    
    # Поиск элементов
    B = input_float("Введите число B: ")
    filtered = analyzer.find_elements_above_threshold(B)
    
    # Вывод результатов
    analyzer.display_results()
    
    # Дополнительная информация
    print("\nДополнительная информация:")
    print(f"Размер матрицы: {rows}x{cols}")
    print(f"Диапазон значений: [{min_val}, {max_val}]")
    print(f"Всего элементов: {rows * cols}")
    
    # Сохранение результатов в файл
    save_to_file = input("\nСохранить результаты в файл? (y/n): ").lower()
    if save_to_file == 'y':
        filename = input("Введите имя файла (без расширения): ") + ".txt"
        with open(filename, 'w') as f:
            f.write("Результаты анализа матрицы\n")
            f.write("="*30 + "\n")
            f.write(f"Размер матрицы: {rows}x{cols}\n")
            f.write(f"Число B (по модулю): {analyzer.threshold}\n")
            f.write(f"Количество элементов > |B|: {analyzer.count_elements_above_threshold()}\n")
            f.write(f"Элементы: {analyzer.filtered_elements}\n")
            median_std, median_manual = analyzer.calculate_median()
            f.write(f"Медиана (стандартная): {median_std:.2f}\n")
            f.write(f"Медиана (ручная): {median_manual:.2f}\n")
        print(f"Результаты сохранены в файл: {filename}")

def main():
    run_task5()

if __name__ == "__main__":
    main()