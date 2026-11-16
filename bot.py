import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ═══════════════════════════════════════
#  НАСТРОЙКИ — ЗАМЕНИ НА СВОИ
# ═══════════════════════════════════════
BOT_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"        # Токен от @BotFather
ADMIN_ID   = 123456789                 # Твой Telegram ID (число) — @lapalilpup2088, узнай через @userinfobot
# ═══════════════════════════════════════

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
CHOOSE_SERVICE, DESCRIBE_WISH = range(2)

SERVICES = {
    "🤖 Телеграм бот": "Telegram-бот",
    "🌐 Свой сайт":    "Сайт",
    "🎮 Игра (бета)":  "Игра",
    "🎬 Видео":        "Видео",
}

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[s] for s in SERVICES.keys()],
    resize_keyboard=True,
    one_time_keyboard=True,
)


# ── /start ──────────────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе заказать нужную услугу.\n\n"
        "Выбери, что хочешь получить:",
        reply_markup=MAIN_KEYBOARD,
    )
    return CHOOSE_SERVICE


# ── Пользователь выбрал услугу ───────────────────────────────────────────────
async def choose_service(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text

    if text not in SERVICES:
        await update.message.reply_text(
            "Пожалуйста, выбери один из вариантов на клавиатуре.",
            reply_markup=MAIN_KEYBOARD,
        )
        return CHOOSE_SERVICE

    ctx.user_data["service"] = SERVICES[text]

    prompts = {
        "🤖 Телеграм бот": (
            "🤖 Отлично! Расскажи подробнее:\n\n"
            "• Что должен делать бот?\n"
            "• Есть ли особые функции?\n"
            "• Любые пожелания по дизайну/языку?"
        ),
        "🌐 Свой сайт": (
            "🌐 Круто! Опиши сайт:\n\n"
            "• Тематика / назначение сайта?\n"
            "• Сколько страниц нужно?\n"
            "• Есть примеры, которые нравятся?"
        ),
        "🎮 Игра (бета)": (
            "🎮 Интересно! Расскажи об игре:\n\n"
            "• Жанр (платформер, головоломка, RPG…)?\n"
            "• Для какой платформы (ПК, мобилка, браузер)?\n"
            "• Идея / сюжет?"
        ),
        "🎬 Видео": (
            "🎬 Опиши видео:\n\n"
            "• Тема / цель видео?\n"
            "• Формат (анимация, монтаж, обучение)?\n"
            "• Длина и стиль?"
        ),
    }

    await update.message.reply_text(
        prompts[text],
        reply_markup=ReplyKeyboardRemove(),
    )
    return DESCRIBE_WISH


# ── Пользователь описал желание ──────────────────────────────────────────────
async def describe_wish(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user     = update.effective_user
    service  = ctx.user_data.get("service", "Не указано")
    wish     = update.message.text

    # Формируем заявку для админа
    order_text = (
        f"📥 <b>Новая заявка!</b>\n\n"
        f"👤 Пользователь: {user.full_name}\n"
        f"🔗 Username: @{user.username or '—'}\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        f"📌 Услуга: <b>{service}</b>\n\n"
        f"💬 Пожелание:\n{wish}"
    )

    # Отправляем заявку админу
    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=order_text,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Не удалось отправить заявку админу: {e}")

    # Благодарим пользователя
    await update.message.reply_text(
        "✅ Заявка принята! Мы скоро свяжемся с тобой.\n\n"
        "Хочешь заказать ещё что-то? Нажми /start",
        reply_markup=ReplyKeyboardRemove(),
    )

    ctx.user_data.clear()
    return ConversationHandler.END


# ── Отмена ───────────────────────────────────────────────────────────────────
async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Отменено. Напиши /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove(),
    )
    ctx.user_data.clear()
    return ConversationHandler.END


# ── Запуск ───────────────────────────────────────────────────────────────────
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_SERVICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_service)
            ],
            DESCRIBE_WISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, describe_wish)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
