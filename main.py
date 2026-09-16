import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Official Financial Details & Accounts for Bravo Bingo (ትክክለኛዎቹ መረጃዎች)
CBE_ACCOUNT = "1000682528641"
TELEBIRR_ACCOUNT = "0944123180"
ACCOUNT_NAME = "እንያቸዉ አመርጋ"

# Temporary memory for user registration and balances
user_data_db = {}

# Start Command & Registration Flow
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_data_db:
        user_data_db[user_id] = {"balance": 0.0, "registered": False}
        text = (
            f"🎉 እንኳን ወደ Bravo Bingo በሰላም መጡ, {user.first_name}!\n\n"
            "ይህንን የቢንጎ ጨዋታ ለመጀመር መጀመሪያ **መመዝገብ (Register)** ይኖርብዎታል።"
        )
        keyboard = [[InlineKeyboardButton("✅ ራሴን መዝግብ (Register)", callback_data="do_register")]]
        
        if update.message:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if update.message:
        await show_main_menu(update, context)

# Registration Handler
async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id in user_data_db:
        user_data_db[user_id]["registered"] = True
    
    await query.answer("✅ በሳካ ሁኔታ ተመዝግበዋል!", show_alert=True)
    await show_main_menu_callback(query)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.effective_user.id
    balance = user_data_db.get(user_id, {}).get("balance", 0.0)
    
    welcome_text = (
        f"🎯 **Bravo Bingo ዋና ገጽ**\n\n"
        f"👤 ስም: {user.first_name}\n"
        f"💰 ባላንስ: `{balance} ETB`\n\n"
        "🎁 **ስጦታ እና ቦነስ፦**\n"
        "• 500 ብር ወይም ከዛ በላይ Deposit ሲያደርጉ 50% ፕላስ ይሸለሙ! 🟢"
    )
    keyboard = [
        [InlineKeyboardButton("🎮 Play Game", callback_data="play_menu")],
        [InlineKeyboardButton("💳 Deposit funds", callback_data="deposit_menu")],
        [InlineKeyboardButton("💸 Withdraw funds", callback_data="withdraw_menu")],
        [InlineKeyboardButton("💰 Check balance", callback_data="check_balance")],
        [InlineKeyboardButton("ℹ️ How to play", callback_data="rules")]
    ]
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_main_menu_callback(query):
    user_id = query.from_user.id
    balance = user_data_db.get(user_id, {}).get("balance", 0.0)
    
    welcome_text = (
        f"🎯 **Bravo Bingo ዋና ገጽ**\n\n"
        f"💰 ባላንስ: `{balance} ETB`\n\n"
        "ከታች ባሉት አማራጮች መቀጠል ይችላሉ:"
    )
    keyboard = [
        [InlineKeyboardButton("🎮 Play Game", callback_data="play_menu")],
        [InlineKeyboardButton("💳 Deposit funds", callback_data="deposit_menu")],
        [InlineKeyboardButton("💸 Withdraw funds", callback_data="withdraw_menu")],
        [InlineKeyboardButton("💰 Check balance", callback_data="check_balance")],
        [InlineKeyboardButton("ℹ️ How to play", callback_data="rules")]
    ]
    await query.edit_message_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Button Handler for Menu Options
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id not in user_data_db:
        user_data_db[user_id] = {"balance": 0.0, "registered": True}

    current_balance = user_data_db[user_id]["balance"]

    if query.data == "do_register":
        user_data_db[user_id]["registered"] = True
        await show_main_menu_callback(query)

    elif query.data == "deposit_menu":
        text = "Please select the bank option you wish to use for the top-up."
        keyboard = [
            [InlineKeyboardButton("Telebirr", callback_data="dep_telebirr"),
             InlineKeyboardButton("CBE", callback_data="dep_cbe")],
            [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "dep_telebirr":
        text = (
            f"👤 ስም: {ACCOUNT_NAME}\n"
            f"📱 አካውንት: `{TELEBIRR_ACCOUNT}`\n\n"
            "🟡 መመሪያ፦\n"
            "1. ከላይ ባለው Telebirr አካውንት ገንዘብ ያስተላልፉ።\n"
            "2. ገንዘብ ከከፈሉ በኋላ የክፍያ ማረጋገጫውን (ስክሪንሾት/ሪሲት) ለዚህ ቦት ይላኩት።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "dep_cbe":
        text = (
            f"👤 ስም: {ACCOUNT_NAME}\n"
            f"🏦 አካውንት: `{CBE_ACCOUNT}`\n\n"
            "🟡 መመሪያ፦\n"
            "1. ከላይ ባለው የንግድ ባንክ አካውንት ገንዘብ ያስተላልፉ።\n"
            "2. ገንዘብ ከከፈሉ በኋላ የክፍያ ማረጋገጫውን (ስክሪንሾት/ሪሲት) ለዚህ ቦት ይላኩት።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "withdraw_menu":
        if current_balance <= 0:
            text = "❌ አካውንትዎ ላይ በቂ ባላንስ ስለሌለ ዊዝድሮ (Withdraw) ማድረግ አይችሉም!"
        else:
            text = f"💸 የእርስዎ ባላንስ: {current_balance} ETB ነው። ዊዝድሮ ለማድረግ የሚፈልጉትን መጠን ይጠይቁ።"
        
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "play_menu":
        if current_balance <= 0:
            text = (
                "🎯 **Bravo Bingo - Stake (መደብ) ምርጫ**\n\n"
                "❌ **Low Balance:** ባላንስዎ 0 ETB ስለሆነ ጨዋታውን መቀላቀል አይችሉም። መጀመሪያ ዴፖዚት ያድርጉ።"
            )
            keyboard = [
                [InlineKeyboardButton("10 ብር (Low balance)", callback_data="low_bal")],
                [InlineKeyboardButton("20 ብር (Low balance)", callback_data="low_bal")],
                [InlineKeyboardButton("50 ብር (Low balance)", callback_data="low_bal")],
                [InlineKeyboardButton("💳 ሂሳብ መሙላት (Deposit)", callback_data="deposit_menu")],
                [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
            ]
        else:
            text = "🎯 ጨዋታውን ለመጀመር የStake መጠን ይምረጡ፦"
            keyboard = [
                [InlineKeyboardButton("Play 10 ETB", callback_data="play_active")],
                [InlineKeyboardButton("Play 20 ETB", callback_data="play_active")],
                [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
            ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "low_bal":
        await query.answer("❌ ባላንስዎ ስለሌለ ጨዋታውን መቀላቀል አይችሉም! እባክዎ መጀመሪያ Deposit ያድርጉ።", show_alert=True)

    elif query.data == "play_active":
        await query.answer("🎮 ወደ ጨዋታው ቦርድ ገብተዋል!", show_alert=True)

    elif query.data == "check_balance":
        text = f"💰 **የእርስዎ አካውንት ባላንስ፦**\n\n• የሐሳብ መጠን፡ **{current_balance} ETB**\n• ስቴተስ፡ {'በቂ ባላንስ አለዎ' if current_balance > 0 else 'Low Balance'}"
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
        await show_main_menu_callback(query)

# Photo / Receipt handler for Deposits
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
     "📥 **የክፍያ ማረጋገጫ (ሪሲት/ስክሪንሾት) ደርሶናል!**\n\n"
     "አስተዳዳሪው (Admin) እስኪመረምረው እና ባላንስዎን እስኪያስተካክለው ትንሽ ይጠብቁ።"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    TOKEN = "8980600172:AAH-QudXX5OniJGVJw-3ScUv5KUyi4nr5vU"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Bravo Bingo Bot is running successfully without errors...")
    application.run_polling()

if __name__ == "__main__":
    main()
