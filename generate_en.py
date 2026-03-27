#!/usr/bin/env python3
"""Generate /en/ English versions of all Poseidon site pages.

For each .html file in root:
1. Copy to en/
2. Change <html lang="ru"> → <html lang="en">
3. Swap data-en values into visible text (default content becomes English)
4. Update <title>, <meta description>, og:title, og:description → English
5. Update og:locale → en_US
6. Update og:url → add /en/
7. Add hreflang alternate links
8. Update internal href links → ../en/
9. Update CSS/JS/image paths → ../
10. Translate Schema.org JSON-LD breadcrumbs & FAQ
"""
import os
import re
import json

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
EN_DIR = os.path.join(SRC_DIR, "en")

# Translation map for titles and descriptions
TITLE_MAP = {
    "Дайвинг на Ко Самуи — Poseidon Diving Center": "Diving in Koh Samui — Poseidon Diving Center",
    "Poseidon Diving Center — дайвинг на Самуи и в ОАЭ": "Poseidon Diving Center — Diving in Samui & UAE",
    "PADI курсы на Самуи — Poseidon Diving Center": "PADI Courses in Samui — Poseidon Diving Center",
    "Цены на дайвинг — Poseidon Diving Center": "Diving Prices — Poseidon Diving Center",
    "Экскурсии на Самуи — Poseidon Diving Center": "Tours in Samui — Poseidon Diving Center",
    "Дайвинг на Ко Тао из Самуи — Poseidon Diving Center": "Diving in Koh Tao from Samui — Poseidon Diving Center",
    "Дайвинг на Пангане — Poseidon Diving Center": "Diving in Koh Phangan — Poseidon Diving Center",
    "Лучший дайвинг на Самуи — Poseidon Diving Center": "Best Diving in Samui — Poseidon Diving Center",
    "Наша команда — Poseidon Diving Center": "Our Team — Poseidon Diving Center",
    "Контакты — Poseidon Diving Center": "Contact — Poseidon Diving Center",
    "Спецкурсы PADI — Poseidon Diving Center": "PADI Specialties — Poseidon Diving Center",
    "Дайв-сайты Самуи и Ко Тао — Poseidon Diving Center": "Dive Sites Samui & Koh Tao — Poseidon Diving Center",
    "ОАЭ — Poseidon Diving Center": "UAE — Poseidon Diving Center",
    "Дайвинг в Фуджейре — Poseidon Diving Center": "Diving in Fujairah — Poseidon Diving Center",
    "Дайвинг в Дубае и РАК — Poseidon Diving Center": "Diving in Dubai & RAK — Poseidon Diving Center",
    "Дайвинг-туры ОАЭ — Poseidon Diving Center": "Diving Tours UAE — Poseidon Diving Center",
    "PADI курсы ОАЭ — Poseidon Diving Center": "PADI Courses UAE — Poseidon Diving Center",
    "Спецкурсы PADI ОАЭ — Poseidon Diving Center": "PADI Specialties UAE — Poseidon Diving Center",
    "Цены ОАЭ — Poseidon Diving Center": "Prices UAE — Poseidon Diving Center",
    "Контакты ОАЭ — Poseidon Diving Center": "Contact UAE — Poseidon Diving Center",
    "Дайвинг в Дубае — Poseidon Diving Center": "Diving in Dubai — Poseidon Diving Center",
    "Poseidon — Дайвинг центр | Самуи & ОАЭ": "Poseidon — Diving Center | Samui & UAE",
    "Ко Нанг Юань — дайвинг, снорклинг, экскурсия с Самуи | Poseidon": "Koh Nang Yuan — Diving, Snorkeling, Tour from Samui | Poseidon",
    "Sail Rock дайвинг — лучший дайв-сайт Самуи и Ко Панган | Poseidon": "Sail Rock Diving — Best Dive Site Samui & Koh Phangan | Poseidon",
    "Дайвинг на Ко Панган — Sail Rock, Mae Haad | Poseidon Samui": "Diving in Koh Phangan — Sail Rock, Mae Haad | Poseidon Samui",
    "Цены на дайвинг в ОАЭ — Фуджейра, Дубай, РАК | Poseidon": "Diving Prices UAE — Fujairah, Dubai, RAK | Poseidon",
    "Цены на дайвинг — Самуи, Тао, Панган | Poseidon": "Diving Prices — Samui, Tao, Phangan | Poseidon",
    "Экскурсии на Ко Самуи — Анг Тонг, острова, рыбалка | Poseidon": "Tours in Koh Samui — Ang Thong, Islands, Fishing | Poseidon",
    "Дайвинг на Ко Тао с Самуи — Poseidon Diving Center": "Diving in Koh Tao from Samui — Poseidon Diving Center",
}

