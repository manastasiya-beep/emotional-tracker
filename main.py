import csv
import io
import os
import atexit
import fcntl
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import db
import keyboards
import rewards
from zoneinfo import ZoneInfo

from config import (
    ART_WEEKLY_REFLECTION_PROMPTS,
    BOT_TOKEN,
    DAILY_FOCUS_PROMPTS,
    DAILY_QUESTIONS,
    DEEP_REFLECTION_QUESTIONS,
    END_OF_DAY_PROMPTS,
    FOCUS_TAGS,
    PAINTINGS,
    REMINDER_INTERVAL_HOURS,
    ZONES,
)

# The bot's own local UTC offset — used only to make /export timestamps
# readable. Reminder timing and "today" boundaries deliberately avoid this:
# the server runs in UTC regardless of where the user actually is, so hours
# a user types (e.g. via /hours) are interpreted as server-clock hours, not
# their real local hours. A real fix needs the user to tell us their offset.
LOCAL_TZ = datetime.now().astimezone().tzinfo

BOT_LOCK_PATH = os.path.join(tempfile.gettempdir(), "artoffocus-bot.lock")
_bot_lock_file = None


def release_bot_lock():
    global _bot_lock_file
    if _bot_lock_file is None:
        return

    try:
        fcntl.flock(_bot_lock_file.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass

    _bot_lock_file.close()
    _bot_lock_file = None


def acquire_bot_lock():
    global _bot_lock_file
    lock_file = open(BOT_LOCK_PATH, "w")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_file.close()
        raise SystemExit("Bot is already running; refusing to start a second polling instance.")

    _bot_lock_file = lock_file
    atexit.register(release_bot_lock)


def user_timezone(telegram_id: int):
    user = db.get_user(telegram_id)
    if not user or not user.get("timezone_name"):
        return timezone.utc
    try:
        return ZoneInfo(user["timezone_name"])
    except Exception:
        return timezone.utc


WELCOME_TEXT = (
    "Привет, {name}! Это ArtOfFocus.\n\n"
    "Идея простая: изучая свои эмоции, ты начинаешь лучше понимать и чужие — "
    "а заодно глубже видеть смысл в искусстве.\n\n"
    "Раз в 2-3 часа буду присылать короткий вопрос «как ты сейчас» — отметить нужно "
    "пару тапов. После последней отметки дня пришлю картину мирового искусства "
    "с одним вопросом, который помогает посмотреть на неё внимательнее. А если за "
    "неделю накопится 15 отметок — будет отдельная картина недели с более глубоким "
    "блоком вопросов для рефлексии.\n\n"
    "Отмечать момент можно и самой в любое время — кнопкой в меню, не дожидаясь "
    "напоминания.\n\n"
    "Когда тебе удобно получать напоминания?"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing = db.get_user(user.id)
    db.upsert_user(user.id, user.first_name or "друг")

    if existing is None:
        await update.message.reply_text(
            WELCOME_TEXT.format(name=user.first_name or "друг"),
            reply_markup=keyboards.active_hours_keyboard(),
        )
        return

    await update.message.reply_text(
        WELCOME_TEXT.format(name=user.first_name or "друг"),
        reply_markup=keyboards.active_hours_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Раз в 2-3 часа в твоё активное время бот спрашивает «как ты сейчас» — "
        "выбираешь энергию, приятность и эмоцию, по желанию — на чём был фокус. "
        "После последней отметки дня — картина и вопрос повнимательнее посмотреть "
        "на неё. За 15 отметок в неделю — отдельная картина недели с более глубокой "
        "рефлексией.\n\n"
        "Команды:\n"
        "/progress — отметки за неделю\n"
        "/export — выгрузить все отметки файлом (CSV)\n"
        "/hours — поменять активные часы\n"
        "/timezone — указать часовой пояс\n"
        "/pause — приостановить напоминания\n"
        "/resume — снова включить напоминания\n\n"
        f"Кнопка «{keyboards.MOMENT_BUTTON_TEXT}» всегда доступна, чтобы отметить момент самому.",
        reply_markup=keyboards.main_menu_keyboard(),
    )


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.set_paused(update.effective_user.id, True)
    await update.message.reply_text("Напоминания приостановлены. /resume — включить обратно.")


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.set_paused(update.effective_user.id, False)
    await update.message.reply_text("Напоминания снова включены.", reply_markup=keyboards.main_menu_keyboard())


def build_weekly_summary(telegram_id: int) -> str:
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    entries = db.entries_since(telegram_id, since)
    if not entries:
        return "Пока нет отметок за последние 7 дней."

    counts = {}
    daily_counts = {}
    for e in entries:
        zone = e["zone"]
        counts[zone] = counts.get(zone, 0) + 1

        created_at = datetime.fromisoformat(e["created_at"]).astimezone(timezone.utc)
        day = created_at.date().isoformat()
        daily_counts[day] = daily_counts.get(day, 0) + 1

    dominant_zone = max(counts.items(), key=lambda item: item[1])[0]
    lines = [
        f"Отметок за неделю: {len(entries)}",
        f"Доминирующая зона: {ZONES[dominant_zone]['label']}",
    ]

    for zone, label in (("red", "🔴"), ("yellow", "🟡"), ("blue", "🔵"), ("green", "🟢")):
        if zone in counts:
            lines.append(f"{label} {ZONES[zone]['label']}: {counts[zone]}")

    recent_days = sorted(daily_counts.items())[-3:]
    if recent_days:
        lines.append("Последние дни:")
        for day, count in recent_days:
            lines.append(f"- {day}: {count} отметок")

    return "\n".join(lines)


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = build_weekly_summary(update.effective_user.id)
    await update.message.reply_text(
        summary,
        reply_markup=keyboards.weekly_reflection_keyboard(),
    )


async def weekly_summary_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = build_weekly_summary(update.effective_user.id)
    await update.message.reply_text(
        summary,
        reply_markup=keyboards.weekly_reflection_keyboard(),
    )


async def handle_weekly_reflection_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, question_type = query.data.split(":")

    if question_type == "skip":
        await query.edit_message_text("Понятно. Можно вернуться к итогам недели позже.")
        await restore_main_menu(context, query.from_user.id)
        return

    prompts = {
        "feeling": "Что ты чувствовал(а) в течение этой недели в целом?",
        "important": "Что было особенно важным или тревожным на этой неделе?",
        "good": "Что было хорошего, ресурсного или поддерживающего в эту неделю?",
    }
    context.user_data["awaiting_weekly_reflection"] = question_type
    await query.edit_message_text(f"{prompts[question_type]}\n\nНапиши коротко в одном сообщении.")


async def hours_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Когда тебе удобно получать напоминания?", reply_markup=keyboards.active_hours_keyboard()
    )


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entries = db.entries_since(update.effective_user.id, "2000-01-01T00:00:00")
    reflections = db.daily_reflections_since(update.effective_user.id, "2000-01-01T00:00:00")
    if not entries and not reflections:
        await update.message.reply_text("Пока нет сохранённых записей.")
        return

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Тип записи", "Дата", "Время", "Зона", "Эмоция", "Фокус", "Вопрос", "Ответ"])
    for e in entries:
        ts = datetime.fromisoformat(e["created_at"]).astimezone(user_timezone(update.effective_user.id))
        writer.writerow([
            "Отметка состояния",
            ts.strftime("%Y-%m-%d"),
            ts.strftime("%H:%M"),
            ZONES[e["zone"]]["label"],
            e["emotion"],
            e["focus_tag"] or "",
            "",
            "",
        ])
    question_labels = {
        "gratitude": "За что я благодарен(а) сегодня?",
        "success": "Что сегодня удалось?",
        "value": "Что было для меня важным?",
        "rest": "Что поможет улучшить состояние?",
        "feeling": "Что я чувствовал(а) в течение этой недели?",
        "important": "Что было особенно важным или тревожным на этой неделе?",
        "good": "Что было хорошего, ресурсного или поддерживающего на этой неделе?",
    }
    for reflection in reflections:
        question_type = reflection["question_type"].split(":")[-1]
        ts = datetime.fromisoformat(reflection["created_at"]).astimezone(user_timezone(update.effective_user.id))
        writer.writerow([
            "Ответ на вопрос",
            ts.strftime("%Y-%m-%d"),
            ts.strftime("%H:%M"),
            "",
            "",
            "",
            question_labels.get(question_type, question_type),
            reflection["answer_text"],
        ])

    doc = io.BytesIO(buf.getvalue().encode("utf-8-sig"))
    doc.name = "artoffocus_export.csv"
    await update.message.reply_document(document=doc, filename="artoffocus_export.csv")


async def moment_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как ты сейчас?", reply_markup=keyboards.energy_keyboard())


async def daily_focus_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери дополнительный фокус дня. Один вопрос будет приходить в конце дня.",
        reply_markup=keyboards.daily_focus_keyboard(),
    )


