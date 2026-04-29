# PARSING SPEED FOR 5000 NEWS - 30 min

import requests
from bs4 import BeautifulSoup
import time
import random

query = 'a'
lang  = "es"
pages = 2
pagedeep = 10

def get_news_page(page, news_per_page, max_retries=3):
    """Получение одной страницы с новостями"""
    url = f"https://news.google.com/rss/search?q={query}&hl={lang}&num={news_per_page}&start={(page-1)*10}"
    
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': f'{lang}-{lang.upper()},{lang};q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                
                news_list = []
                for item in items:
                    # Очистка описания от HTML
                    description = item.find('description')
                    if description and description.text:
                        desc_text = BeautifulSoup(description.text, 'html.parser').get_text()
                    else:
                        desc_text = ''
                    
                    news_list.append({
                        'title': item.find('title').text if item.find('title') else '',
                        'link': item.find('link').text if item.find('link') else '',
                        'date': item.find('pubDate').text if item.find('pubDate') else '',
                        'source': item.find('source').text if item.find('source') else '',
                        'description': desc_text,
                        'page': page
                    })
                
                return news_list
            else:
                print(f"  ⚠️ Страница {page}: статус {response.status_code}, попытка {attempt+1}/{max_retries}")
                time.sleep(5 * (attempt + 1))
                
        except Exception as e:
            print(f"  ❌ Страница {page}: ошибка {str(e)[:50]}, попытка {attempt+1}/{max_retries}")
            time.sleep(5 * (attempt + 1))
    
    return []

def collect_news(pages=10, news_per_page=10):
    """Сбор новостей до достижения целевого количества"""
    total_target = pages * news_per_page

    all_news = []
    page = 1
    max_pages = (total_target // news_per_page) + 10  # Запас 10 страниц
    
    print(f"🎯 Цель: собрать {total_target} новостей")
    print(f"📄 Страниц потребуется: {pages}")
    print("-" * 50)
    
    while len(all_news) < total_target and page <= max_pages:
        print(f"📥 Страница {page} (собрано: {len(all_news)}/{total_target})...", end=" ")
        
        news_batch = get_news_page(page, news_per_page)
        
        if news_batch:
            all_news.extend(news_batch)
            print(f"✅ +{len(news_batch)} новостей")
            rdelay(3,4)
        else:
            print(f"❌ Пусто или ошибка")
            rdelay(9, 11) # increase delay
        
        page += 1
        
        # EACH 10 PAGES SHOW PROGRESS
        if page % 10 == 0:
            print(f"📊 Прогресс: {len(all_news)}/{total_target} новостей, страниц: {page}")
    
    return all_news[:total_target]

def rdelay(a, b):
    time.sleep(random.uniform(a, b))

def superprint(s):
    print("=" * 50)
    print(s)
    print("=" * 50)

def json_save(data, fn="data"):
    with open(f"{fn}.json", 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"💾 Saved to {fn}.json")

def outnews(data, newslen):
    print(f"\n📰 First {newslen} news:")
    print("-" * 50)
    for i, news in enumerate(data[:total_news], 1):
        print(f"{i}. {news['title'][:newslen]}")
        print(f"   Source: {news['source']}\n")

output_filename = "data5000"

import json
def main():
    superprint("🚀 Начинаем сбор новостей...")
    news_data = collect_news(pages, pagedeep)
    superprint(f"✅ Собрано новостей: {len(news_data)}")

    if news_data:
        json_save(news_data, output_filename)
        outnews(news_data, pages * pagedeep)
    else:
        print("❌ Не удалось собрать новости. Проверьте соединение или измените headers.")

main()
