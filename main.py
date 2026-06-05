import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = "8309790192:AAEMOhyZk0hqpEznXm9miR-ulJx3DbYLp7M"
GEMINI_KEY = "AQ.Ab8RN6J9Hn8UQxjzmv77yvHwkaofKFFKJiz3IQL6uXXMg2tLeg"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

async def is_inappropriate(text):
    try:
        response = model.generate_content(
            f"هل هذا النص يحتوي على سباب أو محتوى مخل أو روابط إباحية؟ أجب بـ نعم أو لا فقط:\n{text}"
        )
        return "نعم" in response.text
    except:
        return False

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    user = message.from_user
    chat_id = message.chat_id
    text = message.text

    if await is_inappropriate(text):
        await message.delete()
        await context.bot.ban_chat_member(chat_id, user.id)
        await context.bot.send_message(chat_id,
            f"🚫 تم حظر {user.first_name} تلقائياً لإرسال محتوى مخالف")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return
    user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id
    await context.bot.ban_chat_member(chat_id, user.id)
    await context.bot.send_message(
    chat_id=chat_id,
    text=f"🚫 {user.first_name} تم حظره تلقائيًا لإرسال محتوى مخالف"
)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))
    app.add_handler(CommandHandler("ban", ban_command))
    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()