import math


import requests
from bs4 import BeautifulSoup


def check_image(soup):
    items = soup.find_all("img")
    miss_alt_count = 0

    for item in items:
        if item.get("alt") is None:
            miss_alt_count += 1

    if miss_alt_count > 0:
        return {
            "type": "missing_alt",
            "count": miss_alt_count,
            "message": (
                "ОШИБКА❌: Есть неподписанные изображения. "
                "Добавьте ко всем изображениям описание alt. "
                f"Количество ошибок: {miss_alt_count}"
            )
        }

    return None


def check_empty_alt(soup):
    items = soup.find_all("img")
    empty_alt_count = 0

    for item in items:
        if item.has_attr("alt") and item.get("alt").strip() == "":
            empty_alt_count += 1

    if empty_alt_count > 0:
        return {
            "type": "empty_alt",
            "count": empty_alt_count,
            "message": (
                "ПРЕДУПРЕЖДЕНИЕ⚠️: Есть пустые alt. "
                "Проверьте, действительно ли изображения декоративные. "
                f"Количество предупреждений: {empty_alt_count}"
            )
        }

    return None


def check_buttons(soup):
    items = soup.find_all("button")
    miss_button_count = 0

    for item in items:
        has_text = bool(item.get_text(strip=True))
        has_aria_label = bool(item.get("aria-label"))
        has_aria_labelledby = bool(item.get("aria-labelledby"))

        image = item.find("img")
        has_image_alt = (
            image is not None
            and image.has_attr("alt")
            and bool(image.get("alt").strip())
        )

        if not (
            has_text
            or has_aria_label
            or has_aria_labelledby
            or has_image_alt
        ):
            miss_button_count += 1

    if miss_button_count > 0:
        return {
            "type": "missing_button_name",
            "count": miss_button_count,
            "message": (
                "КРИТИЧЕСКАЯ ОШИБКА❌: Есть кнопки без доступного названия. "
                "Добавьте текст, aria-label или aria-labelledby. "
                f"Количество ошибок: {miss_button_count}"
            )
        }

    return None


def check_h1(soup):
    items = soup.find_all("h1")

    if len(items) == 0:
        return {
            "type": "missing_h1",
            "count": 1,
            "message": (
                "ОШИБКА❌: На странице отсутствует заголовок <h1>. "
                "Добавьте один главный заголовок страницы."
            )
        }

    if len(items) > 1:
        many_h1_count = len(items) - 1

        return {
            "type": "many_h1",
            "count": many_h1_count,
            "message": (
                "ОШИБКА❌: На странице несколько заголовков <h1>. "
                "Оставьте один главный заголовок. "
                f"Количество лишних заголовков: {many_h1_count}"
            )
        }

    return None


def check_div_onclick(soup):
    items = soup.find_all("div")
    div_onclick_count = 0

    for item in items:
        if item.get("onclick"):
            div_onclick_count += 1

    if div_onclick_count > 0:
        return {
            "type": "div_onclick",
            "count": div_onclick_count,
            "message": (
                "КРИТИЧЕСКАЯ ОШИБКА❌: Есть элементы <div> с onclick. "
                "Используйте <button> для действия или <a> для перехода. "
                f"Количество ошибок: {div_onclick_count}"
            )
        }

    return None


def check_form_labels(soup):
    fields = soup.find_all(["input", "textarea", "select"])
    missing_label_count = 0

    ignored_input_types = {
        "hidden",
        "submit",
        "button",
        "reset",
        "image"
    }

    for field in fields:
        if field.name == "input":
            input_type = field.get("type", "text").lower()

            if input_type in ignored_input_types:
                continue

        has_aria_label = bool(field.get("aria-label"))
        has_aria_labelledby = bool(field.get("aria-labelledby"))

        field_id = field.get("id")
        has_label_for = False

        if field_id:
            label = soup.find("label", attrs={"for": field_id})
            has_label_for = label is not None

        parent_label = field.find_parent("label")
        has_parent_label = parent_label is not None

        if not (
            has_aria_label
            or has_aria_labelledby
            or has_label_for
            or has_parent_label
        ):
            missing_label_count += 1

    if missing_label_count > 0:
        return {
            "type": "missing_form_label",
            "count": missing_label_count,
            "message": (
                "КРИТИЧЕСКАЯ ОШИБКА❌: Есть поля формы без подписи. "
                "Свяжите поле с <label> или добавьте aria-label. "
                f"Количество ошибок: {missing_label_count}"
            )
        }

    return None


