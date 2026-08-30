from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from config import ZONES, FOCUS_TAGS

MOMENT_BUTTON_TEXT = "📝 Отметить момент"


def active_hours_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Рабочий день (9–18)", callback_data="hours:9:18")],
        [InlineKeyboardButton("Весь день (9–22)", callback_data="hours:9:22")],
        [InlineKeyboardButton("Свой вариант", callback_data="hours:custom")],
    ])


def main_menu_keyboard():
    return ReplyKeyboardMarkup([[MOMENT_BUTTON_TEXT]], resize_keyboard=True)


def energy_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Много энергии", callback_data="nrg:high")],
        [InlineKeyboardButton("🌙 Мало энергии", callback_data="nrg:low")],
    ])


def valence_keyboard(energy):
    if energy == "high":
        row = [
            InlineKeyboardButton("🔴 Неприятно", callback_data="zone:red"),
            InlineKeyboardButton("🟡 Приятно", callback_data="zone:yellow"),
        ]
    else:
        row = [
            InlineKeyboardButton("🔵 Неприятно", callback_data="zone:blue"),
            InlineKeyboardButton("🟢 Приятно", callback_data="zone:green"),
        ]
    return InlineKeyboardMarkup([row])


def emotion_keyboard(zone):
    emotions = ZONES[zone]["emotions"]
    rows = [[InlineKeyboardButton(e, callback_data=f"emo:{zone}:{i}")] for i, e in enumerate(emotions)]
    return InlineKeyboardMarkup(rows)


def focus_keyboard():
    rows = [[InlineKeyboardButton(label, callback_data=f"focus:{code}")] for code, label in FOCUS_TAGS.items()]
    return InlineKeyboardMarkup(rows)
