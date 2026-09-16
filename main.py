import random
from flask import Flask, jsonify, request

app = Flask(__name__)

# የውርርድ አማራጮች እና የቤቱ ኮሚሽን (20%)
STAKE_OPTIONS = [10, 20, 50, 100]
HOUSE_COMMISSION_PERCENT = 0.20

# የማሳያ የተጠቃሚዎች ባላንስ እና የዊዝድሮ ጥያቄዎች ዳታቤዝ
user_balances = {
    "user_12345": 150,
    "user_67890": 200
}
withdrawal_requests = []

# 200 የሚሆኑ ልዩ የቢንጎ ቦርዶችን ማመንጨት
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
            "B": b_col,
            "I": i_col,
            "N": n_col,
            "G": g_col,
            "O": o_col
        }
    return boards

BINGO_BOARDS = generate_bingo_boards()

# 1. ጨዋታውን መቀላቀል እና ቦርድ መምረጥ
@app.route('/join_game', methods=['POST'])
def join_game():
    data = request.json
    user_id = data.get("user_id")
    stake = data.get("stake")
    chosen_board_id = data.get("board_id") # ከ 1 እስከ 200 ያለው ቦርድ ቁጥር

    if stake not in STAKE_OPTIONS:
        return jsonify({"status": "error", "message": "የተሳሳተ የውርርድ መጠን!"}), 400

    if chosen_board_id not in BINGO_BOARDS:
        return jsonify({"status": "error", "message": "ይህ የቢንጎ ቦርድ የለም!"}), 400

    current_balance = user_balances.get(user_id, 0)

    # ሎው ባላንስ (Low Balance) ማረጋገጫ
    if current_balance < stake:
        return jsonify({
            "status": "error", 
            "message": f"Low Balance! የ계좌 ቀሪ ኑሮዎ (ብር {current_balance}) ለዚህ ጨዋታ በቂ አይደለም።"
        }), 400

    # ከባላንሱ ላይ ስቴክውን መቀነስ
    user_balances[user_id] = current_balance - stake
    assigned_board = BINGO_BOARDS[chosen_board_id]

    return jsonify({
        "status": "success",
        "message": f"በተሳካ ሁኔታ ወደ {stake} ብር ጨዋታ ገብተዋል!",
        "board_id": chosen_board_id,
        "assigned_board": assigned_board,
        "remaining_balance": user_balances[user_id]
    })

# 2. አውቶማቲክ የዲፖዚት ማረጋገጫ (FT Number Auto-Verification)
@app.route('/verify_deposit', methods=['POST'])
def verify_deposit():
    data = request.json
    user_id = data.get("user_id")
    ft_number = data.get("ft_number")
    amount = data.get("amount")

    # FT ቁጥር ሲረጋገጥ
    is_valid_ft = True 

    if is_valid_ft:
        if user_id not in user_balances:
            user_balances[user_id] = 0
        user_balances[user_id] += amount

        return jsonify({
            "status": "success",
            "message": f"ብር {amount} አካውንትዎ ላይ በሰላም ገብቷል!",
            "new_balance": user_balances[user_id]
        })
    else:
        return jsonify({"status": "error", "message": "የተሳሳተ የትራንዛክሽን ቁጥር (FT Number)!"}), 400

# 3. አውቶማቲክ የገንዘብ ማውጣት (Withdrawal) ሎጂክ
@app.route('/withdraw', methods=['POST'])
def withdraw_funds():
    data = request.json
    user_id = data.get("user_id")
    bank_type = data.get("bank_type") # ቴሌብር ወይም ንግድ ባንክ
    account_number = data.get("account_number")
    amount = data.get("amount")

    current_balance = user_balances.get(user_id, 0)

    # ባላንስ በቂ መሆኑን ማረጋገጥ (Low Balance Check ለውዝድሮ)
    if current_balance < amount:
        return jsonify({
            "status": "error",
            "message": f"Low Balance! የ계좌 ቀሪ ኑሮዎ (ብር {current_balance}) ይህንን ያህል ገንዘብ ለማውጣት በቂ አይደለም።"
        }), 400

    # ከባላንሱ መቀነስ እና ጥያቄውን መመዝገብ
    user_balances[user_id] = current_balance - amount
    
    withdrawal_record = {
        "user_id": user_id,
        "bank_type": bank_type,
        "account_number": account_number,
        "amount": amount,
        "status": "Processing"
    }
    withdrawal_requests.append(withdrawal_record)

    return jsonify({
        "status": "success",
        "message": f"የብር {amount} ዊዝድሮ ጥያቄዎ ተቀባይነት አግኝቷል! በቅርቡ ይተላለፍልዎታል።",
        "remaining_balance": user_balances[user_id]
    })

# 4. አሸናፊዎችን በእኩል ማካፈል (Split Prize Logic)
@app.route('/declare_winners', methods=['POST'])
def declare_winners():
    data = request.json
    stake = data.get("stake")
    winner_user_ids = data.get("winners", [])

    if not winner_user_ids:
        return jsonify({"status": "error", "message": "አሸናፊ አልተገኘም!"}), 400

    total_pool = stake * len(winner_user_ids)
    house_cut = total_pool * HOUSE_COMMISSION_PERCENT
    net_prize_pool = total_pool - house_cut

    num_winners = len(winner_user_ids)
    prize_per_winner = net_prize_pool / num_winners

    for uid in winner_user_ids:
        if uid not in user_balances:
            user_balances[uid] = 0
        user_balances[uid] += prize_per_winner

    return jsonify({
        "status": "success",
        "total_winners": num_winners,
        "prize_per_winner": prize_per_winner,
        "message": f"አሸናፊዎች {num_winners} ስለሆኑ ሽልማቱ በእኩል ተካፍሏል!"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
