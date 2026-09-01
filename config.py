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
        "id": 9, "zone": "red", "title": "Спящая цыганка", "artist": "Густав Курбе",
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Gustave_Courbet_-_The_Sleeping_Gypsy_%28The_Sleeping_Gipsy%29.jpg",
    },
    {
        "id": 10, "zone": "red", "title": "Смерть Сарданапала", "artist": "Эдвард Бёрн-Джонс",
        "url": "https://upload.wikimedia.org/wikipedia/commons/1/16/Edward_Burne-Jones_-_The_Decadence_of_the_Sardanapalus.jpg",
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
        "id": 11, "zone": "yellow", "title": "Солнце встаёт", "artist": "Клод Моне",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Claude_Monet_-_Impression%2C_soleil_levant.jpg",
    },
    {
        "id": 12, "zone": "yellow", "title": "Прачки", "artist": "Сандро Боттичелли",
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/88/Sandro_Botticelli_-_The_birth_of_venus.jpg",
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
        "id": 13, "zone": "blue", "title": "Покинутый дом", "artist": "Густав Климт",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Gustav_Klimt_036.jpg",
    },
    {
        "id": 14, "zone": "blue", "title": "Старый мост", "artist": "Клод Моне",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/5d/Claude_Monet_The_Stacks_at_Le_porte_au_soleil.jpg",
    },
    {
        "id": 7, "zone": "green", "title": "Кувшинки", "artist": "Клод Моне",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg",
    },
    {
        "id": 8, "zone": "green", "title": "Телега для сена", "artist": "Джон Констебл",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d9/John_Constable_The_Hay_Wain.jpg",
    },
    {
        "id": 15, "zone": "green", "title": "Лесной путь", "artist": "Артур Милнер",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/73/Arthur_Milner_-_A_Forest_Path.jpg",
    },
    {
        "id": 16, "zone": "green", "title": "Озеро в горах", "artist": "Каспар Давид Фридрих",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Caspar_David_Friedrich_-_The_Sea_of_Ice.jpg",
    },
    {
        "id": 17, "zone": "red", "title": "Лист набросков", "artist": "Эжен Делакруа",
        "url": "https://www.artic.edu/iiif/2/ca266d0e-1917-b446-5267-727c6456e501/full/843,/0/default.jpg",
    },
    {
        "id": 18, "zone": "red", "title": "Жерико на смертном одре", "artist": "Шарль Эмиль Калланд де Шампмартен",
        "url": "https://www.artic.edu/iiif/2/3ef09d92-f10b-f01f-515d-c69a0a3a3e92/full/843,/0/default.jpg",
    },
    {
        "id": 19, "zone": "red", "title": "Воскресение", "artist": "Чекко дель Караваджо",
        "url": "https://www.artic.edu/iiif/2/a49c5ada-f461-d7d1-0f1b-468ac577a872/full/843,/0/default.jpg",
    },
    {
        "id": 20, "zone": "red", "title": "Мильтон диктует дочери", "artist": "Генри Фюзели",
        "url": "https://www.artic.edu/iiif/2/6006b9e7-567a-4fb8-34e2-a120886690fe/full/843,/0/default.jpg",
    },
    {
        "id": 21, "zone": "red", "title": "Воскресение", "artist": "Филипп Галле",
        "url": "https://www.artic.edu/iiif/2/7a0f6878-699d-446a-8754-7b01241cbb7b/full/843,/0/default.jpg",
    },
    {
        "id": 22, "zone": "red", "title": "Купальщицы у реки", "artist": "Анри Матисс",
        "url": "https://www.artic.edu/iiif/2/419ddce3-c90b-3d0c-43b3-73683a87bf98/full/843,/0/default.jpg",
    },
    {
        "id": 23, "zone": "red", "title": "Сад земных наслаждений", "artist": "Иероним Босх",
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/6d/The_Garden_of_Earthly_Delights_by_Bosch_High_Resolution.jpg",
    },
    {
        "id": 24, "zone": "red", "title": "Остров мёртвых", "artist": "Арнольд Бёклин",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Arnold_Boecklin_-_Island_of_the_Dead%2C_Third_Version.JPG",
    },
    {
        "id": 25, "zone": "yellow", "title": "Воскресный день на острове Гранд-Жатт", "artist": "Жорж Сёра",
        "url": "https://www.artic.edu/iiif/2/2d484387-2509-5e8e-2c43-22f9981972eb/full/843,/0/default.jpg",
    },
    {
        "id": 26, "zone": "yellow", "title": "Парижская улица в дождливый день", "artist": "Гюстав Кайботт",
        "url": "https://www.artic.edu/iiif/2/f8fd76e9-c396-5678-36ed-6a348c904d27/full/843,/0/default.jpg",
    },
    {
        "id": 27, "zone": "yellow", "title": "Купание ребёнка", "artist": "Мэри Кассат",
        "url": "https://www.artic.edu/iiif/2/3b885ae0-4d46-5fe4-d70a-00474827f02c/full/843,/0/default.jpg",
    },
    {
        "id": 28, "zone": "yellow", "title": "Фонтан виллы Торлония", "artist": "Джон Сингер Сарджент",
        "url": "https://www.artic.edu/iiif/2/3f9aa9db-61e1-7060-fdb0-bfd7e41ddd08/full/843,/0/default.jpg",
    },
    {
        "id": 29, "zone": "yellow", "title": "Балет в Парижской опере", "artist": "Эдгар Дега",
        "url": "https://www.artic.edu/iiif/2/cb34b0a8-bc51-d063-aab1-47c7debf3a7b/full/843,/0/default.jpg",
    },
    {
        "id": 30, "zone": "yellow", "title": "Мужская фигура", "artist": "Густав Климт",
        "url": "https://www.artic.edu/iiif/2/35a41ca7-f92c-b686-c89f-978321214c5c/full/843,/0/default.jpg",
    },
    {
        "id": 31, "zone": "yellow", "title": "Две сестры на террасе", "artist": "Пьер-Огюст Ренуар",
        "url": "https://www.artic.edu/iiif/2/3a608f55-d76e-fa96-d0b1-0789fbc48f1e/full/843,/0/default.jpg",
    },
    {
        "id": 32, "zone": "yellow", "title": "Звёздная ночь", "artist": "Винсент Ван Гог",
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/66/VanGogh-starry_night_ballance1.jpg",
    },
    {
        "id": 33, "zone": "blue", "title": "Мадонна в горах", "artist": "Каспар Давид Фридрих",
        "url": "https://www.artic.edu/iiif/2/444f3e95-b21f-c821-e6af-00fe9560fb95/full/843,/0/default.jpg",
    },
    {
        "id": 34, "zone": "blue", "title": "Эскиз готической арки", "artist": "Джон Эверетт Милле",
        "url": "https://www.artic.edu/iiif/2/7035a4ba-61c4-c498-618d-8f9076889ac5/full/843,/0/default.jpg",
    },
    {
        "id": 35, "zone": "blue", "title": "В море", "artist": "Арнольд Бёклин",
        "url": "https://www.artic.edu/iiif/2/fa81bfb9-5a07-5e3c-33b4-4efde68981c8/full/843,/0/default.jpg",
    },
    {
        "id": 36, "zone": "blue", "title": "Трагический актёр", "artist": "Эдуар Мане",
        "url": "https://www.artic.edu/iiif/2/8840b41b-2425-c8aa-23fd-db834df457e0/full/843,/0/default.jpg",
    },
    {
        "id": 37, "zone": "blue", "title": "Ноктюрн: синий и золотой", "artist": "Джеймс Макнил Уистлер",
        "url": "https://www.artic.edu/iiif/2/50034c7f-ce51-00f1-430e-a6f7efc233fc/full/843,/0/default.jpg",
    },
    {
        "id": 38, "zone": "blue", "title": "Полуночники", "artist": "Эдвард Хоппер",
        "url": "https://www.artic.edu/iiif/2/831a05de-d3f6-f4fa-a460-23008dd58dda/full/843,/0/default.jpg",
    },
    {
        "id": 39, "zone": "blue", "title": "Девушка у окна", "artist": "Эдвард Мунк",
        "url": "https://www.artic.edu/iiif/2/d7df2633-3b40-f570-c906-211503a37cde/full/843,/0/default.jpg",
    },
    {
        "id": 40, "zone": "blue", "title": "Старый гитарист", "artist": "Пабло Пикассо",
        "url": "https://www.artic.edu/iiif/2/4e7f3081-179a-af18-8abd-7908a7ae8c4e/full/843,/0/default.jpg",
    },
    {
        "id": 41, "zone": "green", "title": "Сток-бай-Нейленд", "artist": "Джон Констебл",
        "url": "https://www.artic.edu/iiif/2/400ce9e8-2f67-44e2-dd68-e6c98880d27f/full/843,/0/default.jpg",
    },
    {
        "id": 42, "zone": "green", "title": "Большая волна в Канагаве", "artist": "Кацусика Хокусай",
        "url": "https://www.artic.edu/iiif/2/b3974542-b9b4-7568-fc4b-966738f61d78/full/843,/0/default.jpg",
    },
    {
        "id": 43, "zone": "green", "title": "Водопад", "artist": "Анри Руссо",
        "url": "https://www.artic.edu/iiif/2/be01ad9a-fe63-1538-2f0a-78e296b0a0d5/full/843,/0/default.jpg",
    },
    {
        "id": 44, "zone": "green", "title": "Корзина яблок", "artist": "Поль Сезанн",
        "url": "https://www.artic.edu/iiif/2/52ac8996-3460-cf71-cb42-5c4d0aa29b74/full/843,/0/default.jpg",
    },
    {
        "id": 45, "zone": "green", "title": "Рыбацкие лодки", "artist": "Уильям Тёрнер",
        "url": "https://www.artic.edu/iiif/2/8641479e-c93e-f1a8-9925-19be061706da/full/843,/0/default.jpg",
    },
    {
        "id": 46, "zone": "green", "title": "Воспоминание об Италии", "artist": "Камиль Коро",
        "url": "https://www.artic.edu/iiif/2/ab107179-7106-937e-7676-e0263b02e530/full/843,/0/default.jpg",
    },
    {
        "id": 47, "zone": "green", "title": "Махана но Atua", "artist": "Поль Гоген",
        "url": "https://www.artic.edu/iiif/2/a4bef587-48a4-d186-813d-f297441b1ab3/full/843,/0/default.jpg",
    },
    {
        "id": 48, "zone": "green", "title": "Цветочные облака", "artist": "Одилон Редон",
        "url": "https://www.artic.edu/iiif/2/fb2077d9-82cc-ca7e-f450-5471d7f78c9a/full/843,/0/default.jpg",
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
    "success": "Что сегодня удалось особенно хорошо?",
    "value": "Что сегодня было для тебя особенно важным?",
    "rest": "Что тебе сегодня особенно нужно, чтобы чувствовать себя лучше?",
}

