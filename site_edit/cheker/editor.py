def fix_h1(soup):
    items = soup.find_all("h1")
    for item in items[1:]:
        item.name = "h2"
    return soup


def fix_div_onclick(soup):
    items = soup.find_all("div")
    for item in items:
        if item.get("onclick"):
            item.name = "button"
            item["type"] = "button"
    return soup

def fix_tabindex(soup):
    items = soup.find_all(attrs={"tabindex": True})
    for item in items:
        tub_element = item.get("tabindex")
        try:
            num_tab = int(tub_element)

            if num_tab >0:
                del item["tabindex"]

        except (TypeError, ValueError):
            del item["tabindex"]
    return soup

def fix_lang(soup):
    html = soup.find("html")
    lang = html.get("lang")
    if lang is None or lang.strip() == "":
        html["lang"] = "ru"
    return soup

def fix_site(soup):
    fix_h1(soup)
    fix_div_onclick(soup)
    fix_tabindex(soup)
    fix_lang(soup)
    return soup