async def restore_main_menu(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    await context.bot.send_message(
        chat_id=chat_id,
        text="Что дальше?",
        reply_markup=keyboards.main_menu_keyboard(),
    )


async def handle_daily_focus_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, question_type = query.data.split(":", 1)

    if question_type == "disable":
        db.set_daily_focus(query.from_user.id, None)
        await query.edit_message_text(
            "Дополнительный фокус дня отключён.",
            reply_markup=keyboards.main_menu_keyboard(),
        )
        return

    prompt = DAILY_FOCUS_PROMPTS[question_type]
    db.set_daily_focus(query.from_user.id, question_type)
    context.user_data["awaiting_daily_focus_response"] = question_type
    await query.edit_message_text(f"{prompt}\n\nНапиши коротко в одном сообщении — ответ сохранится в дневник.")


async def handle_daily_reflection_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, question_type = query.data.split(":")

    if question_type == "deep":
        await query.edit_message_text(
            "Сделаем глубже: выбери один вопрос.",
            reply_markup=keyboards.deep_reflection_keyboard(),
        )
        return

    if question_type == "skip":
        await query.edit_message_text("Понятно. Если захочешь — можно вернуться позже.")
        return

    context.user_data["awaiting_daily_reflection"] = question_type
    prompt = END_OF_DAY_PROMPTS[question_type]
    await query.edit_message_text(f"{prompt}\n\nНапиши коротко в одном сообщении.")


async def handle_deep_reflection_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, question_type = query.data.split(":")

    if question_type == "skip":
        await query.edit_message_text("Понятно. Короткий дневник останется для тебя доступен позже.")
        await restore_main_menu(context, query.from_user.id)
        return

    context.user_data["awaiting_daily_reflection"] = f"deep:{question_type}"
    prompt = DEEP_REFLECTION_QUESTIONS[question_type]
    await query.edit_message_text(f"{prompt}\n\nНапиши коротко в одном сообщении.")


async def timezone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Укажи часовой пояс в формате IANA, например: Europe/Moscow, Europe/Berlin, UTC\n"
        "Если не уверена — можно написать просто UTC."
    )
    context.user_data["awaiting_timezone"] = True