DAILY_FOCUS_PROMPTS = {
    "gratitude": "🌟 Что было хорошего? Напиши коротко, за что ты благодарен(а) сегодня.",
    "success": "✅ Что сегодня удалось? Какой момент прошёл особенно хорошо?",
    "value": "🎯 Что было важным? На что сегодня было приятно обратить внимание?",
    "rest": "💤 Что нужно для отдыха? Что бы помогло тебе чувствовать себя лучше?",
}

DEEP_REFLECTION_QUESTIONS = {
    "body": "Какое ощущение в теле сейчас наиболее заметно?",
    "thought": "Какая мысль или интерпретация связана с этим состоянием?",
    "value": "Какая ценность сейчас особенно важна или нарушена?",
}

ART_WEEKLY_REFLECTION_PROMPTS = [
    "Какая часть картины больше всего откликается в тебе прямо сейчас?",
    "Какие скрытые смыслы твоей недели передаёт этот сюжет?",
    "О каком ресурсе или источнике напряжения напоминает тебе эта работа?",
    "Что бы ты изменил(а) в картине и как это связано с твоей жизнью?",
    "Какой главный вопрос эта картина задаёт тебе?",
]

WEEKLY_ENTRIES_THRESHOLD = 15
WEEKLY_WINDOW_DAYS = 7
REMINDER_INTERVAL_HOURS = 2.5