# Description translations
DESC_MAP = {
    "Дайвинг центр Посейдон — PADI курсы, дайв-туры, снорклинг и морские экскурсии на Ко Самуи и в ОАЭ (Фуджейра, Дубай).":
        "Poseidon Diving Center — PADI courses, dive tours, snorkeling and boat excursions in Koh Samui and UAE (Fujairah, Dubai).",
    "Дайвинг на Ко Самуи: дайв-туры на Нанг Юань, Ко Тао, Sail Rock. PADI-курсы от Discover Scuba до Divemaster. 15+ лет опыта.":
        "Diving in Koh Samui: dive trips to Nang Yuan, Koh Tao, Sail Rock. PADI courses from Discover Scuba to Divemaster. 15+ years experience.",
    "Дайв-туры на Нанг Юань, Ко Тао, Sail Rock. PADI-курсы от Discover Scuba до Divemaster. 15+ лет опыта.":
        "Dive trips to Nang Yuan, Koh Tao, Sail Rock. PADI courses from Discover Scuba to Divemaster. 15+ years experience.",
    "PADI курсы дайвинга на Ко Самуи: Bubblemaker, Seal Team, Discover Scuba, Scuba Diver, Open Water, Advanced, Rescue, EFR, Master Scuba Diver, Divemaster, Instructor. Международная сертификация.":
        "PADI diving courses in Koh Samui: Bubblemaker, Seal Team, Discover Scuba, Scuba Diver, Open Water, Advanced, Rescue, EFR, Master Scuba Diver, Divemaster, Instructor. International certification.",
    "Цены на дайвинг, PADI курсы и специализации на островах Самуи, Ко Тао и Ко Панган. Всё включено: снаряжение, инструктор, питание, страховка.":
        "Diving prices, PADI courses and specialties in Samui, Koh Tao and Koh Phangan. All inclusive: equipment, instructor, meals, insurance.",
    "Экскурсии на Ко Самуи: морской парк Анг Тонг, остров Свинок, Нанг Юань, розовые дельфины, рыбалка, джип-сафари, зиплайн. Организуем отдых под ключ.":
        "Tours in Koh Samui: Ang Thong Marine Park, Pig Island, Nang Yuan, pink dolphins, fishing, jeep safari, zipline. Organized trips.",
    "Лучшие дайв-сайты вокруг Ко Самуи: Sail Rock, Chumphon Pinnacle, Southwest Pinnacle, Shark Island. Глубины, морская жизнь, сезон.":
        "Best dive sites around Koh Samui: Sail Rock, Chumphon Pinnacle, Southwest Pinnacle, Shark Island. Depths, marine life, seasons.",
    "Дайв-трипы на Ко Тао с Ко Самуи. Chumphon Pinnacle, Southwest Pinnacle, White Rock, Twins. Китовые акулы, черепахи, рифовые акулы.":
        "Dive trips to Koh Tao from Koh Samui. Chumphon Pinnacle, Southwest Pinnacle, White Rock, Twins. Whale sharks, turtles, reef sharks.",
    "Дайвинг на Ко Панган с Самуи. Sail Rock — лучший дайв-сайт Сиамского залива. Китовые акулы, барракуды, камин. Поездки из Самуи.":
        "Diving in Koh Phangan from Samui. Sail Rock — the best dive site in the Gulf of Thailand. Whale sharks, barracudas, chimney. Trips from Samui.",
    "Всё о дайвинге на Ко Самуи: лучшие сезоны, температура воды, видимость, морская жизнь, китовые акулы. Почему стоит нырять с Poseidon.":
        "Everything about diving in Koh Samui: best seasons, water temperature, visibility, marine life, whale sharks. Why dive with Poseidon.",
    "Команда PADI-инструкторов Poseidon на Ко Самуи. Опытные дайв-мастера, инструкторы и капитаны с многолетним опытом в Таиланде и ОАЭ.":
        "Poseidon's PADI instructor team in Koh Samui. Experienced divemasters, instructors and captains with years of experience in Thailand and UAE.",
    "PADI спецкурсы на Ко Самуи: Deep Diver, Night Diver, Nitrox, Wreck Diver, Подводная фотография, Навигация, Drift Diver, Fish ID.":
        "PADI specialty courses in Koh Samui: Deep Diver, Night Diver, Nitrox, Wreck Diver, Underwater Photography, Navigation, Drift Diver, Fish ID.",
    "Нанг Юань дайвинг и снорклинг с Ко Самуи. Japanese Garden, Twins, вьюпоинт 360°. Koh Nang Yuan diving — трансфер включён, коралловые рифы, тропические рыбы.":
        "Nang Yuan diving and snorkeling from Koh Samui. Japanese Garden, Twins, 360° viewpoint. Koh Nang Yuan diving — transfer included, coral reefs, tropical fish.",
    "Japanese Gardens — мелководный коралловый дайв-сайт у Ко Нанг Юань. Идеален для начинающих дайверов и снорклинга. Poseidon Diving Center, Самуи.":
        "Japanese Gardens — shallow coral dive site near Koh Nang Yuan. Perfect for beginner divers and snorkeling. Poseidon Diving Center, Samui.",
    "Sail Rock (Hin Bai) — лучший дайв-сайт Сиамского залива между Самуи и Ко Тао. Камин (Chimney), китовые акулы, торнадо барракуд. Глубина 5–40м. Поездки из Самуи от 4,500 ฿.":
        "Sail Rock (Hin Bai) — the best dive site in the Gulf of Thailand between Samui and Koh Tao. Chimney, whale sharks, barracuda tornado. Depth 5-40m. Trips from Samui from 4,500 THB.",
    "Chumphon Pinnacle дайвинг — самый знаменитый дайв-сайт Ко Тао. Китовые акулы, гигантские тревалли, барракуды. Дайв-трип с Ко Самуи. Чумпон Пиннакл Ко Тао.":
        "Chumphon Pinnacle diving — the most famous dive site in Koh Tao. Whale sharks, giant trevallies, barracudas. Dive trip from Koh Samui.",
    "Дайвинг в ОАЭ — ежедневные погружения в Фуджейре. Трансфер из Дубая, Шарджи, Рас Эль Хаймы. PADI курсы, ночные погружения.":
        "Diving in UAE — daily dives in Fujairah. Transfer from Dubai, Sharjah, Ras Al Khaimah. PADI courses, night dives.",
    "Дайвинг в Фуджейре — лучшие дайв-сайты ОАЭ: Dibba Rock, Snoopy Island, Shark Island. Акулы, черепахи, кораллы. Ежедневные погружения.":
        "Diving in Fujairah — best UAE dive sites: Dibba Rock, Snoopy Island, Shark Island. Sharks, turtles, corals. Daily dives.",
    "Дайвинг из Дубая и Рас Эль Хаймы — трансфер до Фуджейры, программы на выходные, пакеты погружений. Забираем от отеля.":
        "Diving from Dubai and Ras Al Khaimah — transfer to Fujairah, weekend programs, dive packages. Hotel pickup.",
    "Дайвинг в Дубае — ежедневные выезды из Дубая на побережье Фуджейры. Трансфер от отеля, 2 погружения, снаряжение, обед. Рифовые акулы, черепахи, скаты.":
        "Diving in Dubai — daily trips from Dubai to Fujairah coast. Hotel transfer, 2 dives, equipment, lunch. Reef sharks, turtles, rays.",
    "Дайвинг-туры в ОАЭ: дневные, ночные, выходные и недельные программы. Трансфер из Дубая, Шарджи, Рас Эль Хаймы. Погружения в Фуджейре круглый год.":
        "Diving tours in UAE: day, night, weekend and weekly programs. Transfer from Dubai, Sharjah, Ras Al Khaimah. Diving in Fujairah year-round.",
    "PADI курсы в ОАЭ: Open Water, Advanced, Rescue Diver, EFR, Divemaster. Обучение в тёплых водах Индийского океана. Сертификация PADI, оборудование Scubapro.":
        "PADI courses in UAE: Open Water, Advanced, Rescue Diver, EFR, Divemaster. Training in warm Indian Ocean waters. PADI certification, Scubapro equipment.",
    "Спецкурсы PADI в ОАЭ: Deep Diver, Night Diver, Nitrox, Wreck Diver, Underwater Photographer, Drift Diver. Обучение в Фуджейре, трансфер из Дубая.":
        "PADI specialty courses in UAE: Deep Diver, Night Diver, Nitrox, Wreck Diver, Underwater Photographer, Drift Diver. Training in Fujairah, transfer from Dubai.",
    "Цены на дайвинг в ОАЭ — Фуджейра, Дубай, Рас Эль Хайма, Шарджа. PADI курсы, фан-дайвинг, специализации. Все цены в дирхамах (AED).":
        "Diving prices in UAE — Fujairah, Dubai, Ras Al Khaimah, Sharjah. PADI courses, fun diving, specialties. All prices in AED.",
    "Контакты Poseidon в ОАЭ — Telegram, WhatsApp, телефон. Бронирование дайвинга в Фуджейре. Трансфер из Дубая, Шарджи, РАК.":
        "Poseidon UAE contacts — Telegram, WhatsApp, phone. Dive booking in Fujairah. Transfer from Dubai, Sharjah, RAK.",
}

