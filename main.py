import os
from telegram import Update, ChatPermissions
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = os.getenv("TOKEN")

BAD_WORDS = [
   "زق", "كلب", "حمار", "يلعن", "تبا", "بعير",
   "sex", "porn", "xxx", "18+", "+18", "onlyfans",
   "سكس", "بورن", "نيك", "شرموطة", "قحبة", "عاهرة"
]

BAD_LINKS = [
   "onlyfans", "xvideos", "xnxx", "pornhub",
   "tinyurl", "adult", "xxx", "t.me/+"
]

ALLOWED_LINKS = [
   "youtube.com", "github.com", "google.com",
   "drive.google.com", "docs.google.com", "wikipedia.org",
   "stackoverflow.com", "microsoft.com", "visualstudio.com",
   "learn.microsoft.com", "w3schools.com", "sqlservertutorial.net",
   "tutorialspoint.com", "geeksforgeeks.org", "leetcode.com",
   "kaggle.com", "researchgate.net", "academia.edu",
   "linkedin.com", "twitter.com", "notion.so",
   "figma.com", "canva.com", "trello.com"
]

# تحذيرات الأعضاء
warnings = {}

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
   message = update.message
   if not message or not message.text:
       return

   user = message.from_user
   user_id = user.id
   chat_id = message.chat_id
   text = message.text.lower()

   is_allowed = any(allowed in text for allowed in ALLOWED_LINKS)
   if is_allowed:
       return

   contains_bad_word = any(word in text for word in BAD_WORDS)
   contains_bad_link = any(link in text for link in BAD_LINKS)

   if contains_bad_word:
       warnings[user_id] = warnings.get(user_id, 0) + 1
       count = warnings[user_id]

       await message.delete()

       if count == 1:
           await context.bot.send_message(chat_id,
               f"⚠️ تحذير لـ {user.first_name}\n"
               f"تم حذف رسالتك لاحتوائها على ألفاظ مسيئة\n"
               f"التكرار يؤدي للحظر!")
       else:
           await context.bot.ban_chat_member(chat_id, user_id)
           await context.bot.send_message(chat_id,
               f"🚫 تم حظر {user.first_name}\n"
               f"السبب: تكرار استخدام ألفاظ مسيئة")
           del warnings[user_id]

   elif contains_bad_link:
       await message.delete()
       await context.bot.ban_chat_member(chat_id, user_id)
       await context.bot.send_message(chat_id,
           f"🚫 تم حظر {user.first_name}\n"
           f"السبب: إرسال رابط مشبوه")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   if not update.message.reply_to_message:
       return
   user = update.message.reply_to_message.from_user
   chat_id = update.message.chat_id
   await context.bot.ban_chat_member(chat_id, user.id)
   await context.bot.send_message(chat_id,
       f"🚫 تم حظر {user.first_name} من قبل الإدارة")

def main():
   app = Application.builder().token(TOKEN).build()
   app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))
   app.add_handler(CommandHandler("ban", ban_command))
   print("✅ البوت يعمل...")
   app.run_polling()

if __name__ == "__main__":
   main()