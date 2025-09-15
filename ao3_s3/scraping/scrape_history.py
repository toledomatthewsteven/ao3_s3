# scraping/scrape_history.py
from bs4 import BeautifulSoup
import time, re

import re

def extract_year(view_text):
    match = re.search(r"\b(20\d{2}|19\d{2})\b", view_text)  # finds 1990–2099
    return int(match.group(0)) if match else None


def scrape_history(session, username, start_year=None, end_year=None, progress_callback=None):
    """
    session: requests.Session (NOT a Playwright page)
    username: AO3 username
    progress_callback: optional function(current_count:int, title:str)
    """
    # Sanity check: bail early if caller accidentally passed a Playwright page
    if hasattr(session, "goto"):
        raise TypeError("scrape_history expects a requests.Session (returned by ao3_login). You passed a Playwright page. Use the Playwright-specific scraper or pass a requests.Session.")

    base_url = f"https://archiveofourown.org/users/{username}/readings"
    titles, authors, ships, characters, ratings, fandoms, tags, words = [], [], [], [], [], [], [], []

    p = 1
    isDone = False
    fic_count = 0

    while not isDone:
        url = f"{base_url}?page={p}" if p > 1 else base_url
        r = session.get(url)
        if r.status_code != 200:
            # failed page load — stop gracefully
            break

        soup = BeautifulSoup(r.text, "html.parser")

        fics = soup.findAll('div', class_="header module")
        extras = soup.findAll('ul', class_="tags commas")
        stats = soup.findAll('dl', class_="stats")
        views = soup.findAll('h4', class_="viewed heading")

        if not fics:
            break

        for i in range(len(fics)):
            view_text = views[i].text if i < len(views) else ""
            year = extract_year(view_text)

            if year and start_year and year < start_year:
                isDone = True
                break
            if year and end_year and year > end_year:
                continue


            heading = fics[i].find('h4', class_='heading')
            title = heading.find(href=re.compile("works")).text if heading and heading.find(href=re.compile("works")) else "Untitled"
            author_tag = heading.find('a', rel='author') if heading else None
            author = ['Anonymous'] if author_tag is None else [author_tag.text]

            fandom = [f.text for f in fics[i].findAll('a', class_="tag")]
            rating_list = fics[i].findAll('a', class_="help symbol question modal")
            rating = [rating_list[0].text] if rating_list else []

            # extras may be shorter, protect indices
            rels = []
            chars = []
            frees = []
            if i < len(extras):
                rels = [x.text for x in extras[i].findAll('li', class_="relationships")]
                chars = [x.text for x in extras[i].findAll('li', class_="characters")]
                frees = [x.text for x in extras[i].findAll('li', class_="freeforms")]

            word_el = stats[i].find('dd', class_="words") if i < len(stats) else None
            if word_el:
                try:
                    word = int(word_el.text.replace(',', "").strip())
                except ValueError:
                    word = 0
            else:
                word = 0

            titles.append(title)
            authors.append(author)
            ships.append(rels)
            characters.append(chars)
            ratings.append(rating)
            fandoms.append(fandom)
            tags.append(frees)
            words.append(word)

            fic_count += 1
            if progress_callback:
                try:
                    progress_callback(fic_count, title)
                except Exception:
                    pass  # don't crash the scraper if UI callback errors

        p += 1
        time.sleep(1)  # be nice to AO3

    return {
        "titles": titles,
        "authors": authors,
        "ships": ships,
        "characters": characters,
        "ratings": ratings,
        "fandoms": fandoms,
        "tags": tags,
        "words": words,
    }
