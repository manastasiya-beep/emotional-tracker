from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from config import ZONES, FOCUS_TAGS

MOMENT_BUTTON_TEXT = "📝 Отметить момент"
DAILY_REFLECTION_BUTTON_TEXT = "💬 Как прошёл день?"
DAILY_FOCUS_BUTTON_TEXT = "🎯 Доп. фокус дня"


def active_hours_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Рабочий день (9–18)", callback_data="hours:9:18")],
        [InlineKeyboardButton("Весь день (9–22)", callback_data="hours:9:22")],
        [InlineKeyboardButton("Свой вариант", callback_data="hours:custom")],
    ])


def main_menu_keyboard():
    return ReplyKeyboardMarkup([[MOMENT_BUTTON_TEXT], [DAILY_FOCUS_BUTTON_TEXT]], resize_keyboard=True)


def daily_focus_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌟 За что я благодарен(а)?", callback_data="daily_focus:gratitude")],
        [InlineKeyboardButton("✅ Что сегодня удалось?", callback_data="daily_focus:success")],
        [InlineKeyboardButton("🎯 Что было для меня важным?", callback_data="daily_focus:value")],
        [InlineKeyboardButton("💤 Что поможет улучшить состояние?", callback_data="daily_focus:rest")],
        [InlineKeyboardButton("Отключить дополнительный фокус", callback_data="daily_focus:disable")],
    ])


def weekly_reflection_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💭 Что я чувствовал?", callback_data="weekly:feeling")],
        [InlineKeyboardButton("🎯 Что было важно?", callback_data="weekly:important")],
        [InlineKeyboardButton("🌟 Что было хорошо?", callback_data="weekly:good")],
        [InlineKeyboardButton("Не сейчас", callback_data="weekly:skip")],
    ])


def daily_reflection_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌟 Что сегодня было хорошего?", callback_data="dailyq:gratitude")],
        [InlineKeyboardButton("✅ Что сегодня удалось?", callback_data="dailyq:success")],
        [InlineKeyboardButton("Пропустить", callback_data="dailyq:skip")],
    ])


def deep_reflection_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🫧 Что я чувствую в теле?", callback_data="deep:body")],
        [InlineKeyboardButton("💭 Какая мысль за этим стоит?", callback_data="deep:thought")],
        [InlineKeyboardButton("🎯 Какая ценность важна или нарушена?", callback_data="deep:value")],
        [InlineKeyboardButton("Не сейчас", callback_data="deep:skip")],
    ])


def deep_answer_keyboard(question_type):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Пропустить", callback_data=f"deep_skip:{question_type}")],
        [InlineKeyboardButton("Закончить", callback_data="deep_finish")],
    ])


def energy_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Много энергии", callback_data="nrg:high")],
        [InlineKeyboardButton("🌙 Мало энергии", callback_data="nrg:low")],
    ])


def valence_keyboard(energy):
    if energy == "high":
        row = [
            InlineKeyboardButton("🔴 Неприятно", callback_data="zone:red"),
            InlineKeyboardButton("🟢 Приятно", callback_data="zone:yellow"),
        ]
    else:
        row = [
            InlineKeyboardButton("🔵 Неприятно", callback_data="zone:blue"),
            InlineKeyboardButton("🟢 Приятно", callback_data="zone:green"),
        ]
    return InlineKeyboardMarkup([row, [InlineKeyboardButton("⬅️ Назад", callback_data="moment_back:energy")]])


def emotion_keyboard(zone):
    emotions = ZONES[zone]["emotions"]
    rows = [[InlineKeyboardButton(e, callback_data=f"emo:{zone}:{i}")] for i, e in enumerate(emotions)]
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="moment_back:zone")])
    return InlineKeyboardMarkup(rows)


def focus_keyboard():
    rows = [[InlineKeyboardButton(label, callback_data=f"moment_focus:{code}")] for code, label in FOCUS_TAGS.items()]
    rows.append([InlineKeyboardButton("🔎 Посмотреть глубже", callback_data="moment_focus:deep")])
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="moment_back:emotion")])
    return InlineKeyboardMarkup(rows)
