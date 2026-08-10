
import requests
from bs4 import BeautifulSoup
from .editor import fix_site

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
            f"У {miss_alt_count} изображений отсутствует текстовое описание(alt). "
            "Пользователь со скринридером не сможет понять, что на них изображено. "
            "Добавьте краткое и понятное описание для каждого информативного изображения."
            if miss_alt_count > 0
            else "Все изображения имеют текстовое описание."
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
            f"У {miss_button_count} кнопок отсутствует понятное название(aria-label либо aria-labelledby). "
            "Пользователь со скринридером услышит только слово «кнопка» и не поймёт её назначение. "
            "Добавьте видимый текст или понятное текстовое название для каждой кнопки."
            if miss_button_count > 0
            else "Все кнопки имеют понятное название."
        )
    }


def check_h1(soup):
    items = soup.find_all("h1")
    many_h1_count = max(0, len(items) - 1)

    return {
        "type": "many_h1",
        "count": many_h1_count,
        "total": 1,
        "message": (
            "Найдено несколько заголовков h1. Структура заголовков страницы может быть непонятной. "
            "Пользователю скринридера будет сложнее быстро понять устройство страницы и переходить между разделами. "
            "Оставьте один основной заголовок страницы и выстройте остальные заголовки последовательно."
            if many_h1_count > 0
            else "Структура основного заголовка не вызывает замечаний."
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
        "total": 1,
        "message": (
            f"На странице найдено {div_onclick_count} интерактивных элементов(div с onclick), которые размечены как обычные блоки. "
            "Вместо div с onclick используйте button."
            "Скринридер может не сообщить пользователю, что на них можно нажать. "
            "Используйте кнопку для действия или ссылку для перехода."
            if div_onclick_count > 0
            else "Интерактивные элементы размечены корректно."
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
            f"У {empty_alt_count} изображений пустое текстовое описание(alt=""). "
            "Если изображение содержит важную информацию, незрячий пользователь её не получит. "
            "Оставляйте пустое описание только у декоративных изображений, а информативным добавьте понятный текст."
            if empty_alt_count > 0
            else "Изображения с пустым описанием не найдены."
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
            f"У {missing_label_count} полей формы отсутствует понятная подпись(aria-label или aria-labelledby). "
            "Пользователь со скринридером не поймёт, какие данные нужно ввести. "
            "Добавьте видимую подпись к каждому полю или задайте ему понятное текстовое название."
            if missing_label_count > 0
            else "Все поля формы имеют понятные подписи."
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
            f"На странице найдено {missing_href_count} ссылок(элементов <a>), у которых отсутствует элемент href или его значение пустое. "
            "Пользователь может попытаться перейти по ссылке, но ничего не произойдёт. "
            "Для навигации необходимо указать корректный href. "
            if missing_href_count > 0
            else "Все ссылки ведут по указанным адресам."
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
            f"У {empty_link_count} ссылок отсутствует понятное название(aria-label либо aria-labelledby). "
            "Пользователь со скринридером не поймёт, куда ведёт ссылка. "
            "Добавьте понятный текст ссылки или текстовое описание её назначения."
            if empty_link_count > 0
            else "Все ссылки имеют понятные названия."
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
        "total": len(link_images),
        "message": (
            f"У {missing_link_image_alt_count} изображений-ссылок отсутствует текстовое описание(alt). "
            "Пользователь со скринридером не поймёт, куда ведёт такое изображение. "
            "Добавьте краткое описание назначения каждой ссылки с изображением."
            if missing_link_image_alt_count > 0
            else "Все изображения-ссылки имеют понятное описание."
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
                "Отсутствует корневой элемент <html>. Не удалось определить основную структуру страницы. "
                "Из-за этого вспомогательные технологии могут неверно обработать содержимое. "
                "Проверьте, что страница содержит корректную основную HTML-структуру."
            )
        }

    lang = html.get("lang")

    if lang is None or lang.strip() == "":
        return {
            "type": "html_lang",
            "count": 1,
            "total": 1,
            "message": (
                "На странице не указан основной язык(<lang>). "
                "Скринридер может выбрать неправильное произношение и читать текст неестественно. "
                "Укажите язык страницы в её основной разметке."
            )
        }

    return {
        "type": "html_lang",
        "count": 0,
        "total": 1,
        "message": "Основной язык страницы указан."
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
            f"У {missing_title_count} встроенных блоков отсутствует понятное описание(title). "
            "Пользователь со скринридером не поймёт, что находится внутри встроенного окна. "
            "Добавьте каждому встроенному блоку краткое и понятное название."
            if missing_title_count > 0
            else "Все встроенные блоки имеют понятные описания."
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
            "Обнаружены проблемы с порядком навигации с клавиатуры(положительное значение элементов с tabindex)"
            "Пользователь может перемещаться по элементам страницы в неожиданном порядке и пропускать важные элементы. "
            "Используйте естественный порядок элементов и не задавайте принудительный положительный порядок перехода."
            if error_count > 0
            else "Порядок навигации с клавиатуры не вызывает замечаний."
        )
    }


def generate_summary(score):
    if score >= 90:
        return (
            "Страница в целом удобна для пользователей со скринридером. "
            "Обнаружены только отдельные замечания, которые стоит проверить перед публикацией."
        )
    if score >= 70:
        return (
            "На странице есть проблемы, которые могут затруднить использование сайта незрячими пользователями. "
            "Часть элементов может озвучиваться непонятно или работать не так, как ожидает пользователь."
        )
    if score >= 50:
        return (
            "На странице обнаружены серьёзные проблемы доступности. "
            "Некоторые изображения, кнопки, ссылки или поля формы могут быть непонятны пользователям со скринридером."
        )
    return (
        "Страница содержит критические проблемы доступности. "
        "Незрячие пользователи могут не понять содержание страницы или не суметь воспользоваться её основными функциями."
    )


def check_site(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    checks = [
        check_buttons,
        check_div_onclick,
        check_form_labels,
        check_empty_links,
        check_link_images_alt,
        check_image,
        check_links_without_href,
        check_html_lang,
        check_iframe_title,
        check_positive_tabindex,
        check_h1,
        check_empty_alt
    ]
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

    final_score = round(total_score, 2)
    edited_soup= BeautifulSoup(response.text, "html.parser")
    fix_site(edited_soup)

    return {
        "score": final_score,
        "summary": generate_summary(final_score),
        "errors": errors,
        "results": results,
        "fixed_site": str(edited_soup),
        "page_note": (
            "Проверена только указанная страница. "
            "Текущая версия не анализирует остальные страницы сайта автоматически."
        )
    }

