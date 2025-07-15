import re
import zipfile
from collections import Counter
import matplotlib.pyplot as plt

class TextAnalyzer:
    """Класс для анализа текста (задание 2, вариант 11)"""
    
    def __init__(self, text):
        self.text = text
        self.sentences = self._split_sentences()
        self.words = self._extract_words()
        self.smiley_pattern = re.compile(r"[:;]-*[\(\)\[\]]+")
    
    def _split_sentences(self):
        sentences = re.split(r'(?<=[.!?])\s+', self.text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_words(self):
        words = re.findall(r'\b[\w-]+\b', self.text.lower())
        return [word for word in words if word]
    
    def count_sentences(self):
        return len(self.sentences)
    
    def count_sentence_types(self):
        counts = {'declarative': 0, 'interrogative': 0, 'imperative': 0}
        for sentence in self.sentences:
            if sentence.endswith('.'):
                counts['declarative'] += 1
            elif sentence.endswith('?'):
                counts['interrogative'] += 1
            elif sentence.endswith('!'):
                counts['imperative'] += 1
        return counts
    
    def avg_sentence_length(self):
        if not self.sentences: return 0
        total_words = sum(len(re.findall(r'\b\w+\b', s)) for s in self.sentences)
        return total_words / len(self.sentences)
    
    def avg_word_length(self):
        if not self.words: return 0
        return sum(len(word) for word in self.words) / len(self.words)
    
    def count_smileys(self):
        return len(self.smiley_pattern.findall(self.text))
    
    # Методы для 11 варианта
    def words_with_alpha_and_digits(self):
        pattern = re.compile(r'\b(?=\w*[a-o])(?=\w*\d)\w+\b', re.IGNORECASE)
        return pattern.findall(self.text)
    
    def count_quoted_words(self):
        return len(re.findall(r'["\'](\w+)["\']', self.text))
    
    def letter_frequency(self):
        return Counter(char.lower() for char in self.text if char.isalpha())
    
    def comma_separated_phrases(self):
        phrases = []
        matches = re.finditer(r'(\b\w+\b)(?:\s*,\s*(\b\w+\b))+', self.text)
        for match in matches:
            phrase = match.group().split(',')
            phrases.extend([p.strip() for p in phrase if p.strip()])
        return sorted(set(phrases))
    
    def analyze_and_save(self, filename):
        results = {
            "Общее количество предложений": self.count_sentences(),
            "Типы предложений": self.count_sentence_types(),
            "Средняя длина предложения": round(self.avg_sentence_length(), 2),
            "Средняя длина слова": round(self.avg_word_length(), 2),
            "Количество смайликов": self.count_smileys(),
            "Слова с a-o и цифрами": self.words_with_alpha_and_digits(),
            "Слова в кавычках": self.count_quoted_words(),
            "Частота букв": dict(self.letter_frequency()),
            "Словосочетания через запятую": self.comma_separated_phrases()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            for key, value in results.items():
                if isinstance(value, dict):
                    f.write(f"{key}:\n")
                    for k, v in value.items():
                        f.write(f"  {k}: {v}\n")
                else:
                    f.write(f"{key}: {value}\n")
        
        with zipfile.ZipFile(f'{filename}.zip', 'w') as zipf:
            zipf.write(filename)
        
        return results

def run_task2():
    print("\n=== Задание 2: Анализ текста ===")
    sample_text = """
    Example text with 4 sentences. Two declarative, one interrogative? And one imperative!
    Words with a-o and digits: a1, b2, c3, but not x5. "Quoted" words appear here.
    Comma-separated: apple, banana, cherry, apple. Smileys: :) ;-( :)))
    """
    
    analyzer = TextAnalyzer(sample_text)
    results = analyzer.analyze_and_save('text_analysis.txt')
    
    print("\nРезультаты анализа:")
    for key, value in results.items():
        if key == "Частота букв":
            print(f"{key}:")
            for letter, count in sorted(value.items()):
                print(f"  {letter}: {count}")
        elif isinstance(value, list):
            print(f"{key}: {', '.join(value)}")
        elif isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
    
    # Визуализация частоты букв
    letters = analyzer.letter_frequency()
    plt.bar(letters.keys(), letters.values())
    plt.title('Частота букв в тексте')
    plt.xlabel('Буквы')
    plt.ylabel('Количество')
    plt.savefig('letter_frequency.png')
    plt.close()
    print("\nГрафик частоты букв сохранен в letter_frequency.png")