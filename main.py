import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Official Financial Details & Accounts for Bravo Bingo
CBE_ACCOUNT = "1000682528641"
TELEBIRR_ACCOUNT = "0944123180"
ACCOUNT_NAME = "Enyachew amerga

# Start Command & Main Menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"🎉 እንኳን ወደ **Bravo Bingo** በሰላም መጡ, {user.first_name}!\n\n"
        "ይህ የቢንጎ ጨዋታ አሸናፊ የሚሆኑበት እና ሽልማት የሚወስዱበት አጓጊ መድረክ ነው።\n\n"
        "🎁 **ስጦታ እና ቦነስ፦**\n"
        "• 500 ብር ወይም ከዛ በላይ Deposit ሲያደርጉ 50% ፕላስ ይሸለሙ! 🟢\n\n"
        "📜 **ህጎች፦**\n"
        "1. ጨዋታ ከመጀመርዎ በፊት በቂ ባላንስ ሊኖርዎት ይገባል።\n"
        "2. በቂ ባላንስ ከሌለዎት ከታች ባለው 'Deposit funds' በመጠቀም ሂሳብዎን ይሙሉው።"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎮 Play Game", callback_data="play_menu")],
        [InlineKeyboardButton("💳 Deposit funds", callback_data="deposit_menu")],
        [InlineKeyboardButton("💰 Check balance", callback_data="check_balance")],
        [InlineKeyboardButton("ℹ️ How to play", callback_data="rules")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Button Handler for Menu Options
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "deposit_menu":
        text = "Please select the bank option you wish to use for the top-up."
        keyboard = [
            [InlineKeyboardButton("Telebirr", callback_data="dep_telebirr"),
             InlineKeyboardButton("CBE", callback_data="dep_cbe")],
            [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "dep_telebirr":
        text = (
            f"👤 **ስም:** {ACCOUNT_NAME}\n"
            f"📱 **አካውንት:** `{TELEBIRR_ACCOUNT}`\n\n"
            "🟡 **መመሪያ፦**\n"
            "1. ከላይ ባለው Telebirr አካውንት ገንዘብ ያስተላልፉ።\n"
            "2. በክፍል ሰዓት ያስተላለፉትን መረጃ ከሰጠቁ በኋላ ሪሲቱን (sms) ይላኩ።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "dep_cbe":
        text = (
            f"👤 **ስም:** {ACCOUNT_NAME}\n"
            f"🏦 **አካውንት:** `{CBE_ACCOUNT}`\n\n"
            "🟡 **መመሪያ፦**\n"
            "1. ከላይ ባለው የንግድ ባንክ አካውንት ገንዘብ ያስተላልፉ።\n"
            "2. የተላለፈውን የባንክ ርዕሰ-መልእክት (sms) ቴክስት ኮፒ በማድረግ ይላኩ።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "play_menu":
        text = (
            "🎯 **Bravo Bingo - Stake (መደብ) ምርጫ**\n\n"
            "አሁን ባላንሴ 0 ETB ስለሆነ ጨዋታውን ለመቀላቀል መጀመሪያ ሂሳብ መሙላት (Deposit) ይኖርብዎታል።"
        )
        keyboard = [
            [InlineKeyboardButton("10 ብር (Low balance)", callback_data="low_bal"),
             InlineKeyboardButton("Play 10", callback_data="play_10")],
            [InlineKeyboardButton("20 ብር (Low balance)", callback_data="low_bal"),
             InlineKeyboardButton("Play 20", callback_data="play_20")],
            [InlineKeyboardButton("50 ብር (Low balance)", callback_data="low_bal"),
             InlineKeyboardButton("Play 50", callback_data="play_50")],
            [InlineKeyboardButton("💳 ሂሳብ መሙላት (Deposit)", callback_data="deposit_menu")],
            [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "low_bal":
        await query.answer("❌ ባላንስዎ ስለሌለ ጨዋታውን መቀላቀል አይችሉም! እባክዎ መጀመሪያ Deposit ያድርጉ።", show_alert=True)

    elif query.data == "check_balance":
        text = "💰 **የእርስዎ አካውንት ባላንስ፦**\n\n• የሐሳብ መጠን፡ **0.00 ETB**\n• ስቴተስ፡ በቂ ባላንስ የለዎትም (Low Balance)"
        keyboard = [
            [InlineKeyboardButton("💳 Deposit funds", callback_data="deposit_menu")],
            [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "rules":
        text = (
            "📜 **የBravo Bingo አጠቃቀም መመሪያ፦**\n\n"
            "1. 'Play Game' በመጫወት የሚፈልጉትን የክፍያ መጠን ይምረጡ።\n"
            "2. በቂ ባላንስ ከሌለዎት በ 'Deposit funds' በኩል ገንዘብ በመላክ አካውንትዎን ይሙሉን።\n"
            "3. አሸናፊ ሲሆኑ በራስ ሰር ሽልማትዎ ይገባል!"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "main_menu":
        await start(update, context)

def main():
    TOKEN = "8980600172:AAH-QudXX5OniJGVJw-3ScUv5KUyi4nr5vU"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bravo Bingo Bot is starting successfully...")
    application.run_polling()

if __name__ == "__main__":
    main()

