import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID   = int(os.environ.get("ADMIN_ID"))

CHANNEL_LINK = "https://t.me/claude_buy_sell"

CHOOSE_SERVICE, DESCRIBE_WISH = range(2)

SERVICES = {
    "🤖 Телеграм бот": {"label": "Telegram-бот", "price": "30–35 ⭐"},
    "🌐 Свой сайт":    {"label": "Сайт",         "price": "30 ⭐"},
    "🎮 Игра (бета)":  {"label": "Игра",          "price": "50 ⭐"},
    "🎬 Видео":        {"label": "Видео",          "price": "15 ⭐"},
}

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🤖 Телеграм бот", "🌐 Свой сайт"],
        ["🎮 Игра (бета)", "🎬 Видео"],
        ["💬 Отзывы", "📢 Наш канал"],
        ["🔍 Найти Данные"],
    ],
    resize_keyboard=True,
)

REVIEWS = [
    ("Алибек", "Заказал телеграм бота — всё сделали быстро и качественно! ⭐⭐⭐⭐⭐"),
    ("Дмитрий", "Сделали сайт за 2 дня, очень доволен результатом! ⭐⭐⭐⭐⭐"),
    ("Айгерим", "Заказала видео — получилось отлично, рекомендую! ⭐⭐⭐⭐⭐"),
]


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе заказать нужную услугу.\n\n"
        "💰 <b>Наши цены:</b>\n"
        "🤖 Телеграм бот — 30–35 ⭐\n"
        "🌐 Сайт — 30 ⭐\n"
        "🎮 Игра (бета) — 50 ⭐\n"
        "🎬 Видео — 15 ⭐\n"
        "🔍 Найти данные — 15 ⭐\n\n"
        "Выбери что хочешь заказать:",
        parse_mode="HTML",
        reply_markup=MAIN_KEYBOARD,
    )
    return CHOOSE_SERVICE


async def choose_service(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text

    # Кнопка Отзывы
    if text == "💬 Отзывы":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Читать отзывы", url="https://t.me/otzivi_claude")]
        ])
        await update.message.reply_text(
            "💬 Здесь отзывы наших клиентов!",
            reply_markup=keyboard
        )
        return CHOOSE_SERVICE

    # Кнопка Канал
    if text == "📢 Наш канал":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Перейти в канал", url=CHANNEL_LINK)]
        ])
        await update.message.reply_text(
            "📢 Наш канал — здесь все новости и обновления!",
            reply_markup=keyboard
        )
        return CHOOSE_SERVICE

    # Кнопка Найти Данные
    if text == "🔍 Найти Данные":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✉️ Написать @Dev_AssO", url="https://t.me/Dev_AssO")]
        ])
        await update.message.reply_text(
            "🔍 Чтобы найти данные, напиши мне: @Dev_AssO",
            reply_markup=keyboard
        )
        return CHOOSE_SERVICE

    if text not in SERVICES:
        await update.message.reply_text(
            "Пожалуйста, выбери один из вариантов.",
            reply_markup=MAIN_KEYBOARD,
        )
        return CHOOSE_SERVICE

    service = SERVICES[text]
    ctx.user_data["service"] = service["label"]

    prompts = {
        "🤖 Телеграм бот": "🤖 Отлично! Цена: <b>30–35 ⭐</b>\n\nРасскажи подробнее:\n• Что должен делать бот?\n• Есть ли особые функции?\n• Пожелания по дизайну?",
        "🌐 Свой сайт":    "🌐 Цена: <b>30 ⭐</b>\n\nОпиши сайт:\n• Тематика / назначение?\n• Сколько страниц?\n• Есть примеры которые нравятся?",
        "🎮 Игра (бета)":  "🎮 Цена: <b>50 ⭐</b>\n\nРасскажи об игре:\n• Жанр (платформер, RPG...)?\n• Платформа (ПК, мобилка)?\n• Идея / сюжет?",
        "🎬 Видео":        "🎬 Цена: <b>15 ⭐</b>\n\nОпиши видео:\n• Тема / цель?\n• Формат (анимация, монтаж)?\n• Длина и стиль?",
    }

    await update.message.reply_text(
        prompts[text],
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    return DESCRIBE_WISH


async def describe_wish(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user    = update.effective_user
    service = ctx.user_data.get("service", "Не указано")
    wish    = update.message.text

    order_text = (
        f"📥 <b>Новая заявка!</b>\n\n"
        f"👤 Пользователь: {user.full_name}\n"
        f"🔗 Username: @{user.username or '—'}\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        f"📌 Услуга: <b>{service}</b>\n\n"
        f"💬 Пожелание:\n{wish}"
    )

    try:
        await ctx.bot.send_message(chat_id=ADMIN_ID, text=order_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")

    await update.message.reply_text(
        "✅ Заявка принята! Мы скоро свяжемся с тобой.\n\n"
        "Хочешь заказать ещё что-то?",
        reply_markup=MAIN_KEYBOARD,
    )
    ctx.user_data.clear()
    return CHOOSE_SERVICE


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отменено.", reply_markup=MAIN_KEYBOARD)
    ctx.user_data.clear()
    return CHOOSE_SERVICE


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_service)],
            DESCRIBE_WISH:  [MessageHandler(filters.TEXT & ~filters.COMMAND, describe_wish)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
