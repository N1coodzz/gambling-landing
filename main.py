from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import logging

API_TOKEN = '7061910884:AAFuIhI_YJrvfb2bvrYV3OTbh-Azi9QG7Gc'
ADMIN_IDS = [7317215910, 703605167]
CHANNEL_LINK = "https://t.me/+syIFV7GBgEc5OTcy"
ASK_QUESTION = 1

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Подать заявку", callback_data="submit")]]
    )
    await update.message.reply_text(
        "👋 Привет! Для доступа к нашему закрытому каналу пройди простую верификацию.\n\n"
        "⏱ Среднее время обработки заявки — от 1 до 15 минут.",
        reply_markup=keyboard
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "submit":
        context.user_data["attempts"] = 2
        await query.message.reply_text("❓ Вопрос: сколько будет 3 + 2 + 2?")
        return ASK_QUESTION

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    attempts = context.user_data.get("attempts", 0)
    if text == "7":
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{update.effective_user.id}")]]
        )
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                admin_id,
                f"📨 Заявка от @{update.effective_user.username or update.effective_user.full_name} (ID: {update.effective_user.id})",
                reply_markup=keyboard
            )
        await update.message.reply_text(
            "✅ Заявка подана. Ожидайте одобрения администратора.\n\n⏳ Обычно это занимает от 1 до 15 минут."
        )
        return ConversationHandler.END
    else:
        attempts -= 1
        context.user_data["attempts"] = attempts
        if attempts > 0:
            await update.message.reply_text(f"❌ Неверно. Осталось попыток: {attempts}")
            return ASK_QUESTION
        else:
            await update.message.reply_text("⛔ Попытки исчерпаны.")
            return ConversationHandler.END

async def approve_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("⛔ У вас нет прав.", show_alert=True)
        return
    user_id = int(query.data.split("_")[1])
    try:
        await context.bot.send_message(
            user_id,
            f"🎉 Ваша заявка одобрена!\n\n👉 Ссылка на канал: {CHANNEL_LINK}"
        )
        await query.edit_message_text("✅ Пользователь приглашён.")
    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка при отправке: {e}")

def main():
    app = Application.builder().token(API_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^submit$")],
        states={ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]},
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(approve_handler, pattern="^approve_"))

    app.run_polling()

if __name__ == "__main__":
    main()
