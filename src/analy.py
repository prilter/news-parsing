''' DATASET DESCRIPION '''

import json
import re
from datetime import datetime
from statistics import mean, median
from typing import List, Dict, Any, Tuple, Set
from collections import Counter

# FUNCTIONS
def count_words_in_text(text: str) -> int:
    """Подсчитывает количество слов в тексте"""
    if not isinstance(text, str) or not text:
        return 0
    words = re.findall(r'\b\w+\b', text, re.UNICODE)
    return len(words)

def get_total_records_count(news_data: List[Dict[str, Any]]) -> int:
    """
    Пункт 1: Количество записей
    """
    return len(news_data)

def get_unique_words_count(news_data: List[Dict[str, Any]], field: str = 'title') -> int:
    """
    Пункт 2: Количество уникальных слов в указанном поле (по умолчанию title)
    """
    all_words = []
    for item in news_data:
        text = item.get(field, '')
        if text:
            words = re.findall(r'\b\w+\b', text, re.UNICODE)
            all_words.extend([word.lower() for word in words])
    
    return len(set(all_words))

def get_word_count_statistics(news_data: List[Dict[str, Any]], field: str = 'title') -> Dict[str, float]:
    """
    Пункт 3: Минимальное, максимальное, среднее, медианное количество слов в записях
    """
    word_counts = [count_words_in_text(item.get(field, '')) for item in news_data]
    
    if not word_counts:
        return {
            'min': 0,
            'max': 0,
            'mean': 0.0,
            'median': 0.0
        }
    
    return {
        'min': min(word_counts),
        'max': max(word_counts),
        'mean': mean(word_counts),
        'median': median(word_counts)
    }

def get_date_range(news_data: List[Dict[str, Any]], date_field: str = 'date') -> Dict[str, str]:
    """
    Пункт 4: Диапазон дат опубликования записей
    Поддерживает формат: "Fri, 01 May 2026 12:45:34 GMT"
    """
    dates = []
    
    for item in news_data:
        date_str = item.get(date_field, '')
        if date_str:
            try:
                # Пробуем разные форматы дат
                for fmt in ["%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%d", "%d.%m.%Y"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        dates.append(date_obj)
                        break
                    except ValueError:
                        continue
            except:
                continue
    
    if not dates:
        return {
            'min_date': None,
            'max_date': None,
            'range_days': None
        }
    
    min_date = min(dates)
    max_date = max(dates)
    range_days = (max_date - min_date).days
    
    return {
        'min_date': min_date.strftime('%Y-%m-%d'),
        'max_date': max_date.strftime('%Y-%m-%d'),
        'range_days': range_days
    }

def get_missing_values_ratio(news_data: List[Dict[str, Any]], 
                            attributes: List[str] = None) -> Dict[str, float]:
    """
    Пункт 5: Доля пропусков в записях по каждому из атрибутов
    Возвращает словарь {атрибут: процент_пропусков}
    """
    if attributes is None:
        # Если атрибуты не указаны, берем все ключи из первой записи
        if news_data:
            attributes = list(news_data[0].keys())
        else:
            return {}
    
    total_records = len(news_data)
    missing_ratio = {}
    
    for attr in attributes:
        missing_count = 0
        for item in news_data:
            value = item.get(attr)
            
            # Проверяем на пропуск (None, пустая строка, пустой список)
            if value is None or value == '' or value == []:
                missing_count += 1
            # Для числовых полей проверяем отдельно
            elif isinstance(value, (int, float)) and value == 0 and attr in ['page', 'comments_count']:
                # 0 может быть валидным значением, не считаем пропуском
                pass
        
        missing_ratio[attr] = (missing_count / total_records) * 100 if total_records > 0 else 0
    
    return missing_ratio

# MAIN
text_field = 'title'
date_field = 'date'

def main(fn: str):
    print("=" * 60)
    print("Statistic")
    print("=" * 60)

    # 0. Get data
    data = []
    with open(fn, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Количество записей
    total = get_total_records_count(data)
    print(f"\n1. Количество записей: {total}")
    
    # 2. Уникальные слова
    unique_words = get_unique_words_count(data, field=text_field)
    print(f"\n2. Количество уникальных слов (в поле '{text_field}'): {unique_words}")
    
    # 3. Статистика по словам
    word_stats = get_word_count_statistics(data, field=text_field)
    print(f"\n3. Статистика количества слов (в поле '{text_field}'):")
    print(f"   - Минимальное: {word_stats['min']}")
    print(f"   - Максимальное: {word_stats['max']}")
    print(f"   - Среднее: {word_stats['mean']:.2f}")
    print(f"   - Медианное: {word_stats['median']:.2f}")
    
    # 4. Диапазон дат
    date_range = get_date_range(data, date_field=date_field)
    print(f"\n4. Диапазон дат (поле '{date_field}'):")
    if date_range['min_date']:
        print(f"   - С: {date_range['min_date']}")
        print(f"   - По: {date_range['max_date']}")
        print(f"   - Всего дней: {date_range['range_days']}")
    else:
        print("   - Нет корректных дат для анализа")
    
    # 5. Доля пропусков
    missing_ratios = get_missing_values_ratio(data)
    print(f"\n5. Доля пропусков по атрибутам:")
    for attr, ratio in missing_ratios.items():
        print(f"   - {attr:15}: {ratio:5.2f}%")
    
    print("\n" + "=" * 60)

main(input('Enter file dir: '))
