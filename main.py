import os
import random
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder='templates', static_folder='static')

# ==========================================
# 1. አራዳ ቢንጎ መርህ የያዘ የቦት ውቅር (Configuration)
# ==========================================
BOT_NAME = "Bravo Bingo"
HOUSE_COMMISSION_RATE = 0.20  # 20% ለቤቱ የሚቀረው ኮሚሽን
STAKE_TIERS = [10, 20, 50, 100]  # የሚፈቀዱ የπονታ (Stake) አማራጮች

# የክፍያ አካውንቶች መረጃ (እንያቸው አመርጋ)
PAYMENT_ACCOUNTS = {
    "CBE": {
        "bank_name": "የኢትዮጵያ ንግድ ባንክ (CBE)",
        "account_number": "1000682528641",
        "account_holder": "እንያቸው አመርጋ"
    },
    "Telebirr": {
        "bank_name": "ቴሌብር (Telebirr)",
        "account_number": "0944123180",
        "account_holder": "እንያቸው አመርጋ"
    }
}

# ጊዚያዊ የዳታቤዝ መዋቅር (ለተጠቃሚዎች ባላንስ እና ጌም ስቴት)
users_db = {} 
active_games = {}

# ==========================================
# 2. ሚኒ አፕ እና ኤፒአይ ራውቶች (Mini App & Backend APIs)
# ==========================================

@app.route('/')
def mini_app_home():
    """የሚኒ አፑን ዋና የፊት ገጽ (Frontend) ማሳያ"""
    try:
        return render_template('index.html')
    except:
        return jsonify({
            "status": "Active",
            "bot_name": BOT_NAME,
            "message": "Bravo Bingo Mini App Backend is running successfully!"
        })

@app.route('/api/config', methods=['GET'])
def get_config():
    """ለሚኒ አፑ የሚፈልጉትን ውቅሮች (አካውንቶች እና ፖንታዎች) ማቀበል"""
    return jsonify({
        "success": True,
        "bot_name": BOT_NAME,
        "accounts": PAYMENT_ACCOUNTS,
        "stakes": STAKE_TIERS,
        "commission_rate": HOUSE_COMMISSION_RATE
    })

@app.route('/api/user/balance', methods=['POST'])
def get_user_balance():
    """የተጠቃሚውን ባላንስ ማረጋገጫ"""
    data = request.json
    user_id = str(data.get('user_id'))
    
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0, "username": data.get('username', 'Player')}
        
    return jsonify({
        "success": True,
        "balance": users_db[user_id]["balance"]
    })

@app.route('/api/deposit', methods=['POST'])
def process_deposit():
    """የዲፖዚት ጥያቄ መቀበያ እና ባላንስ ማስተካከያ"""
    data = request.json
    user_id = str(data.get('user_id'))
    amount = float(data.get('amount', 0))
    payment_method = data.get('method') # CBE ወይም Telebirr
    
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0}
    
    # ባላንስ መጨመር
    users_db[user_id]["balance"] += amount
    
    return jsonify({
        "success": True,
        "message": f"የ {amount} ብር ዲፖዚትዎ በተሳካ ሁኔታ ተመዝግቧል!",
        "new_balance": users_db[user_id]["balance"],
        "account_used": PAYMENT_ACCOUNTS.get(payment_method)
    })

@app.route('/api/withdraw', methods=['POST'])
def process_withdrawal():
    """የገንዘብ ማውጣት (Withdrawal) ጥያቄ ማስተናገጃ"""
    data = request.json
    user_id = str(data.get('user_id'))
    amount = float(data.get('amount', 0))
    
    if user_id not in users_db or users_db[user_id]["balance"] < amount:
        return jsonify({
            "success": False,
            "message": "በቂ የባላንስ ሂሳብ የለዎትም!"
        }), 400
    
    # ከሂሳብ መቀነስ
    users_db[user_id]["balance"] -= amount
    
    return jsonify({
        "success": True,
        "message": f"የ {amount} ብር የገንዘብ ማውጣት ጥያቄዎ ተቀባይነት አግኝቷል!",
        "remaining_balance": users_db[user_id]["balance"]
    })

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """የቢንጎ ጨዋታ ፖንታ መምረጫ እና ቋት (Pool) ማቀናበሪያ"""
    data = request.json
    user_id = str(data.get('user_id'))
    stake = int(data.get('stake', 10))
    
    if stake not in STAKE_TIERS:
        return jsonify({"success": False, "message": "የተሳሳተ የπονታ መጠን!"}), 400
        
    if user_id not in users_db or users_db[user_id]["balance"] < stake:
        return jsonify({"success": False, "message": "ለዚህ ጨዋታ በቂ ባላንስ የለዎትም!"}), 400
        
    # ከባላንስ ላይ የπονታውን ዋጋ መቀነስ
    users_db[user_id]["balance"] -= stake
    
    # የቢንጎ ቁጥሮች ማመንጨት ሎጂክ (ከ 1 እስከ 75)
    board_numbers = random.sample(range(1, 76), 25)
    
    return jsonify({
        "success": True,
        "message": f"ጨዋታው በ {stake} ብር ፖንታ ተጀምሯል!",
        "board": board_numbers,
        "remaining_balance": users_db[user_id]["balance"]
    })

@app.route('/api/game/win', methods=['POST'])
def declare_win():
    """ቢንጎ ሲሉ አሸናፊውን ገንዘብ ከ 20% ኮሚሽንቀሪ አስልቶ መስጠት"""
    data = request.json
    user_id = str(data.get('user_id'))
    stake = int(data.get('stake', 10))
    total_pool = float(data.get('total_pool', stake * 5)) # ምሳሌ የተጠቃሚዎች አጠቃላይ ቋት
    
    # 20% ለቤቱ ኮሚሽን መቀነስ፣ 80% ለአሸናፊው መስጠት
    house_cut = total_pool * HOUSE_COMMISSION_RATE
    winner_prize = total_pool - house_cut
    
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0}
        
    users_db[user_id]["balance"] += winner_prize
    
    return jsonify({
        "success": True,
        "message": f"እንኳን ደስ አለዎት! አሸንፈዋል!",
        "prize": winner_prize,
        "house_commission": house_cut,
        "new_balance": users_db[user_id]["balance"]
    })

# ==========================================
# 3. ሰርቨሩን ማስጀመር
# ==========================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
