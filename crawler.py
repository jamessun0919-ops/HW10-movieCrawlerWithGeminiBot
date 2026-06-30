import requests
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://ssr1.scrape.center"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore

OUTPUT_FILE = "movies.json"

session = requests.Session()
session.headers.update(HEADERS)


def safe_get(url):
    try:
        resp = session.get(url, timeout=15, verify=False)
        resp.encoding = "utf-8"
        if resp.status_code == 200:
            return resp
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
    return None


def parse_list_page(html):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(".el-card.item")
    movies = []
    for card in cards:
        link = card.select_one("a[href^='/detail/']")
        if not link:
            continue
        href = link.get("href", "")
        movie_id = href.split("/")[-1] if href else None
        name_el = card.select_one(".name h2")
        name = name_el.get_text(strip=True) if name_el else ""
        score_el = card.select_one(".score")
        score = score_el.get_text(strip=True) if score_el else ""
        cover_el = card.select_one(".cover")
        cover = cover_el.get("src", "") if cover_el else ""
        categories = [
            btn.get_text(strip=True)
            for btn in card.select(".category span")
        ]
        info_spans = card.select(".info span")
        region = info_spans[0].get_text(strip=True) if len(info_spans) > 0 else ""
        duration = info_spans[2].get_text(strip=True) if len(info_spans) > 2 else ""
        release = ""
        for el in card.select(".info"):
            text = el.get_text(strip=True)
            if "上映" in text:
                release = text
        movies.append({
            "id": int(movie_id) if movie_id and movie_id.isdigit() else None,
            "name": name,
            "score": score,
            "cover": cover,
            "categories": categories,
            "region": region,
            "duration": duration,
            "release": release,
        })
    return movies


def parse_detail_page(html, movie_data):
    soup = BeautifulSoup(html, "html.parser")
    drama_el = soup.select_one(".drama p")
    movie_data["drama"] = drama_el.get_text(strip=True) if drama_el else ""
    directors = []
    for d in soup.select(".directors .director"):
        name_el = d.select_one(".name")
        if name_el:
            directors.append(name_el.get_text(strip=True))
    movie_data["directors"] = directors
    actors = []
    for a in soup.select(".actors .actor"):
        name_el = a.select_one(".name")
        role_el = a.select_one(".role")
        if name_el:
            actors.append({
                "name": name_el.get_text(strip=True),
                "role": role_el.get_text(strip=True) if role_el else "",
            })
    movie_data["actors"] = actors
    photos = []
    for p in soup.select(".photos .photo img"):
        src = p.get("src", "")
        if src:
            photos.append(src)
    movie_data["photos"] = photos
    return movie_data


def crawl_all():
    all_movies = []
    page = 1
    while True:
        url = f"{BASE_URL}/page/{page}"
        print(f"[CRAWL] List page {page}...")
        resp = safe_get(url)
        if not resp:
            break
        movies = parse_list_page(resp.text)
        if not movies:
            print("[DONE] No more movies.")
            break
        for m in movies:
            detail_url = f"{BASE_URL}/detail/{m['id']}"
            print(f"  [DETAIL] {m['id']} - {m['name']}")
            detail_resp = safe_get(detail_url)
            if detail_resp:
                parse_detail_page(detail_resp.text, m)
            all_movies.append(m)
        page += 1
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)
    print(f"\n[SAVED] {len(all_movies)} movies to {OUTPUT_FILE}")


if __name__ == "__main__":
    crawl_all()
