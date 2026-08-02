
import requests
from bs4 import BeautifulSoup


def calculate_score(total, errors, weight):
    if total == 0:
        return weight
    score = (total - errors) / total * weight

    return max(0, min(weight, score))


def check_image(soup):
    items = soup.find_all("img")
    miss_alt_count = 0

    for item in items:
        if item.get("alt") is None:
            miss_alt_count += 1

    return {
        "type": "missing_alt",
        "count": miss_alt_count,
        "total": len(items),
        "message": (
            f"ОШИБКА❌: Изображений без alt: {miss_alt_count}."
            if miss_alt_count > 0
            else "✅ У всех изображений есть атрибут alt."
        )
    }


def check_buttons(soup):
    items = soup.find_all("button")
    miss_button_count = 0

    for item in items:
        has_text = bool(item.get_text(strip=True))
        has_aria_label = bool(item.get("aria-label"))
        has_aria_labelledby = bool(item.get("aria-labelledby"))

        if not (
            has_text
            or has_aria_label
            or has_aria_labelledby
        ):
            miss_button_count += 1

    return {
        "type": "button_name",
        "count": miss_button_count,
        "total": len(items),
        "message": (
            f"КРИТИЧЕСКАЯ ОШИБКА❌: Неподписанных кнопок: "
            f"{miss_button_count}."
            if miss_button_count > 0
            else "✅ У всех кнопок есть доступное название."
        )
    }


def check_h1(soup):
    items = soup.find_all("h1")
    many_h1_count = max(0, len(items) - 1)

    return {
        "type": "many_h1",
        "count": many_h1_count,
        # Это проверка одного правила, а не каждого заголовка
        "total": 1,
        "message": (
            f"ПРЕДУПРЕЖДЕНИЕ⚠️: Найдено несколько заголовков h1. "
            f"Лишних заголовков: {many_h1_count}."
            if many_h1_count > 0
            else "✅ Количество заголовков h1 допустимо."
        )
    }


def check_div_onclick(soup):
    items = soup.find_all("div")
    div_onclick_count = 0

    for item in items:
        if item.get("onclick"):
            div_onclick_count += 1

    return {
        "type": "div_onclick",
        "count": div_onclick_count,
        # Проверяем наличие нарушения как отдельное правило
        "total": 1,
        "message": (
            f"КРИТИЧЕСКАЯ ОШИБКА❌: Интерактивных div с onclick: "
            f"{div_onclick_count}."
            if div_onclick_count > 0
            else "✅ Интерактивные div с onclick не найдены."
        )
    }


def check_empty_alt(soup):
    items = soup.find_all("img")
    empty_alt_count = 0

    for item in items:
        alt = item.get("alt")

        if alt is not None and alt.strip() == "":
            empty_alt_count += 1

    return {
        "type": "empty_alt",
        "count": empty_alt_count,
        "total": len(items),
        "message": (
            f"ПРЕДУПРЕЖДЕНИЕ⚠️: Изображений с пустым alt: "
            f"{empty_alt_count}. Проверьте, являются ли они декоративными."
            if empty_alt_count > 0
            else "✅ Пустые alt не найдены."
        )
    }


def check_form_labels(soup):
    fields = soup.find_all(["input", "textarea", "select"])
    checked_fields = []
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

        checked_fields.append(field)

        has_aria_label = bool(field.get("aria-label"))
        has_aria_labelledby = bool(field.get("aria-labelledby"))

        field_id = field.get("id")
        has_label_for = False

        if field_id:
            label = soup.find("label", attrs={"for": field_id})
            has_label_for = label is not None

        has_parent_label = field.find_parent("label") is not None

        if not (
            has_aria_label
            or has_aria_labelledby
            or has_label_for
            or has_parent_label
        ):
            missing_label_count += 1

    return {
        "type": "missing_form_label",
        "count": missing_label_count,
        "total": len(checked_fields),
        "message": (
            f"КРИТИЧЕСКАЯ ОШИБКА❌: Полей формы без подписи: "
            f"{missing_label_count}."
            if missing_label_count > 0
            else "✅ У всех проверенных полей формы есть подпись."
        )
    }


def check_links_without_href(soup):
    links = soup.find_all("a")
    missing_href_count = 0

    for link in links:
        href = link.get("href")

        if href is None or href.strip() == "":
            missing_href_count += 1

    return {
        "type": "link_without_href",
        "count": missing_href_count,
        "total": len(links),
        "message": (
            f"ОШИБКА❌: Ссылок без href: {missing_href_count}."
            if missing_href_count > 0
            else "✅ У всех ссылок есть href."
        )
    }


