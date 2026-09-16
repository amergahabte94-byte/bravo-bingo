import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder='templates', static_folder='static')

# ==========================================
# 1. የቦት ውቅሮች እና መረጃዎች (Configuration)
# ==========================================
BOT_NAME = "Bravo Bingo"
HOUSE_COMMISSION_RATE = 0.20  # 20% ለቤቱ የሚቀረው ኮሚሽን
STAKE_TIERS = [10, 20, 50, 100]  # የሚፈቀዱ የπονታ አማራጮች

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

# ለጊዜው መረጃዎችን ለመያዝ (Databse ሲኖር በ SQL/MongoDB ይቀየራል)
users_db = {} 

# ==========================================
# 2. የሚኒ አፕ ራውቶች (Mini App Frontend & APIs)
# ==========================================

@app.route('/')
def mini_app_home():
    # ሚኒ አፑ የሚከፈትበት ዋናው የ HTML ገጽ (templates/index.html ካለ በቀጥታ ያሳያል)
    try:
        return render_template('index.html')
    except:
        return jsonify({
            "status": "Running",
            "bot_name": BOT_NAME,
            "message": "Bravo Bingo Mini App Backend is active!"
        })

# የባንክ እና የክፍያ መረጃዎችን ለሚኒ አፑ ለማቀበል
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    return jsonify({
        "success": True,
        "accounts": PAYMENT_ACCOUNTS,
        "stakes": STAKE_TIERS
    })

# ዲፖዚት ለመጠየቅ/ለማረጋገጥ
@app.route('/api/deposit', methods=['POST'])
def process_deposit():
    data = request.json
    user_id = str(data.get('user_id'))
    amount = float(data.get('amount', 0))
    payment_method = data.get('method') # CBE ወይም Telebirr
    
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0}
    
    users_db[user_id]["balance"] += amount
    
    return jsonify({
        "success": True,
        "message": f"የ{amount} ብር ዲፖዚት ተመዝግቧል!",
        "new_balance": users_db[user_id]["balance"],
        "account_used": PAYMENT_ACCOUNTS.get(payment_method)
    })

# ዊዝድሮ (Withdrawal) ለመጠየቅ
@app.route('/api/withdraw', methods=['POST'])
def process_withdrawal():
    data = request.json
    user_id = str(data.get('user_id'))
    amount = float(data.get('amount', 0))
    
    if user_id not in users_db or users_db[user_id]["balance"] < amount:
        return jsonify({
            "success": False,
            "message": "በቂ የባላንስ ሂሳብ የለዎትም!"
        }), 400
    
    users_db[user_id]["balance"] -= amount
    
    return jsonify({
        "success": True,
        "message": f"የ {amount} ብር የገንዘብ ማውጣት ጥያቄ ተቀባይነት አግኝቷል!",
        "remaining_balance": users_db[user_id]["balance"]
    })

# ==========================================
# 3. አፕሊኬሽኑን ማስጀመር
# ==========================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
