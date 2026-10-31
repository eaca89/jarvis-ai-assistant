"""Part 6 - Remote: message JARVIS from your phone. Same brain and memory, the tools run on your PC."""
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from brain import think, log

load_dotenv()
OWNER = int(os.environ["TELEGRAM_USER_ID"])        # only you can command your PC

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Telegram from {update.effective_user.id}: {update.message.text}")
    log("telegram", from_id=update.effective_user.id, text=update.message.text)
    if update.effective_user.id != OWNER:
        return await update.message.reply_text("Sorry, I only work for my owner.")
    reply = think("me", update.message.text)      # "me" = same memory as the voice JARVIS
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).build()
async def on_error(update, context):
    print("Telegram error:", context.error)
    log("telegram_error", error=str(context.error))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
app.add_error_handler(on_error)
print(f"JARVIS is on Telegram (owner id {OWNER}). Message your bot from your phone.")
app.run_polling()
