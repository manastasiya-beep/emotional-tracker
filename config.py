import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ZONES = {
    "red": {
        "label": "Высокая энергия / Неприятно",
        "emotions": ["Злость", "Тревога", "Раздражение", "Напряжение", "Отвращение"],
    },
    "yellow": {
        "label": "Высокая энергия / Приятно",
        "emotions": ["Радость", "Драйв", "Интерес", "Воодушевление", "Удивление"],
    },
    "blue": {
        "label": "Низкая энергия / Неприятно",
        "emotions": ["Грусть", "Усталость", "Вина", "Разочарование", "Стыд"],
    },
    "green": {
        "label": "Низкая энергия / Приятно",
        "emotions": ["Спокойствие", "Баланс", "Доверие", "Умиротворение", "Уют"],
    },
}

FOCUS_TAGS = {
    "meet": "🗣 Общение / встреча",
    "focus": "🎯 Фокусная работа",
    "perf": "🎤 Публичный момент",
    "routine": "🌀 Рутина",
    "personal": "🏠 Личное",
    "skip": "— Пропустить",
}

# Стартовый набор — все ссылки проверены вручную на commons.wikimedia.org,
# статус public domain подтверждён (авторы умерли более 100 лет назад).
PAINTINGS = [
    {
        "id": 1, "zone": "red", "title": "Крик", "artist": "Эдвард Мунк",
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
    },
    {
        "id": 2, "zone": "red", "title": "Сатурн, пожирающий своего сына", "artist": "Франсиско Гойя",
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/82/Francisco_de_Goya%2C_Saturno_devorando_a_su_hijo_%281819-1823%29.jpg",
    },
    {
        "id": 3, "zone": "yellow", "title": "Поцелуй", "artist": "Густав Климт",
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Gustav_Klimt_016.jpg",
    },
    {
        "id": 4, "zone": "yellow", "title": "Бал в Мулен де ла Галетт", "artist": "Огюст Ренуар",
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Renoir%2C_Pierre-Auguste_-_Dance_at_Le_Moulin_de_la_Galette%2C_1876.jpg",
    },
    {
        "id": 5, "zone": "blue", "title": "Абсент", "artist": "Эдгар Дега",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Edgar_Degas_-_In_a_Caf%C3%A9_-_Google_Art_Project_2.jpg",
    },
    {
        "id": 6, "zone": "blue", "title": "Странник над морем тумана", "artist": "Каспар Давид Фридрих",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/af/Caspar_David_Friedrich_-_Wanderer_above_the_Sea_of_Fog.jpeg",
    },
    {
        "id": 7, "zone": "green", "title": "Кувшинки", "artist": "Клод Моне",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg",
    },
    {
        "id": 8, "zone": "green", "title": "Телега для сена", "artist": "Джон Констебл",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d9/John_Constable_The_Hay_Wain.jpg",
    },
]

DAILY_QUESTIONS = [
    "Какая деталь картины первой зацепила твой взгляд — и что она может говорить о тебе сегодня?",
    "Что в этой картине — цвет, поза, свет — перекликается с тем, что ты чувствуешь сейчас?",
    "Если бы эта картина была твоим сегодняшним настроением, какая её часть звучала бы громче всего?",
    "Куда смотрит взгляд на картине (или твой взгляд на неё) — и о чём это тебе говорит?",
    "Если дать этой картине название, отражающее твой день, как бы ты её назвал(а)?",
]

REFLECTION_QUESTIONS = [
    "Какая часть картины больше всего откликается в тебе прямо сейчас?",
    "Какие скрытые смыслы твоей недели передаёт этот сюжет?",
    "О каком ресурсе или источнике напряжения напоминает тебе эта работа?",
    "Что бы ты изменил(а) в картине и как это связано с твоей жизнью?",
    "Какой главный вопрос эта картина задаёт тебе?",
]

END_OF_DAY_PROMPTS = {
    "gratitude": "Что сегодня было хорошего? За что ты благодарен(а)?",
    "success": "Что сегодня получилось особенно хорошо?",
}
DEEP_REFLECTION_QUESTIONS = {
    "body": "Какое ощущение в теле сейчас наиболее заметно?",
    "thought": "Какая мысль или интерпретация связана с этим состоянием?",
    "value": "Какая ценность сейчас особенно важна или нарушена?",
}
WEEKLY_ENTRIES_THRESHOLD = 15
WEEKLY_WINDOW_DAYS = 7
REMINDER_INTERVAL_HOURS = 2.5