async def handle_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")

    if parts[1] == "custom":
        context.user_data["awaiting_hours"] = True
        await query.edit_message_text(
            "Напиши через дефис, во сколько начинать и заканчивать напоминания, "
            "например: 8-23"
        )
        return

    _, start_h, end_h = parts
    db.set_active_hours(query.from_user.id, int(start_h), int(end_h))
    await confirm_active_hours(context, query.from_user.id, query)


async def confirm_active_hours(context, telegram_id, query=None):
    text = "Готово! Буду присылать напоминания в этом окне. Меню с кнопкой для ручной отметки — ниже 👇"
    if query:
        await query.edit_message_text(text)
    else:
        await context.bot.send_message(chat_id=telegram_id, text=text)
    await context.bot.send_message(
        chat_id=telegram_id,
        text="Так и живём:",
        reply_markup=keyboards.main_menu_keyboard(),
    )


async def handle_energy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, energy = query.data.split(":")
    await query.edit_message_text("Приятно это тебе сейчас или нет?", reply_markup=keyboards.valence_keyboard(energy))


async def handle_zone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, zone = query.data.split(":")
    context.user_data["draft_zone"] = zone
    await query.edit_message_text("Какая эмоция ближе всего?", reply_markup=keyboards.emotion_keyboard(zone))


