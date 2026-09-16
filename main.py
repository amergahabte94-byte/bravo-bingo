import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Official Financial Details & Stakes for Bravo Bingo
CBE_ACCOUNT = "1000682528641"
TELEBIRR_ACCOUNT = "0944123180"

# Start Command & Main Menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"🎉 እንኳን ወደ **Bravo Bingo** በሰላም መጡ, {user.first_name}!\n\n"
        "ይህ የቢንጎ ጨዋታ አሸናፊ የሚሆኑበት እና ሽልማት የሚወስዱበት አጓጊ መድረክ ነው።\n\n"
        "📜 **የጨዋታ ህጎች እና አጠቃቀም፦**\n"
        "1. መጫወት ከመጀመርዎ በፊት ማስተላለፍዎን ይረጋገጡ።\n"
        "2. የሚፈልጉትን የStake (መደብ) መጠን (10፣ 20፣ 50 ወይም 100 ብር) ይምረጡ።\n"
        "3. ከታች ባሉት የባንክ አካውንቶች ገንዘብ በማስተላለፍ ሪሲቱን ያያይዙ።\n\n"
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

# Button Handler for Menu Options & Stakes
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "deposit_info":
        text = (
            "💳 **የክፍያ መመሪያ እና አካውንቶች**\n\n"
            f"• **CBE:** `{CBE_ACCOUNT}`\n"
            f"• **Telebirr:** `{TELEBIRR_ACCOUNT}`\n\n"
            "ገንዘብ ካስተላለፉ በኋላ የክፍያ ማረጋገጫውን (ሪሲቱን) ይላኩ።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "play_menu":
        text = (
            "🎯 **የStake (መደብ) መጠን ይምረጡ፦**\n"
            "ከሚከተሉት አማራጮች ውስጥ አንዱን ይምረጡ (200 ቦርዶች ዝግጁ ናቸው):"
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
        text = (
            f"✅ የ **{stake_amount} ብር** ጨዋታ ተመርጧል!\n\n"
            "ቦርዱ እና የጨዋታ ቁጥሮች (ከ 1 እስከ 200 ያሉ ቦርዶች) እየተዘጋጁ ነው... እባክዎ ትንሽ ይጠብቁ።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "rules":
        text = (
            "📜 **የBravo Bingo ህጎች፦**\n"
            "1. ዋልታ ከመጀመሩ በፊት ምዝገባዎን ያረጋግጡ።\n"
            "2. የተሳሳተ ሪሲት ወይም ሀሰተኛ መረጃ ማቅረብ ከአገልግሎት ውጭ ያደርጋል።\n"
            "3. አሸናፊው ከሌሎች ተጫዋቾች ቀድሞ ቦርዱን መሙላት አለበት።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "main_menu":
        await start(update, context)

def main():
    # ቶከኑ በቀጥታ እዚህ ስለገባ ምንም አይነት Variable ማስተካከል አይጠበቅብዎትም
    TOKEN = "8980600172:AAH-QudXX5OniJGVJw-3ScUv5KUyi4nr5vU"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bravo Bingo Bot is starting successfully...")
    application.run_polling()

if __name__ == "__main__":
    main()
