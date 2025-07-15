import matplotlib.pyplot as plt
import math
from abc import ABC, abstractmethod

class Color:
    """Класс для представления цвета фигуры"""
    def __init__(self, color_name):
        self.color_name = color_name
    
    @property
    def color(self):
        return self.color_name
    
    def __str__(self):
        return self.color_name

class Shape(ABC):
    """Абстрактный базовый класс геометрической фигуры"""
    def __init__(self, color):
        self.color = Color(color)
    
    @abstractmethod
    def area(self):
        """Абстрактный метод для вычисления площади"""
        pass
    
    @abstractmethod
    def draw(self):
        """Абстрактный метод для отрисовки фигуры"""
        pass
    
    @abstractmethod
    def get_params(self):
        """Абстрактный метод для получения параметров"""
        pass
    
    @property
    @abstractmethod
    def name(self):
        """Абстрактное свойство - название фигуры"""
        pass

class SquareWithTriangle(Shape):
    """Класс для квадрата с треугольником на стороне (вариант 11)"""
    
    @property
    def name(self):
        return "Квадрат с равносторонним треугольником"
    
    def __init__(self, side_length, color="blue"):
        super().__init__(color)
        self.side_length = side_length
    
    def area(self):
        """Вычисление общей площади фигуры"""
        square_area = self.side_length ** 2
        triangle_area = (math.sqrt(3) / 4) * self.side_length ** 2
        return square_area + triangle_area
    
    def get_params(self):
        """Возвращает параметры фигуры в виде строки"""
        return (
            f"{self.name}\n"
            f"Цвет: {self.color}\n"
            f"Длина стороны: {self.side_length:.2f}\n"
            f"Общая площадь: {self.area():.2f}"
        )
    
    def draw(self, filename=None):
        """Отрисовка фигуры с помощью matplotlib"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Координаты квадрата
        square_x = [0, self.side_length, self.side_length, 0, 0]
        square_y = [0, 0, self.side_length, self.side_length, 0]
        
        # Координаты треугольника
        triangle_height = (math.sqrt(3) / 2) * self.side_length
        triangle_x = [0, self.side_length / 2, self.side_length, 0]
        triangle_y = [self.side_length, 
                     self.side_length + triangle_height, 
                     self.side_length, 
                     self.side_length]
        
        # Отрисовка квадрата
        ax.fill(square_x, square_y, color=self.color.color, alpha=0.5)
        ax.plot(square_x, square_y, color='black')
        
        # Отрисовка треугольника
        ax.fill(triangle_x, triangle_y, color=self.color.color, alpha=0.5)
        ax.plot(triangle_x, triangle_y, color='black')
        
        # Настройки графика
        ax.set_aspect('equal')
        ax.set_title(self.name)
        ax.grid(True)
        
        # Добавление текста с параметрами
        params_text = (
            f"Длина стороны: {self.side_length:.2f}\n"
            f"Площадь квадрата: {self.side_length**2:.2f}\n"
            f"Площадь треугольника: {(math.sqrt(3)/4)*self.side_length**2:.2f}\n"
            f"Общая площадь: {self.area():.2f}\n"
            f"Цвет: {self.color}"
        )
        ax.text(self.side_length * 1.1, self.side_length / 2, 
                params_text, bbox=dict(facecolor='white', alpha=0.8))
        
        if filename:
            plt.savefig(filename, bbox_inches='tight')
            print(f"Рисунок сохранен в файл: {filename}")
        else:
            plt.show()
        
        plt.close()

def input_float(prompt, min_val=0.1):
    """Безопасный ввод числа с плавающей точкой"""
    while True:
        try:
            value = float(input(prompt))
            if value >= min_val:
                return value
            print(f"Значение должно быть больше или равно {min_val}")
        except ValueError:
            print("Пожалуйста, введите число")

def run_task4():
    print("\n=== Задание 4: Квадрат с треугольником ===")
    print("Построение квадрата с равносторонним треугольником на стороне\n")
    
    # Ввод параметров
    side = input_float("Введите длину стороны (a > 0): ")
    color = input("Введите цвет фигуры (например, red, blue, green): ") or "blue"
    filename = input("Введите имя файла для сохранения (оставьте пустым для показа): ") or None
    
    # Создание и отрисовка фигуры
    figure = SquareWithTriangle(side, color)
    print("\n" + figure.get_params())
    figure.draw(filename)