def check_links_without_href(soup):
    links = soup.find_all("a")
    missing_href_count = 0

    for link in links:
        href = link.get("href")

        if href is None or href.strip() == "":
            missing_href_count += 1

    if missing_href_count > 0:
        return {
            "type": "link_without_href",
            "count": missing_href_count,
            "message": (
                "ОШИБКА❌: Есть ссылки без href. "
                "Добавьте адрес перехода или используйте <button>, "
                "если элемент выполняет действие. "
                f"Количество ошибок: {missing_href_count}"
            )
        }

    return None


def check_empty_links(soup):
    links = soup.find_all("a")
    empty_link_count = 0

    for link in links:
        has_text = bool(link.get_text(strip=True))
        has_aria_label = bool(link.get("aria-label"))
        has_aria_labelledby = bool(link.get("aria-labelledby"))

        images = link.find_all("img")

        has_image_alt = any(
            image.has_attr("alt")
            and bool(image.get("alt").strip())
            for image in images
        )

        if not (
            has_text
            or has_aria_label
            or has_aria_labelledby
            or has_image_alt
        ):
            empty_link_count += 1

    if empty_link_count > 0:
        return {
            "type": "empty_link",
            "count": empty_link_count,
            "message": (
                "КРИТИЧЕСКАЯ ОШИБКА❌: Есть ссылки без доступного названия. "
                "Добавьте текст, aria-label или alt для изображения внутри ссылки. "
                f"Количество ошибок: {empty_link_count}"
            )
        }

    return None


def check_link_images_alt(soup):
    links = soup.find_all("a")
    missing_link_image_alt_count = 0

    for link in links:
        images = link.find_all("img")

        for image in images:
            alt = image.get("alt")

            if alt is None or alt.strip() == "":
                missing_link_image_alt_count += 1

    if missing_link_image_alt_count > 0:
        return {
            "type": "link_image_without_alt",
            "count": missing_link_image_alt_count,
            "message": (
                "КРИТИЧЕСКАЯ ОШИБКА❌: Есть изображения внутри ссылок "
                "без текстового описания. Добавьте непустой alt. "
                f"Количество ошибок: {missing_link_image_alt_count}"
            )
        }

    return None


def check_html_lang(soup):
    html = soup.find("html")

    if html is None:
        return {
            "type": "missing_html",
            "count": 1,
            "message": (
                "ОШИБКА❌: Не найден тег <html>. "
                "Проверьте структуру HTML-документа."
            )
        }

    lang = html.get("lang")

    if lang is None or lang.strip() == "":
        return {
            "type": "missing_lang",
            "count": 1,
            "message": (
                "ОШИБКА❌: У тега <html> отсутствует атрибут lang. "
                'Для русскоязычной страницы добавьте <html lang="ru">.'
            )
        }

    return None


def check_iframe_title(soup):
    items = soup.find_all("iframe")
    missing_title_count = 0

    for item in items:
        title = item.get("title")

        if title is None or title.strip() == "":
            missing_title_count += 1

    if missing_title_count > 0:
        return {
            "type": "iframe_without_title",
            "count": missing_title_count,
            "message": (
                "ОШИБКА❌: Есть элементы <iframe> без атрибута title. "
                "Добавьте краткое описание содержимого каждого iframe. "
                f"Количество ошибок: {missing_title_count}"
            )
        }

    return None


def check_positive_tabindex(soup):
    items = soup.find_all(attrs={"tabindex": True})
    positive_tabindex_count = 0
    invalid_tabindex_count = 0

    for item in items:
        tabindex = item.get("tabindex")

        try:
            tabindex_number = int(tabindex)

            if tabindex_number > 0:
                positive_tabindex_count += 1
        except (TypeError, ValueError):
            invalid_tabindex_count += 1

    total_count = positive_tabindex_count + invalid_tabindex_count

    if total_count > 0:
        return {
            "type": "invalid_tabindex",
            "count": total_count,
            "message": (
                "ОШИБКА❌: Найдены некорректные значения tabindex. "
                "Не используйте положительные значения tabindex. "
                f"Положительных значений: {positive_tabindex_count}. "
                f"Некорректных значений: {invalid_tabindex_count}."
            )
        }

    return None


def check_site(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/150 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        timeout=10,
        headers=headers
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    errors = []

    checks = [
        check_div_onclick,
        check_buttons,
        check_image,
        check_empty_alt,
        check_h1,
        check_form_labels,
        check_links_without_href,
        check_empty_links,
        check_link_images_alt,
        check_html_lang,
        check_iframe_title,
        check_positive_tabindex
    ]

    for check in checks:
        result = check(soup)

        if result is not None:
            errors.append(result)

    return errors