# Template for generic dive site descriptions
DIVESITE_DESC_TEMPLATE_RU = " — дайв-сайт около Ко Тао и Ко Самуи. Глубина, морская жизнь, как добраться. Poseidon Diving Center."
DIVESITE_DESC_TEMPLATE_EN = " — dive site near Koh Tao and Koh Samui. Depth, marine life, how to get there. Poseidon Diving Center."

# FAQ translations (Russian → English)
FAQ_TRANSLATIONS = {
    "Когда лучший сезон для дайвинга на Самуи?": "When is the best season for diving in Samui?",
    "Лучший сезон — с марта по сентябрь: видимость 15-30 метров, спокойное море, температура воды 28-30°C. Дайвинг возможен круглый год.": "The best season is March to September: 15-30m visibility, calm sea, water temperature 28-30°C. Diving is possible year-round.",
    "Нужен ли опыт для первого погружения?": "Do I need experience for my first dive?",
    "Нет! Программа Discover Scuba Diving позволяет попробовать дайвинг без сертификата. Инструктор проведёт брифинг и будет рядом под водой.": "No! The Discover Scuba Diving program lets you try diving without certification. An instructor will brief you and stay by your side underwater.",
    "Что включено в стоимость дайв-тура?": "What is included in a dive tour price?",
    "Трансфер из отеля, снаряжение, 2 погружения, обед, напитки, страховка, сопровождение русскоязычного инструктора.": "Hotel transfer, equipment, 2 dives, lunch, drinks, insurance, and a professional instructor.",
    "С какого возраста можно нырять?": "What is the minimum age for diving?",
    "Discover Scuba Diving — с 10 лет. Bubblemaker (бассейн) — с 8 лет. Снорклинг — с любого возраста.": "Discover Scuba Diving — from 10 years. Bubblemaker (pool) — from 8 years. Snorkeling — any age.",
    "Сколько стоит дайвинг на Ко Тао?": "How much does diving in Koh Tao cost?",
    "Безопасно ли нырять с акулами?": "Is it safe to dive with sharks?",
    "Нужен ли сертификат для дайвинга?": "Do I need a certification for diving?",
    "Можно ли увидеть китовую акулу на Ко Тао?": "Can I see a whale shark in Koh Tao?",
    "Как добраться до Ко Тао с Самуи?": "How to get from Samui to Koh Tao?",
    "Можно ли нырять без опыта?": "Can I dive without experience?",
    "Есть ли ограничения по здоровью?": "Are there any health restrictions?",
}

