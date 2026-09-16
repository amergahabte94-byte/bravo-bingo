from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# --- Bravo Bingo Configs & Correct Account Details ---
BOT_NAME = "Bravo Bingo"
TELEBIRR_ACCOUNT = "0944123180"
TELEBIRR_NAME = "እኒያቸው (Enyachew)"
CBE_ACCOUNT = "1000682528641"
CBE_NAME = "Enyachew Amerga"

# Allowed Stakes (Including 10 тен/100 ETB as requested)
ALLOWED_STAKES = [10, 20, 50, 100]

@app.route('/')
def index():
    return render_template('index.html', bot_name=BOT_NAME)

# Deposit Instructions with Correct Accounts (No Bonus Text)
@app.route('/api/deposit_instructions', methods=['GET'])
def deposit_instructions():
    instructions = f"""
💰 **የገንዘብ ማስቀመጫ መመሪያ፦**

1. በቴሌብር አካውንት፦ **{TELEBIRR_ACCOUNT}** ({TELEBIRR_NAME})
2. በንግድ ባንክ (CBE) አካውንት፦ **{CBE_ACCOUNT}** ({CBE_NAME})

ገንዘብ ከላኩ በኋላ የክፍያውን ማረጋገጫ (ስክሪንሾት) ወደዚህ ቦት ይላኩ። ቦቱ አረጋግጦ ባላንስዎን በራስ-ሰር ይጨምራል።
    """
    return jsonify({"instructions": instructions})

# Clean Deposit & Balance Verification (Filtering Taxi/Transfer fees)
@app.route('/api/deposit', methods=['POST'])
def process_deposit():
    data = request.json
    raw_amount = float(data.get('amount', 0))
    
    # ሎጂክ፦ የባንክ ታክሲ/የትራንስፈር ክፍያን በማስወገድ ንጹህ ገቢውን ብቻ መያዝ
    clean_amount = raw_amount
    if raw_amount > 10 and raw_amount % 10 == 1:
        clean_amount = raw_amount - 1

    return jsonify({
        "status": "success",
        "credited_amount": clean_amount,
        "account_name": CBE_NAME
    })


# ==========================================
# Frontend JavaScript Logic (ለ ሚኒ አፕ የ Low Balance ማረጋገጫ)
# ==========================================
"""
ማስታወሻ፦ ከዚህ በታች ያለው የጃቫስክሪፕት ኮድ በ mini app (index.html ወይም script.js) ውስጥ ይጨመራል፡

function selectBoard(stakeAmount, userBalance) {
    if (userBalance < stakeAmount) {
        alert("Low Balance! በቂ አካውንት የለዎትም፣ እባክዎ አካውንት ይሙሉ።");
        return false;
    }
    // ባላንስ ካለው ወደ ጨዋታው እንዲገባ ይፈቅዳል
    console.log("Game starting for stake:", stakeAmount);
    return true;
}
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
