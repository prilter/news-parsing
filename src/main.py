import requests
from bs4 import BeautifulSoup
import time
import random
import json

# ═══════════════════════════════════════════════════════
TARGET          = 5001
NEWS_PER_PAGE   = 100
OUTPUT_FILENAME = "data"

# Много коротких запросов = разные выдачи Google
QUERIES = [
    # Basis
    "noticias","política","economía","deportes","tecnología",
    "salud","cultura","ciencia","educación","medio ambiente",
    "internacional","sociedad","entretenimiento","negocios","viajes",

    # Themes
    "última hora", "noticias hoy", "urgente", "exclusiva", "confirmado", # Events
    "gobierno", "presidente", "congreso", "elecciones", "ministerio", "reforma", "parlamento", "ley", "política", "diplomacia", # Power and politics
    "economía", "mercado", "bolsa", "precios", "inflación", "empresa", "empleo", "sueldo", "negocios", "finanzas", # Economy and money
    "sucesos", "policía", "justicia", "tribunal", "alerta", "seguridad", "accidente", "investigación", "denuncia", # Society
    "fútbol", "fichajes", "partido", "campeonato", "derrota", "victoria", # Sport
    "tecnología", "ciencia", "salud", "médico", "innovación", "descubrimiento", "estudio", "clima", "medio ambiente", # Science and health
    "cultura", "cine", "estreno", "concierto", "famosos", "espectáculos", # Culture
    "ayuntamiento", "alcalde", "barrio", "comunidad", "vecinos", "protesta", "manifestación", # Local
    "pronóstico", "clima", "tormenta", "medio ambiente", "sostenibilidad", "cambio climático" # Weather
    "universidad", "estudiantes", "oposiciones", "becas", "teletrabajo", "sindicato" # Education
    "detenido", "robo", "incendio", "desaparecido", "operativo", "narcotráfico", "emergencia" # Criminal
]

REGIONS = [
    ("es",     "ES", "ES:es",     "España"),
    ("es-419", "MX", "MX:es-419", "México"),
    ("es",     "US", "US:es",     "EEUU (es)"),
    ("es-419", "GT", "GT:es-419", "Guatemala"),
    ("es-419", "HN", "HN:es-419", "Honduras"),
    ("es-419", "SV", "SV:es-419", "El Salvador"),
    ("es-419", "NI", "NI:es-419", "Nicaragua"),
    ("es-419", "CR", "CR:es-419", "Costa Rica"),
    ("es-419", "PA", "PA:es-419", "Panamá"),
    ("es-419", "CU", "CU:es-419", "Cuba"),
    ("es-419", "DO", "DO:es-419", "República Dominicana"),
    ("es-419", "PR", "PR:es-419", "Puerto Rico"),
    ("es-419", "CO", "CO:es-419", "Colombia"),
    ("es-419", "VE", "VE:es-419", "Venezuela"),
    ("es-419", "PE", "PE:es-419", "Perú"),
    ("es-419", "EC", "EC:es-419", "Ecuador"),
    ("es-419", "BO", "BO:es-419", "Bolivia"),
    ("es-419", "CL", "CL:es-419", "Chile"),
    ("es-419", "AR", "AR:es-419", "Argentina"),
    ("es-419", "UY", "UY:es-419", "Uruguay"),
    ("es-419", "PY", "PY:es-419", "Paraguay"),
    ("es", "GQ", "GQ:es", "Guinea Ecuatorial")
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
]

session = requests.Session()


def getpage(query, page, region, max_retries=3):
    hl, gl, ceid, _ = region
    url = (
        f"https://news.google.com/rss/search"
        f"?q={requests.utils.quote(query)}&hl={hl}&gl={gl}&ceid={ceid}"
        f"&num={NEWS_PER_PAGE}&start={(page-1)*10}"
    )
    headers = {
        "User-Agent":      random.choice(USER_AGENTS),
        "Accept":          "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": f"{hl},{hl[:2]};q=0.9,en;q=0.8",
        "Connection":      "keep-alive",
    }

    for attempt in range(max_retries):
        try:
            r = session.get(url, headers=headers, timeout=20, allow_redirects=True)

            if r.status_code == 200:
                soup  = BeautifulSoup(r.content, "xml")
                items = soup.find_all("item")
                if not items:
                    return []

                result = []
                for item in items:
                    desc     = item.find("description")
                    desc_txt = BeautifulSoup(desc.text, "html.parser").get_text() if desc and desc.text else ""
                    result.append({
                        "title":       item.find("title").text   if item.find("title")   else "",
                        "link":        item.find("link").text    if item.find("link")    else "",
                        "date":        item.find("pubDate").text if item.find("pubDate") else "",
                        "source":      item.find("source").text  if item.find("source")  else "",
                        "description": desc_txt,
                        "query":       query,
                        "region":      region[3],
                    })
                return result

            elif r.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f" [429 – ждём {wait}с]", end="", flush=True)
                time.sleep(wait)
            else:
                time.sleep(5 * (attempt + 1))

        except requests.exceptions.ConnectionError:
            time.sleep(10 * (attempt + 1))
        except Exception:
            time.sleep(5 * (attempt + 1))

    return []


def collect():
    all_news    = []
    seen_links  = set()
    seen_titles = set()

    # Перемешиваем комбинации чтобы не долбить один регион подряд
    combos = [(q, r) for q in QUERIES for r in REGIONS]
    random.shuffle(combos)

    print(f"Target: {TARGET}\n")

    for i, (query, region) in enumerate(combos):
        if len(all_news) >= TARGET:
            break

        done = False
        page = 1

        while not done and len(all_news) < TARGET:
            batch = getpage(query, page, region)

            if not batch:
                break

            for news in batch:
                link  = news["link"].strip()
                title = news["title"].strip().lower()

                if link in seen_links or title in seen_titles:
                    done = True   # первый дубль — уходим
                    break

                seen_links.add(link)
                seen_titles.add(title)
                all_news.append(news)

                if len(all_news) >= TARGET:
                    done = True
                    break

            page += 1
            rdelay(1.5, 2.7)

        # прогресс-строка
        bar_done = int(len(all_news) / TARGET * 100)
        bar(bar_done, 30)

    print() 
    return all_news

def bar(proc, size):
    bar = "█" * int(proc*size/100) + "░" * int((100 - proc)*size/100)
    print(f"\r[{bar}] {proc}%  ", end="", flush=True)

def rdelay(a, b):
    time.sleep(random.uniform(a, b))
    
def superprint(s, n=50):
    print("=" * n)
    print(f"{s:^{n}}")
    print("=" * n)

def main():
    superprint('ПАРСЕР GOOGLE NEWS')

    news = collect()
    print(f"\n✅ Collected uniques: {len(news)}")

    with open(f"{OUTPUT_FILENAME}{TARGET}.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    print(f"💾 {OUTPUT_FILENAME}.json")

main()