async def handle_emotion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, zone, idx = query.data.split(":")
    emotion = ZONES[zone]["emotions"][int(idx)]
    context.user_data["draft_emotion"] = emotion
    await query.edit_message_text("На чём был фокус? (по желанию)", reply_markup=keyboards.focus_keyboard())


async def handle_focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":", 1)
    code = parts[1] if len(parts) == 2 else None
    zone = context.user_data.get("draft_zone")
    emotion = context.user_data.get("draft_emotion")

    if code != "skip" and code not in FOCUS_TAGS:
        await query.edit_message_text(
            "Не удалось распознать этот контекст. Выбери его ещё раз:",
            reply_markup=keyboards.focus_keyboard(),
        )
        return

    if not (zone and emotion):
        await query.edit_message_text("Что-то пошло не так, попробуй отметить момент ещё раз.")
        context.user_data.pop("draft_zone", None)
        context.user_data.pop("draft_emotion", None)
        await restore_main_menu(context, query.from_user.id)
        return

    context.user_data.pop("draft_zone", None)
    context.user_data.pop("draft_emotion", None)
    focus_tag = None if code == "skip" else FOCUS_TAGS[code]

    db.add_entry(query.from_user.id, zone, emotion, focus_tag)

    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    week_count = len(db.entries_since(query.from_user.id, since))
    await query.edit_message_text(
        f"Записано ✅ {emotion}. Отметок за неделю: {week_count}",
    )
    await restore_main_menu(context, query.from_user.id)

    await send_daily_painting_if_due(context, query.from_user.id)

    painting = rewards.maybe_give_weekly_reward(query.from_user.id)
    if painting:
        await send_weekly_reward(context, query.from_user.id, painting)



async def send_daily_painting_if_due(context: ContextTypes.DEFAULT_TYPE, telegram_id: int):
    user = db.get_user(telegram_id)
    if not user:
        return

    tz = user_timezone(telegram_id)
    now_local = datetime.now(tz)
    is_last_checkin = now_local.hour + REMINDER_INTERVAL_HOURS >= user["active_end"]
    if not is_last_checkin:
        return

    today_str = now_local.strftime("%Y-%m-%d")
    if not db.should_send_daily_painting(telegram_id, today_str):
        return

    today_start = datetime.combine(now_local.date(), datetime.min.time(), tzinfo=tz).isoformat()
    entries = db.entries_since(telegram_id, today_start)
    if len(entries) < 1:
        return

    dominant_zone = rewards.dominant_zone(entries)
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_paintings = db.painting_history_since(telegram_id, since)
    excluded_ids = {
        item["painting_id"]
        for item in recent_paintings
        if rewards.painting_valence(item["zone"]) == rewards.painting_valence(dominant_zone)
    }
    painting = rewards.pick_painting(
        dominant_zone,
        exclude_ids=excluded_ids,
        fallback_zone=rewards.neighboring_zone(dominant_zone),
    )

    question = DAILY_QUESTIONS[int(now_local.strftime("%j")) % len(DAILY_QUESTIONS)]
    caption = f"🖼 «{painting['title']}» — {painting['artist']}\n\n{question}"
    await context.bot.send_photo(chat_id=telegram_id, photo=painting["url"], caption=caption)
    db.set_last_painting(telegram_id, painting["id"])
    db.add_painting_history(telegram_id, painting["id"], painting["zone"])
    db.mark_daily_painting_sent(telegram_id, today_str)
    await context.bot.send_message(
        chat_id=telegram_id,
        text="Если хочешь, можно быстро закрыть день:",
        reply_markup=keyboards.daily_reflection_keyboard(),
    )

    focus = db.get_daily_focus(telegram_id)
    if focus and focus.get("enabled"):
        prompt = DAILY_FOCUS_PROMPTS[focus["question_type"]]
        await context.bot.send_message(chat_id=telegram_id, text=f"Доп. фокус дня: {prompt}\n\nНапиши коротко в одном сообщении.")
        context.user_data["awaiting_daily_focus_response"] = focus["question_type"]


