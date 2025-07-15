"""
Module for Task 4: Text analysis
Variant 11 requirements:
a) Count words
b) Find longest word and its position
c) Print every odd word
"""

from text import TEXT

def analyze_text():
    """Analyze text according to variant 11 requirements"""
    words = []
    for word in TEXT.replace(',', ' ').replace('.', ' ').split():
        if word:
            words.append(word.lower())
    
    word_count = len(words)
    
    longest = max(words, key=len)
    longest_pos = words.index(longest) + 1
    
    odd_words = words[::2]
    
    return {
        'word_count': word_count,
        'longest': (longest, longest_pos),
        'odd_words': odd_words
    }

def run_task4():
    """Run task 4 interactively"""
    print("\n--- Task 4: Text analysis ---")
    analysis = analyze_text()
    
    print(f"a) Total words: {analysis['word_count']}")
    
    word, pos = analysis['longest']
    print(f"b) Longest word: '{word}' (position {pos})")
    
    print("c) Every odd word:")
    for i, word in enumerate(analysis['odd_words'], 1):
        print(f"{i}. {word}")