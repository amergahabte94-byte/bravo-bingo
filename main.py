import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Official Financial Details & Accounts for Bravo Bingo
CBE_ACCOUNT = "1000682528641"
TELEBIRR_ACCOUNT = "0944123180"
ACCOUNT_NAME = "እነያቸዉ አመርጋ"

# Admin Telegram User ID (እራስዎ አድሚን እንዲሆኑ የርስዎን ID እዚህ ያስገቡ - ለምሳሌ: 123456789)
ADMIN_USER_ID = 000000000  # <-- እዚህጋ የቴሌግራም IDዎን ያስገቡ (አማራጭ)

# Temporary memory for user registration and balances
user_data_db = {}

# Start Command & Registration Flow
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_data_db:
        user_data_db[user_id] = {"balance": 0.0, "registered": True}

    welcome_text = (
        f"🎉 እንኳን ወደ Bravo Bingo በሰላም መጡ, {user.first_name}!\n\n"
        f"💰 የእርስዎ ባላንስ: `{user_data_db[user_id]['balance']} ETB`\n\n"
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

# Button Handler for Menu Options
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id not in user_data_db:
        user_data_db[user_id] = {"balance": 0.0, "registered": True}

    current_balance = user_data_db[user_id]["balance"]

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
        # ተጠቃሚው ወደ ጨዋታው ምናሌ በቀጥታ ይገባል (እንዳይከለከል ተስተካክሏል)
        text = (
            "🎯 **Bravo Bingo - Stake (መደብ) ምርጫ**\n\n"
            f"💰 አሁን ያለዎት ባላንስ: `{current_balance} ETB`\n"
            "ለመጫወት የሚፈልጉትን የክፍያ መጠን ይምረጡ፦"
        )
        keyboard = [
            [InlineKeyboardButton("Play 10 ETB", callback_data="play_10")],
            [InlineKeyboardButton("Play 20 ETB", callback_data="play_20")],
            [InlineKeyboardButton("Play 50 ETB", callback_data="play_50")],
            [InlineKeyboardButton("💳 ሂሳብ መሙላት (Deposit)", callback_data="deposit_menu")],
            [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data in ["play_10", "play_20", "play_50"]:
        required_amount = 10 if query.data == "play_10" else (20 if query.data == "play_20" else 50)
        if current_balance < required_amount:
            await query.answer(f"❌ በቂ ባላንስ የለዎትም! ይህንን ጨዋታ ለመጫወት {required_amount} ETB ያስፈልጋል። እባክዎ ዴፖዚት ያድርጉ።", show_alert=True)
        else:
            await query.answer(f"🎮 ጨዋታው ተጀምሯል! መልካም እድል!", show_alert=True)

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
        user = query.from_user
        welcome_text = (
            f"🎯 **Bravo Bingo ዋና ገጽ**\n\n"
            f"👤 ስም: {user.first_name}\n"
            f"💰 ባላንስ: `{user_data_db.get(user_id, {}).get('balance', 0.0)} ETB`"
        )
        keyboard = [
            [InlineKeyboardButton("🎮 Play Game", callback_data="play_menu")],
            [InlineKeyboardButton("💳 Deposit funds", callback_data="deposit_menu")],
            [InlineKeyboardButton("💸 Withdraw funds", callback_data="withdraw_menu")],
            [InlineKeyboardButton("💰 Check balance", callback_data="check_balance")],
            [InlineKeyboardButton("ℹ️ How to play", callback_data="rules")]
        ]
        await query.edit_message_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Photo / Receipt handler for Deposits
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
     "📥 **የክፍያ ማረጋገጫ (ሪሲት/ስክሪንሾት) ደርሶናል!**\n\n"
     "አስተዳዳሪው (Admin) እስኪመረምረው እና ባላንስዎን እስኪያስተካክለው ትንሽ ይጠብቁ። ማረጋገጫው ሲጠናቀቅ በራስ ሰር ባላንስዎ ይጨመራል!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# Admin command to add balance manually: /addbalance user_id amount
async def add_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # args check
    if len(context.args) < 2:
        await update.message.reply_text("አጠቃቀም: /addbalance [የተጠቃሚ_ID] [የመጠን_ልክ]\nምሳሌ: /addbalance 123456789 50")
        return

    try:
        target_user_id = int(context.args[0])
        amount = float(context.args[1])
        
        if target_user_id not in user_data_db:
            user_data_db[target_user_id] = {"balance": 0.0, "registered": True}
            
        user_data_db[target_user_id]["balance"] += amount
        await update.message.reply_text(f"✅ ለተጠቃሚ {target_user_id} መጠን {amount} ETB ተጨምሯል። አጠቃላይ ባላንስ: {user_data_db[target_user_id]['balance']} ETB")
    except Exception as e:
        await update.message.reply_text(f"❌ ስህተት ተፈጥሯል: {e}")

def main():
    TOKEN = "8980600172:AAH-QudXX5OniJGVJw-3ScUv5KUyi4nr5vU"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addbalance", add_balance_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Bravo Bingo Bot is running perfectly with updated flows...")
    application.run_polling()

if __name__ == "__main__":
    main()

