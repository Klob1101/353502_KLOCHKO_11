import math
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean, median, mode, variance, stdev

class FunctionAnalyzer:
    """Класс для анализа функции sin(x) (задание 3, вариант 11)"""
    
    def __init__(self, x_values, n_terms=10):
        self.x_values = x_values
        self.n_terms = n_terms
        self.series_results = []
        self.math_results = []
        self.calculate_series()
    
    def calculate_term(self, x, n):
        return ((-1)**(n+1)) * (x**(2*n-1)) / math.factorial(2*n-1)
    
    def calculate_series(self):
        self.series_results = []
        for x in self.x_values:
            series_sum = sum(self.calculate_term(x, n) for n in range(1, self.n_terms+1))
            self.series_results.append(series_sum)
        self.math_results = [math.sin(x) for x in self.x_values]
    
    def calculate_statistics(self):
        data = self.series_results
        return {
            'mean': mean(data),
            'median': median(data),
            'mode': mode(data) if len(data) == len(set(data)) else 'No unique mode',
            'variance': variance(data) if len(data) > 1 else 0,
            'stdev': stdev(data) if len(data) > 1 else 0
        }
    
    def plot_functions(self, filename='function_plot.png'):
        plt.figure(figsize=(10, 6))
        plt.plot(self.x_values, self.series_results, 
                label=f'Ряд Тейлора ({self.n_terms} членов)', 
                color='blue', linestyle='--')
        plt.plot(self.x_values, self.math_results, 
                label='math.sin', 
                color='red', linestyle='-')
        plt.title('Приближение sin(x) рядом Тейлора')
        plt.xlabel('x')
        plt.ylabel('F(x)')
        plt.grid(True)
        plt.legend()
        plt.annotate(
            r'$F(x) = \sum_{n=1}^{\infty} \frac{(-1)^{n+1} x^{2n-1}}{(2n-1)!}$',
            xy=(0.5, -0.15), xycoords='axes fraction',
            ha='center', va='center', fontsize=12
        )
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        print(f"График сохранен в {filename}")

def run_task3():
    print("\n=== Задание 3: Анализ функции sin(x) ===")
    x_values = np.linspace(0, 2*math.pi, 20).tolist()
    n_terms = int(input("Введите количество членов ряда (по умолчанию 10): ") or 10)
    
    analyzer = FunctionAnalyzer(x_values, n_terms)
    stats = analyzer.calculate_statistics()
    
    print("\nСтатистика приближения:")
    for param, value in stats.items():
        print(f"{param:>10}: {value:.6f}")
    
    analyzer.plot_functions()
    
    # Анализ погрешности
    errors = [abs(s - m) for s, m in zip(analyzer.series_results, analyzer.math_results)]
    print(f"\nМаксимальная погрешность: {max(errors):.6f}")
    print(f"Средняя погрешность: {mean(errors):.6f}")
    
    plt.figure(figsize=(10, 4))
    plt.plot(x_values, errors, label='Погрешность', color='green')
    plt.title('Погрешность приближения')
    plt.xlabel('x')
    plt.ylabel('Абсолютная погрешность')
    plt.grid(True)
    plt.legend()
    plt.savefig('error_plot.png', bbox_inches='tight')
    plt.close()
    print("График погрешности сохранен в error_plot.png")