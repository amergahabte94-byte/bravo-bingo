import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Official Financial Details
CBE_ACCOUNT = "1000682528641"
TELEBIRR_ACCOUNT = "0944123180"

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"🎉 እንኳን ወደ **Bravo Bingo** በሰላም መጡ, {user.first_name}!\n\n"
        "ይህ የቢንጎ ጨዋታ አሸናፊ የሚሆኑበት እና ገንዘብ የሚሸለሙበት አጓጊ መድረክ ነው።\n\n"
        "📜 **የጨዋታ ህጎች እና አጠቃቀም፦**\n"
        "1. የሚፈልጉትን የክፍያ አማራጭ (Stake) ይምረጡ (10, 20, 50, ወይም 100 ብር)።\n"
        "2. ከታች ባሉት የባንክ አካውንቶች ገንዘብ በማስተላለፍ ሪሲቱን ያያይዙ።\n"
        "3. ቦርዶቹን በመምረጥ ጨዋታውን ይጀምሩ!\n\n"
        "🏦 **የክፍያ አካውንቶች፦**\n"
        f"• **CBE (የኢትዮጵያ ንግድ ባንክ):** `{CBE_ACCOUNT}`\n"
        f"• **Telebirr (ቴሌብር):** `{TELEBIRR_ACCOUNT}`\n\n"
        "👇 ከታች ባለው አማራጭ ጨዋታውን ይጀምሩ:"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎮 ጨዋታ ጀምር (Play)", callback_data="play_menu")],
        [InlineKeyboardButton("💳 ሂሳብ መሙላት (Deposit)", callback_data="deposit_info")],
        [InlineKeyboardButton("ℹ️ ህጎች እና መመሪያ", callback_data="rules")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Menu Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "deposit_info":
        text = (
            "💳 **የክፍያ መመሪያ እና አካውንቶች**\n\n"
            f"• **CBE:** `{CBE_ACCOUNT}`\n"
            f"• **Telebirr:** `{TELEBIRR_ACCOUNT}`\n\n"
            "ገንዘብ ካስተላለፉ በኋላ የክፍያ ማረጋገጫውን ይላኩ።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "play_menu":
        text = (
            "🎯 **የStake (መደብ) መጠን ይምረጡ፦**\n"
            "ለማጫወት የሚፈልጉትን መጠን ይምረጡ (200 ቦርዶች ዝግጁ ናቸው):"
        )
        keyboard = [
            [InlineKeyboardButton("10 ብር (Stake 10)", callback_data="stake_10"),
             InlineKeyboardButton("20 ብር (Stake 20)", callback_data="stake_20")],
            [InlineKeyboardButton("50 ብር (Stake 50)", callback_data="stake_50"),
             InlineKeyboardButton("100 ብር (Stake 100)", callback_data="stake_100")],
            [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data.startswith("stake_"):
        stake_amount = query.data.split("_")[1]
        text = f"✅ የ **{stake_amount} ብር** ጨዋታ ተመርጧል። ጨዋታው በቅርቡ ይጀምራል!"
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "rules":
        text = (
            "📜 **የBravo Bingo ህጎች፦**\n"
            "- ማንም ተጫዋች ትክክለኛውን የቦርድ ቅደም ተከተል መከተል አለበት።\n"
            "- ማጭበርበር ወይም ሀሰተኛ ሪሲት መጠቀም ከአገልግሎት ያስወግዳል።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "main_menu":
        await start(update, context)

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logger.error("No TELEGRAM_TOKEN found in environment variables!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