async def send_weekly_reward(context: ContextTypes.DEFAULT_TYPE, telegram_id: int, painting: dict):
    user = db.get_user(telegram_id)
    name = user["name"] if user else "друг"
    questions = "\n".join(f"• {q}" for q in ART_WEEKLY_REFLECTION_PROMPTS)
    caption = (
        f"🖼 «{painting['title']}» — {painting['artist']}\n\n"
        f"{name}, посмотри на этот шедевр как на метафорическую карту твоей недели. "
        f"Ответь себе на вопросы:\n\n{questions}\n\n"
        "Если хочешь — ответь сообщением, сохраню это для тебя в файл."
    )
    await context.bot.send_photo(chat_id=telegram_id, photo=painting["url"], caption=caption)
    context.user_data["awaiting_insight"] = painting["id"]


def parse_hours_range(text):
    try:
        start_s, end_s = text.strip().split("-")
        start, end = int(start_s), int(end_s)
    except ValueError:
        return None
    if 0 <= start < end <= 24:
        return start, end
    return None


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == keyboards.MOMENT_BUTTON_TEXT:
        return

    if update.message.text == keyboards.DAILY_FOCUS_BUTTON_TEXT:
        await daily_focus_button(update, context)
        return

    if context.user_data.get("awaiting_hours"):
        parsed = parse_hours_range(update.message.text)
        if not parsed:
            await update.message.reply_text("Не поняла формат. Напиши так: 8-23")
            return
        context.user_data.pop("awaiting_hours")
        db.set_active_hours(update.effective_user.id, *parsed)
        await confirm_active_hours(context, update.effective_user.id)
        return

    if context.user_data.get("awaiting_timezone"):
        tz_name = update.message.text.strip()
        try:
            ZoneInfo(tz_name)
        except Exception:
            await update.message.reply_text("Не смогла распознать такой часовой пояс. Попробуй ещё раз, например: Europe/Moscow или UTC.")
            return
        context.user_data.pop("awaiting_timezone")
        db.set_timezone_name(update.effective_user.id, tz_name)
        await update.message.reply_text(f"Часовой пояс сохранён: {tz_name}.")
        return

    daily_focus_response_type = context.user_data.pop("awaiting_daily_focus_response", None)
    if daily_focus_response_type:
        answer = update.message.text.strip()
        if not answer:
            await update.message.reply_text("Напиши короткий ответ, чтобы я сохранила его для тебя.")
            return
        db.add_daily_reflection(update.effective_user.id, f"daily_focus:{daily_focus_response_type}", answer)
        await update.message.reply_text(
            "Спасибо. Я сохранила ответ на дополнительный фокус дня ✨",
            reply_markup=keyboards.main_menu_keyboard(),
        )
        return

    weekly_reflection_type = context.user_data.pop("awaiting_weekly_reflection", None)
    if weekly_reflection_type:
        answer = update.message.text.strip()
        if not answer:
            await update.message.reply_text("Напиши короткий ответ, чтобы я сохранила его для тебя.")
            return
        db.add_daily_reflection(update.effective_user.id, f"weekly:{weekly_reflection_type}", answer)
        await update.message.reply_text("Спасибо. Я сохранила твой ответ в недельную рефлексию ✨")
        await restore_main_menu(context, update.effective_user.id)
        return

    daily_reflection_type = context.user_data.pop("awaiting_daily_reflection", None)
    if daily_reflection_type:
        answer = update.message.text.strip()
        if not answer:
            await update.message.reply_text("Напиши короткий ответ, чтобы я сохранила его для тебя.")
            return
        db.add_daily_reflection(update.effective_user.id, daily_reflection_type, answer)
        await update.message.reply_text("Спасибо. Я сохранила твой ответ для дневника ✨")
        await restore_main_menu(context, update.effective_user.id)
        return