# Breadcrumb name translations
BREADCRUMB_TRANSLATIONS = {
    "Ко Самуи": "Koh Samui",
    "Курсы PADI": "PADI Courses",
    "Дайв-сайты": "Dive Sites",
    "Экскурсии": "Tours",
    "Цены": "Prices",
    "Контакты": "Contact",
    "Наша команда": "Our Team",
    "Ко Тао": "Koh Tao",
    "Ко Панган": "Koh Phangan",
    "Спецкурсы": "Specialties",
    "Лучший дайвинг": "Best Diving",
    "ОАЭ": "UAE",
    "Фуджейра": "Fujairah",
    "Дубай и РАК": "Dubai & RAK",
    "Дайвинг-туры": "Diving Tours",
    "Новости": "News",
}


def translate_schema(html):
    """Translate JSON-LD schema blocks."""
    def replace_schema(match):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)

        # Translate BreadcrumbList
        if data.get("@type") == "BreadcrumbList":
            for item in data.get("itemListElement", []):
                name = item.get("name", "")
                if name in BREADCRUMB_TRANSLATIONS:
                    item["name"] = BREADCRUMB_TRANSLATIONS[name]
                # Update URLs
                item_url = item.get("item", "")
                if item_url and "poseidon.pro/" in item_url and "/en/" not in item_url:
                    item["item"] = item_url.replace("poseidon.pro/", "poseidon.pro/en/")

        # Translate FAQPage
        if data.get("@type") == "FAQPage":
            for entity in data.get("mainEntity", []):
                q = entity.get("name", "")
                if q in FAQ_TRANSLATIONS:
                    entity["name"] = FAQ_TRANSLATIONS[q]
                a = entity.get("acceptedAnswer", {}).get("text", "")
                if a in FAQ_TRANSLATIONS:
                    entity["acceptedAnswer"]["text"] = FAQ_TRANSLATIONS[a]

        return f'<script type="application/ld+json">\n  {json.dumps(data, ensure_ascii=False, indent=2)}\n  </script>'

    return re.sub(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        replace_schema,
        html,
        flags=re.DOTALL
    )