def check_empty_links(soup):
    links = soup.find_all("a")
    empty_link_count = 0

    for link in links:
        has_text = bool(link.get_text(strip=True))
        has_aria_label = bool(link.get("aria-label"))
        has_aria_labelledby = bool(link.get("aria-labelledby"))

        images = link.find_all("img")

        has_image_alt = any(
            image.get("alt") is not None
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

    return {
        "type": "empty_link",
        "count": empty_link_count,
        "total": len(links),
        "message": (
            f"КРИТИЧЕСКАЯ ОШИБКА❌: Ссылок без доступного названия: "
            f"{empty_link_count}."
            if empty_link_count > 0
            else "✅ У всех ссылок есть доступное название."
        )
    }


def check_link_images_alt(soup):
    links = soup.find_all("a")
    link_images = []

    for link in links:
        link_images.extend(link.find_all("img"))

    missing_link_image_alt_count = 0

    for image in link_images:
        alt = image.get("alt")

        if alt is None or alt.strip() == "":
            missing_link_image_alt_count += 1

    return {
        "type": "link_image_without_alt",
        "count": missing_link_image_alt_count,
        # Считаем изображения, а не ссылки
        "total": len(link_images),
        "message": (
            f"КРИТИЧЕСКАЯ ОШИБКА❌: Изображений внутри ссылок "
            f"без описания: {missing_link_image_alt_count}."
            if missing_link_image_alt_count > 0
            else "✅ У изображений внутри ссылок есть описание."
        )
    }


def check_html_lang(soup):
    html = soup.find("html")

    if html is None:
        return {
            "type": "html_lang",
            "count": 1,
            "total": 1,
            "message": (
                "ОШИБКА❌: Не найден тег html. "
                "Проверьте структуру документа."
            )
        }

    lang = html.get("lang")

    if lang is None or lang.strip() == "":
        return {
            "type": "html_lang",
            "count": 1,
            "total": 1,
            "message": (
                "ОШИБКА❌: У тега html отсутствует атрибут lang."
            )
        }

    return {
        "type": "html_lang",
        "count": 0,
        "total": 1,
        "message": "✅ У страницы указан язык."
    }


def check_iframe_title(soup):
    items = soup.find_all("iframe")
    missing_title_count = 0

    for item in items:
        title = item.get("title")

        if title is None or title.strip() == "":
            missing_title_count += 1

    return {
        "type": "iframe_without_title",
        "count": missing_title_count,
        "total": len(items),
        "message": (
            f"ОШИБКА❌: Элементов iframe без title: "
            f"{missing_title_count}."
            if missing_title_count > 0
            else "✅ У всех iframe есть title."
        )
    }


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

    error_count = (
        positive_tabindex_count
        + invalid_tabindex_count
    )

    return {
        "type": "invalid_tabindex",
        "count": error_count,
        "total": len(items),
        "message": (
            f"ОШИБКА❌: Положительных tabindex: "
            f"{positive_tabindex_count}. "
            f"Некорректных tabindex: {invalid_tabindex_count}."
            if error_count > 0
            else "✅ Некорректные значения tabindex не найдены."
        )
    }


def check_site(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    checks = [
        check_div_onclick,
        check_buttons,
        check_image,
        check_form_labels,
        check_links_without_href,
        check_empty_links,
        check_link_images_alt,
        check_html_lang,
        check_iframe_title,
        check_positive_tabindex,
        check_h1,
        check_empty_alt
    ]

    # Сумма весов равна 100
    weights = {
        "div_onclick": 12,
        "button_name": 12,
        "missing_alt": 12,
        "missing_form_label": 12,
        "link_without_href": 8,
        "empty_link": 10,
        "link_image_without_alt": 8,
        "html_lang": 6,
        "iframe_without_title": 5,
        "invalid_tabindex": 7,
        "many_h1": 3,
        "empty_alt": 5
    }

    results = []
    total_score = 0

    for check in checks:
        result = check(soup)

        weight = weights[result["type"]]

        result["weight"] = weight
        result["score"] = calculate_score(
            result["total"],
            result["count"],
            weight
        )

        total_score += result["score"]
        results.append(result)

    errors = []

    for result in results:
        if result["count"] > 0:
            errors.append(result)

    return {
        "score": round(total_score, 2),
        "errors": errors,
        "results": results
    }

