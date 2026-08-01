import requests
from bs4 import BeautifulSoup

def check_image(soup):
    items = soup.find_all('img')
    miss_alt_count=0
    for item in items:
        if item.get("alt") is None:
            miss_alt_count +=1
    if miss_alt_count>0:
        return {
            "type": "missing_alt",
            "count": miss_alt_count,
            "message": f"ОШИБКА❌: Есть неподписанные изображения. Добавьте ко всем изображениям описание (alt). Количество ошибок: {miss_alt_count}"
        }
    return None

def check_buttons(soup):
    items = soup.find_all('button')
    miss_button_count = 0
    for item in items:
        if not item.get("aria-label") and not item.get_text(strip=True) :
            miss_button_count += 1
    if miss_button_count:
        return {
            "type": "aria-label",
            "count": miss_button_count,
            "message": f"КРИТИЧЕСКАЯ ОШИБКА❌: Неподписанные кнопки (нет aria-label). Добавьте к каждому <button> атрибут aria-label. Количество ошибок: {miss_button_count}"
        }
    return None

def check_h1(soup):
    items = soup.find_all('h1')
    if len(items) >1:
        many_h1_count = len(items) -1
        return {
            "type": "many_h1",
            "count": many_h1_count,
            "message": f"ОШИБКА❌: Несколько заголовков <h1>. Установите один заголовок (например, можно поменять одни <h1> на <h2>, <h3> или <p>). Количество ошибок:  {many_h1_count}"
        }
    return None

def check_div_onclick(soup):
    items = soup.find_all('div')
    div_onclick_count = 0
    for item in items:
        if item.get("onclick"):
            div_onclick_count += 1
    if div_onclick_count > 0:
        return {
            "type": "div_onclick",
            "count": div_onclick_count,
            "message": f"КРИТИЧЕСКАЯ ОШИБКА❌: Некорректное использование <div>. Вместо <div> используйте <button>. Количество ошибок: {div_onclick_count}"
        }
    return None

def check_empty_alt(soup):
    items = soup.find_all('img')
    empty_alt_count = 0
    for item in items:
        if item.has_attr("alt") and item.get("alt").strip() == "":
            empty_alt_count += 1
    if empty_alt_count>0:
        return {
            "type": "empty_alt",
            "count": empty_alt_count,
            "message": f"ПРЕДУПРЕЖДЕНИЕ⚠️: Есть пустые alt. Проверьте, действительно ли они декоративны. Количество предупреждений: {empty_alt_count}"
        }
    return None

def check_site(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    errors = []

    checks = [check_div_onclick,check_buttons,check_image,check_h1,check_empty_alt]

    for check in checks:
        result = check(soup)

        if result is not None:
            errors.append(result)

    return errors