def swap_data_en(html):
    """Replace visible text with data-en value for elements that have both data-ru and data-en."""
    def replacer(match):
        before_content = match.group(1)
        old_content = match.group(2)
        after_tag = match.group(3)

        # Extract data-en value
        en_match = re.search(r'data-en="([^"]*)"', before_content)
        if not en_match:
            return match.group(0)

        en_text = en_match.group(1)
        return f'{before_content}{en_text}{after_tag}'

    # Match elements with data-en that have content between > and </
    # This handles: <tag ...data-en="English"...>Russian text</tag>
    html = re.sub(
        r'(<[^>]+data-en="[^"]*"[^>]*>)(.*?)(</(?:a|span|h[1-6]|p|div|li|button|label|strong|em|td|th|dt|dd|figcaption|cite|small|b|i|u)[^>]*>)',
        replacer,
        html,
        flags=re.DOTALL
    )
    return html


def fix_links(html, filename):
    """Update internal links to point to /en/ versions, and asset paths to ../."""
    # CSS/JS/image paths: href="css/..." → href="../css/..."
    html = re.sub(r'(href|src|srcset)="(css/|js/|images/)', r'\1="../\2', html)

    # Internal page links: href="samui.html" → href="samui.html" (same dir in /en/)
    # But href="./" (home) → href="./" stays same (index in /en/)
    # href="#..." stays same

    # Fix logo link: href="./" → href="./" (already correct, index.html in /en/)

    # Fix favicon
    html = html.replace('href="images/', 'href="../images/')
    # Undo double-fix from above regex
    html = html.replace('href="../../images/', 'href="../images/')
    html = html.replace('src="../../images/', 'src="../images/')
    html = html.replace('srcset="../../images/', 'srcset="../images/')
    html = html.replace('src="../../css/', 'src="../css/')
    html = html.replace('href="../../css/', 'href="../css/')
    html = html.replace('href="../../js/', 'href="../js/')
    html = html.replace('src="../../js/', 'src="../js/')

    # Fix Google Fonts and external URLs — undo the ../ for external links
    html = html.replace('href="../https://', 'href="https://')
    html = html.replace('src="../https://', 'src="https://')

    return html


def add_hreflang(html, filename):
    """Add hreflang alternate links in <head>."""
    ru_url = f"https://www.poseidon.pro/{filename}"
    en_url = f"https://www.poseidon.pro/en/{filename}"

    if filename == "index.html":
        ru_url = "https://www.poseidon.pro/"
        en_url = "https://www.poseidon.pro/en/"

    hreflang = f'  <link rel="alternate" hreflang="ru" href="{ru_url}">\n'
    hreflang += f'  <link rel="alternate" hreflang="en" href="{en_url}">\n'
    hreflang += f'  <link rel="alternate" hreflang="x-default" href="{ru_url}">\n'

    # Insert before </head>
    html = html.replace('</head>', hreflang + '</head>')
    return html