async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    for user in db.all_active_users():
        tz = user_timezone(user["telegram_id"])
        now_local = datetime.now(tz)
        now_utc = datetime.now(timezone.utc)

        await send_daily_painting_if_due(context, user["telegram_id"])

        if not (user["active_start"] <= now_local.hour < user["active_end"]):
            continue
        last = user["last_reminder_at"]
        if last:
            elapsed_hours = (now_utc - datetime.fromisoformat(last)).total_seconds() / 3600
            if elapsed_hours < REMINDER_INTERVAL_HOURS:
                continue
        await context.bot.send_message(
            chat_id=user["telegram_id"], text="Как ты сейчас? 👋", reply_markup=keyboards.energy_keyboard()
        )
        db.update_last_reminder(user["telegram_id"], now_utc.isoformat())


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Начать / перезапустить"),
        BotCommand("hours", "Изменить активные часы"),
        BotCommand("timezone", "Указать часовой пояс"),
        BotCommand("progress", "Отметки за неделю"),
        BotCommand("export", "Выгрузить все отметки (CSV)"),
        BotCommand("pause", "Приостановить напоминания"),
        BotCommand("resume", "Включить напоминания снова"),
        BotCommand("help", "Как это работает"),
    ])


def main():
    acquire_bot_lock()
    db.init_db()
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("pause", pause_command))
    app.add_handler(CommandHandler("resume", resume_command))
    app.add_handler(CommandHandler("progress", progress_command))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("hours", hours_command))
    app.add_handler(CommandHandler("timezone", timezone_command))

    app.add_handler(MessageHandler(filters.Regex(f"^{keyboards.MOMENT_BUTTON_TEXT}$"), moment_button))
    app.add_handler(MessageHandler(filters.Regex(f"^{keyboards.DAILY_FOCUS_BUTTON_TEXT}$"), daily_focus_button))

    app.add_handler(CallbackQueryHandler(handle_hours, pattern="^hours:"))
    app.add_handler(CallbackQueryHandler(handle_weekly_reflection_choice, pattern="^weekly:"))
    app.add_handler(
        CallbackQueryHandler(
            handle_focus,
            pattern=r"^focus:(meet|focus|perf|routine|personal|skip)$",
        )
    )
    app.add_handler(CallbackQueryHandler(
        handle_daily_focus_choice,
        pattern=r"^focus:(gratitude|success|value|rest|disable)$",
    ))
    app.add_handler(CallbackQueryHandler(handle_daily_focus_choice, pattern="^daily_focus:"))
    app.add_handler(CallbackQueryHandler(handle_daily_reflection_choice, pattern="^dailyq:"))
    app.add_handler(CallbackQueryHandler(handle_deep_reflection_choice, pattern="^deep:"))
    app.add_handler(CallbackQueryHandler(handle_energy, pattern="^nrg:"))
    app.add_handler(CallbackQueryHandler(handle_zone, pattern="^zone:"))
    app.add_handler(CallbackQueryHandler(handle_emotion, pattern="^emo:"))
    app.add_handler(CallbackQueryHandler(handle_focus, pattern="^moment_focus:"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.job_queue.run_repeating(send_reminders, interval=1800, first=30)

    app.run_polling()


if __name__ == "__main__":
    main()
