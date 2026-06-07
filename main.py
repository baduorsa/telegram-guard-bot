import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = os.getenv("TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

BAD_WORDS = [
   "زق", "حيوان", "كلب", "حمار", "يلعن", "تبا",
   "sex", "porn", "xxx", "18+", "+18", "onlyfans",
   "سكس", "بورن", "نيك", "شرموطة", "قحبة",
   "t.me/+", "telegram.me/+", "bit.ly", "tinyurl"
]

BAD_LINKS = [
   "onlyfans", "t.me/+", "telegram.me/+",
   "xvideos", "xnxx", "pornhub", "bit.ly/",
   "tinyurl", "adult", "xxx"
]

ALLOWED_LINKS = [
   "youtube.com", "github.com", "google.com",
   "drive.google.com", "docs.google.com", "wikipedia.org"
]

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
   text = message.text.lower()

   contains_bad_word = any(word in text for word in BAD_WORDS)
   contains_bad_link = any(link in text for link in BAD_LINKS) and not any(allowed in text for allowed in ALLOWED_LINKS)

   is_allowed = any(allowed in text for allowed in ALLOWED_LINKS)
   if (contains_bad_word or contains_bad_link or await is_inappropriate(text)) and not is_allowed:
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
   await context.bot.send_message(chat_id, f"🚫 تم حظر {user.first_name}")

def main():
   app = Application.builder().token(TOKEN).build()
   app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))
   app.add_handler(CommandHandler("ban", ban_command))
   print("✅ البوت يعمل...")
   app.run_polling()

if __name__ == "__main__":
   main()