def convert_page(filename):
    """Convert a single page to English."""
    src = os.path.join(SRC_DIR, filename)
    dst = os.path.join(EN_DIR, filename)

    with open(src, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Change lang
    html = html.replace('<html lang="ru">', '<html lang="en">')

    # 2. Update og:locale
    html = html.replace('content="ru_RU"', 'content="en_US"')

    # 3. Update og:url
    html = re.sub(
        r'(og:url" content="https://www\.poseidon\.pro/)(.*?")',
        lambda m: f'{m.group(1)}en/{m.group(2)}' if m.group(2) != '"' else f'{m.group(1)}en/"',
        html
    )

    # 4. Translate title
    title_match = re.search(r'<title>(.*?)</title>', html)
    if title_match:
        ru_title = title_match.group(1)
        # Try both with and without HTML entities
        ru_title_decoded = ru_title.replace("&amp;", "&")
        en_title = TITLE_MAP.get(ru_title) or TITLE_MAP.get(ru_title_decoded, ru_title)
        # For dive site pages not in map, do basic translation
        if en_title == ru_title and "Poseidon" in ru_title:
            en_title = ru_title  # Keep as-is if no translation
        # Re-encode & for HTML context
        en_title_html = en_title.replace("&", "&amp;")
        html = html.replace(f'<title>{ru_title}</title>', f'<title>{en_title_html}</title>')
        # og:title uses unescaped &
        en_title_og = en_title.replace("&amp;", "&")
        html = html.replace(f'og:title" content="{ru_title}"', f'og:title" content="{en_title_og}"')
        # Also try decoded version
        html = html.replace(f'og:title" content="{ru_title_decoded}"', f'og:title" content="{en_title_og}"')

    # 5. Translate meta description + og:description
    desc_match = re.search(r'<meta name="description" content="(.*?)"', html)
    if desc_match:
        ru_desc = desc_match.group(1)
        en_desc = DESC_MAP.get(ru_desc)
        if not en_desc and DIVESITE_DESC_TEMPLATE_RU in ru_desc:
            site_name = ru_desc.split(DIVESITE_DESC_TEMPLATE_RU)[0]
            en_desc = site_name + DIVESITE_DESC_TEMPLATE_EN
        if en_desc:
            html = html.replace(f'name="description" content="{ru_desc}"', f'name="description" content="{en_desc}"')
            # Also try og:description (may be shorter)
            og_desc_match = re.search(r'og:description" content="(.*?)"', html)
            if og_desc_match:
                ru_og = og_desc_match.group(1)
                en_og = DESC_MAP.get(ru_og, en_desc)
                html = html.replace(f'og:description" content="{ru_og}"', f'og:description" content="{en_og}"')

    # 6. Swap data-en content into visible text
    html = swap_data_en(html)

    # 7. Translate schema.org
    html = translate_schema(html)

    # 8. Fix asset paths
    html = fix_links(html, filename)

    # 9. Add hreflang (remove any inherited from source first)
    html = re.sub(r'  <link rel="alternate" hreflang="[^"]*" href="[^"]*">\n', '', html)
    html = add_hreflang(html, filename)

    # 10. Update lang toggle default — EN pages should show "RU" button
    # The JS handles this via localStorage, but set default text
    html = html.replace('>EN</button>', '>RU</button>')

    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)


def add_hreflang_to_ru(filename):
    """Add hreflang links to the Russian (source) page too."""
    src = os.path.join(SRC_DIR, filename)

    with open(src, 'r', encoding='utf-8') as f:
        html = f.read()

    # Remove existing hreflang first, then add fresh
    html = re.sub(r'  <link rel="alternate" hreflang="[^"]*" href="[^"]*">\n', '', html)
    html = add_hreflang(html, filename)

    with open(src, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    os.makedirs(EN_DIR, exist_ok=True)

    html_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.html')]
    print(f"Generating EN versions for {len(html_files)} pages...")

    for filename in sorted(html_files):
        try:
            convert_page(filename)
            add_hreflang_to_ru(filename)
            print(f"  OK {filename}")
        except Exception as e:
            print(f"  FAIL {filename}: {e}")

    print(f"\nDone! {len(html_files)} pages in /en/")
    print("Don't forget to update sitemap.xml with EN pages!")


if __name__ == "__main__":
    main()
