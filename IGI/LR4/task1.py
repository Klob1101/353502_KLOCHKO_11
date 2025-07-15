import csv
import pickle
from abc import ABC, abstractmethod

class SynonymBase(ABC):
    """Абстрактный базовый класс для работы с синонимами"""
    def __init__(self, data=None):
        self.synonyms = data if data else {}
    
    @abstractmethod
    def save(self, filename):
        pass
    
    @abstractmethod
    def load(self, filename):
        pass
    
    def add_pair(self, word1, word2):
        self.synonyms[word1] = word2
        self.synonyms[word2] = word1
    
    def get_synonym(self, word):
        return self.synonyms.get(word, None)
    
    def get_last_synonym(self):
        if not self.synonyms:
            return None
        last_word = list(self.synonyms.keys())[-1]
        return self.synonyms[last_word]

class CSVSynonym(SynonymBase):
    """Класс для работы с синонимами через CSV файл"""
    def save(self, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['word1', 'word2'])
            saved_pairs = set()
            for word1, word2 in self.synonyms.items():
                if (word1, word2) not in saved_pairs and (word2, word1) not in saved_pairs:
                    writer.writerow([word1, word2])
                    saved_pairs.add((word1, word2))
    
    def load(self, filename):
        self.synonyms = {}
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if len(row) >= 2:
                        self.add_pair(row[0], row[1])
        except FileNotFoundError:
            print(f"Файл {filename} не найден. Будет создан новый словарь.")

class PickleSynonym(SynonymBase):
    """Класс для работы с синонимами через pickle"""
    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.synonyms, file)
    
    def load(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.synonyms = pickle.load(file)
        except (FileNotFoundError, EOFError):
            print(f"Файл {filename} не найден или поврежден. Будет создан новый словарь.")

def run_task1():
    print("\n=== Задание 1: Работа с синонимами ===")
    synonyms_data = {
        'happy': 'joyful', 'joyful': 'happy',
        'sad': 'unhappy', 'unhappy': 'sad',
        'big': 'large', 'large': 'big',
        'small': 'tiny', 'tiny': 'small'
    }
    
    csv_synonym = CSVSynonym(synonyms_data)
    pickle_synonym = PickleSynonym(synonyms_data)
    
    csv_synonym.save('synonyms.csv')
    pickle_synonym.save('synonyms.pkl')
    
    csv_synonym.load('synonyms.csv')
    pickle_synonym.load('synonyms.pkl')
    
    while True:
        print("\nМеню задания 1:")
        print("1. Найти синоним для слова")
        print("2. Показать синоним последнего слова в словаре")
        print("3. Добавить новую пару синонимов")
        print("4. Вернуться в главное меню")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            word = input("Введите слово для поиска синонима: ").strip().lower()
            synonym = csv_synonym.get_synonym(word)
            print(f"Синоним для '{word}': {synonym}" if synonym else f"Синоним для '{word}' не найден.")
        
        elif choice == '2':
            last_synonym = csv_synonym.get_last_synonym()
            if last_synonym:
                last_word = list(csv_synonym.synonyms.keys())[-1]
                print(f"Последнее слово: '{last_word}', его синоним: '{last_synonym}'")
            else:
                print("Словарь пуст.")
        
        elif choice == '3':
            word1 = input("Введите первое слово: ").strip().lower()
            word2 = input("Введите его синоним: ").strip().lower()
            if word1 and word2:
                csv_synonym.add_pair(word1, word2)
                pickle_synonym.add_pair(word1, word2)
                csv_synonym.save('synonyms.csv')
                pickle_synonym.save('synonyms.pkl')
                print(f"Добавлена пара: '{word1}' - '{word2}'")
        
        elif choice == '4':
            break
        
        else:
            print("Неверный выбор. Попробуйте снова.")