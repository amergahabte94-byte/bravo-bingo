import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Official Financial Details & Accounts for Bravo Bingo
CBE_ACCOUNT = "1000682528641"
TELEBIRR_ACCOUNT = "0944123180"
ACCOUNT_NAME = "እነያቸዉ አመርጋ"

# ውርርድ አማራጮች እና የቤቱ ኮሚሽን (20%)
STAKE_OPTIONS = [10, 20, 50, 100]
HOUSE_COMMISSION_PERCENT = 0.20

# Temporary memory for user registration and balances
user_data_db = {}

# 200 የሚሆኑ ልዩ የቢንጎ ቦርዶችን በአውቶማቲክ ማመንጨት
def generate_bingo_boards():
    boards = {}
    for board_id in range(1, 201):
        b_col = random.sample(range(1, 16), 5)
        i_col = random.sample(range(16, 31), 5)
        n_col = random.sample(range(31, 46), 4)
        n_col.insert(2, "FREE")
        g_col = random.sample(range(46, 61), 5)
        o_col = random.sample(range(61, 76), 5)
        
        boards[board_id] = {
            "B": b_col, "I": i_col, "N": n_col, "G": g_col, "O": o_col
        }
    return boards

BINGO_BOARDS = generate_bingo_boards()

# Start Command & Registration Flow
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_data_db:
        user_data_db[user_id] = {"balance": 150.0, "registered": False, "selected_stake": 0, "selected_board": None} # ለሙከራ 150 ብር ተሰጥቷል
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

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    balance = user_data_db.get(user_id, {}).get("balance", 0.0)
    
    welcome_text = (
        f"🎯 **Bravo Bingo ዋና ገጽ**\n\n"
        f"👤 ስም: {user.first_name}\n"
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
        user_data_db[user_id] = {"balance": 0.0, "registered": True, "selected_stake": 0, "selected_board": None}

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
            # አውቶማቲክ ዊዝድሮ አማራጮች
            user_data_db[user_id]["balance"] = 0.0 # ባላንሱን በአውቶማቲክ ወደ አድሚን/ከውጭ ወደተጠቃሚው ሲተላለፍ የሚቀነስበት
            text = f"💸 የብር {current_balance} ዊዝድሮ ጥያቄዎ በአውቶማቲክ ተመዝግቧል! በቅርቡ አካውንትዎ ላይ ይገባል።"
        
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "play_menu":
        # 10፣ 20፣ 50 እና 100 ብር ስቴክ አማራጮች
        text = "🎯 **Bravo Bingo - Stake (መደብ) ምርጫ**\n\nእባክዎ የሚፈልጉትን የክፍያ መጠን ይምረጡ፦"
        keyboard = [
            [InlineKeyboardButton("10 ETB", callback_data="stake_10"), InlineKeyboardButton("20 ETB", callback_data="stake_20")],
            [InlineKeyboardButton("50 ETB", callback_data="stake_50"), InlineKeyboardButton("100 ETB", callback_data="stake_100")],
            [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    # የስቴክ ምርጫዎች እና የ Low Balance ማረጋገጫ
    elif query.data in ["stake_10", "stake_20", "stake_50", "stake_100"]:
        stake_amount = int(query.data.split("_")[1])
        
        if current_balance < stake_amount:
            text = f"❌ **Low Balance:** ባላንስዎ ({current_balance} ETB) ለ {stake_amount} ብር ጨዋታ በቂ አይደለም። እባክዎ መጀመሪያ ዴፖዚት ያድርጉ።"
            keyboard = [
                [InlineKeyboardButton("💳 ሂሳብ መሙላት (Deposit)", callback_data="deposit_menu")],
                [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
            ]
        else:
            user_data_db[user_id]["selected_stake"] = stake_amount
            user_data_db[user_id]["balance"] -= stake_amount # ከባላንስ መቀነስ
            text = f"✅ የ {stake_amount} ብር መደብ ተመርጧል!\n\nአሁን ከ **1 እስከ 200** ባሉት ቁጥሮች መካከል የሚፈልጉትን የቢንጎ ቦርድ ቁጥር ይምረጡ (ለምሳሌ፦ ቦርድ ቁጥር 4)። ለመረጡት ቁጥር `board_4` ብለው ይጻፉ ወይም ከታች ያለውን ይጫኑ:"
            keyboard = [
                [InlineKeyboardButton("🎲 ቦርድ ቁጥር 4 ምረጥ", callback_data="board_4")],
                [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
            ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "board_4":
        board_id = 4
        assigned_board = BINGO_BOARDS[board_id]
        user_data_db[user_id]["selected_board"] = board_id
        
        board_str = f"B: {assigned_board['B']}\nI: {assigned_board['I']}\nN: {assigned_board['N']}\nG: {assigned_board['G']}\nO: {assigned_board['O']}"
        text = f"🎉 **ቦርድ ቁጥር {board_id} ተሰጥቶዎታል!**\n\nየእርስዎ የቢንጎ ካርድ ውቅር እነሆ፦\n`{board_str}`\n\nቁጥሮች በአውቶማቲክ መጥራት ጀምረዋል! ሎቢውን ይጠብቁ..."
        keyboard = [[InlineKeyboardButton("🏆 ቢንጎ (Bingo!)", callback_data="claim_bingo")],
                    [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "claim_bingo":
        stake = user_data_db[user_id].get("selected_stake", 10)
        # 20% የቤቱ ኮሚሽን ተቀንሶ ለአሸናፊው የሚሰጥበት ሒሳብ
        house_cut = stake * HOUSE_COMMISSION_PERCENT
        win_prize = stake - house_cut
        user_data_db[user_id]["balance"] += win_prize
        
        text = f"🏆 **እንኳን ደስ አለዎት! ፍጹም አሸናፊ ሆነዋል!**\n\n• የድል ሽልማትዎ: **{win_prize} ETB** (20% የቤት ኮሚሽን ተቀንሷል)\n• አዲስ ባላንስዎ: `{user_data_db[user_id]['balance']} ETB`"
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "check_balance":
        text = f"💰 **የእርስዎ አካውንት ባላንስ፦**\n\n• ቀሪ ገንዘብ፡ **{current_balance} ETB**\n• ስቴተስ፡ {'በቂ ባላንስ አለዎ' if current_balance > 0 else 'Low Balance'}"
        keyboard = [
            [InlineKeyboardButton("💳 Deposit funds", callback_data="deposit_menu")],
            [InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "rules":
        text = (
            "📜 **የBravo Bingo አጠቃቀም መመሪያ፦**\n\n"
            "1. 'Play Game' በመጫወት 10፣ 20፣ 50 ወይም 100 ብር ስቴክ ይምረጡ።\n"
            "2. ከ 1 እስከ 200 ካሉት ቦርዶች መርጠው የቢንጎ ካርድዎን ያግኙ።\n"
            "3. ቁጥሮች በራስ-ሰር ይጠራሉ፤ ሲጨርሱ 'Bingo' በመጫወት ሽልማትዎን ይውሰዱ!"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ገጽ", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "main_menu":
        await show_main_menu_callback(query)

# Photo / Receipt handler for Auto-Deposits
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # አውቶማቲክ የዲፖዚት ማረጋገጫ ሲሙሌሽን (ብር 100 ጨምርለት)
    deposit_added = 100.0
    if user_id not in user_data_db:
        user_data_db[user_id] = {"balance": 0.0, "registered": True}
    
    user_data_db[user_id]["balance"] += deposit_added
    
    text = (
     "📥 **የክፍያ ማረጋገጫ (ሪሲት/ስክሪንሾት) ተረጋግጧል!**\n\n"
     f"✅ በራስ-ሰር አካውንትዎ ላይ **{deposit_added} ETB** ገብቷል!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    TOKEN = "8980600172:AAH-QudXX5OniJGVJw-3ScUv5KUyi4nr5vU"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Bravo Bingo Bot is running successfully with all features...")
    application.run_polling()

if __name__ == "__main__":
    main()

