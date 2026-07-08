import os
import sys
import json
import random
import threading
from datetime import datetime
from flask import Flask
from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes

print("="*60)
print("🎲 PREMIUM DICE COIN BOT STARTING...")
print("="*60)

# ============ FLASK ============
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "Dice Coin Bot is running!", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

# ============ CONFIG ============
BOT_TOKEN = os.environ.get('BOT_TOKEN', "YOUR_BOT_TOKEN_HERE")
OWNER_ID = int(os.environ.get('OWNER_ID', 7760830347))
ADMIN_IDS_FILE = "admins.json"
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
GROUP_ID = -1003920615096  # ⬅️ APNA GROUP ID DAALO

print(f"👑 Owner ID: {OWNER_ID}")

# ============ PREMIUM EMOJIS ============
PREMIUM_EMOJIS = {
    "verified": {"id": "6147565374289220368", "fallback": "✅"},
    "flex": {"id": "6147464060305676048", "fallback": "😎"},
    "blue_verification": {"id": "6147524086768604985", "fallback": "💎"},
    "frozen": {"id": "5449449325434266744", "fallback": "❄️"},
    "crying": {"id": "6273840152980755328", "fallback": "😭"},
    "smiling": {"id": "6276057176444246654", "fallback": "🙂"},
    "seeing_up": {"id": "6273997026661241933", "fallback": "😋"},
    "teeth": {"id": "6273726078649372769", "fallback": "😁"},
    "done": {"id": "6274007313107915274", "fallback": "👍"},
    "blue_badge": {"id": "5978776771623914876", "fallback": "🟫"},
    "black_badge": {"id": "5978686323907628843", "fallback": "🔸"},
    "busy_tag": {"id": "5852873584912896283", "fallback": "🟧"},
    "instagram": {"id": "5895297528106061174", "fallback": "🌐"},
    "telegram": {"id": "5895735846698487922", "fallback": "🌐"},
    "whatsapp": {"id": "5895343514320899727", "fallback": "🌐"},
    "india": {"id": "5913754823643107921", "fallback": "🇮🇳"},
    "dollar": {"id": "5197434882321567830", "fallback": "💵"},
    "top": {"id": "5463071033256848094", "fallback": "🔝"},
    "bro": {"id": "5463256910851546817", "fallback": "🤝"},
    "yes": {"id": "5463423955014529788", "fallback": "👌"},
    "lock": {"id": "5465443379917629504", "fallback": "🔓"},
    "good": {"id": "5465465194056525619", "fallback": "👍"},
    "sigma": {"id": "6235620067942341623", "fallback": "🥃"},
    "don": {"id": "6235717714023814969", "fallback": "🍂"},
    "skills": {"id": "6235593671073339928", "fallback": "💀"},
    "heart": {"id": "6147617184479711380", "fallback": "❤️‍🔥"},
    "stars": {"id": "6235403472741603087", "fallback": "⭐"},
    "github": {"id": "5346181118884331907", "fallback": "📱"},
    "motion": {"id": "5971944878815317190", "fallback": "💠"},
}

def get_emoji_html(name):
    if name in PREMIUM_EMOJIS:
        data = PREMIUM_EMOJIS[name]
        return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>'
    return "⭐"

def get_random_emoji():
    names = list(PREMIUM_EMOJIS.keys())
    if names:
        name = random.choice(names)
        data = PREMIUM_EMOJIS[name]
        return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>'
    return "⭐"

def format_with_emojis(text):
    lines = text.split('\n')
    formatted = []
    for line in lines:
        if line.strip():
            left = get_random_emoji()
            right = get_random_emoji()
            formatted.append(f"{left} {line} {right}")
        else:
            formatted.append(line)
    return '\n'.join(formatted)

def to_fancy(text):
    fancy_map = {
        'A':'𝘼','B':'𝘽','C':'𝘾','D':'𝘿','E':'𝙀','F':'𝙁','G':'𝙂','H':'𝙃',
        'I':'𝙄','J':'𝙅','K':'𝙆','L':'𝙇','M':'𝙈','N':'𝙉','O':'𝙊','P':'𝙋',
        'Q':'𝙌','R':'𝙍','S':'𝙎','T':'𝙏','U':'𝙐','V':'𝙑','W':'𝙒','X':'𝙓',
        'Y':'𝙔','Z':'𝙕','a':'𝙖','b':'𝙗','c':'𝙘','d':'𝙙','e':'𝙚','f':'𝙛',
        'g':'𝙜','h':'𝙝','i':'𝙞','j':'𝙟','k':'𝙠','l':'𝙡','m':'𝙢','n':'𝙣',
        'o':'𝙤','p':'𝙥','q':'𝙦','r':'𝙧','s':'𝙨','t':'𝙩','u':'𝙪','v':'𝙫',
        'w':'𝙬','x':'𝙭','y':'𝙮','z':'𝙯','0':'𝟎','1':'𝟏','2':'𝟐','3':'𝟑',
        '4':'𝟒','5':'𝟓','6':'𝟔','7':'𝟕','8':'𝟖','9':'𝟗'
    }
    return ''.join(fancy_map.get(c, c) for c in text)

# ============ DATABASE ============
def load_json(filename, default=None):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default or {}
    return default or {}

def save_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

# ============ ADMINS ============
def get_admins():
    data = load_json(ADMIN_IDS_FILE, [])
    if not isinstance(data, list):
        data = []
    if OWNER_ID not in data:
        data.append(OWNER_ID)
        save_json(ADMIN_IDS_FILE, data)
    return data

def is_admin(user_id):
    return user_id in get_admins()

def add_admin(user_id):
    admins = get_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_json(ADMIN_IDS_FILE, admins)
        return True
    return False

def remove_admin(user_id):
    admins = get_admins()
    if user_id in admins and user_id != OWNER_ID:
        admins.remove(user_id)
        save_json(ADMIN_IDS_FILE, admins)
        return True
    return False

# ============ BANNED ============
def is_banned(user_id):
    banned = load_json(BANNED_FILE, [])
    if not isinstance(banned, list):
        return False
    return str(user_id) in banned

def ban_user(user_id):
    banned = load_json(BANNED_FILE, [])
    if not isinstance(banned, list):
        banned = []
    if str(user_id) not in banned:
        banned.append(str(user_id))
        save_json(BANNED_FILE, banned)
        return True
    return False

def unban_user(user_id):
    banned = load_json(BANNED_FILE, [])
    if not isinstance(banned, list):
        banned = []
    if str(user_id) in banned:
        banned.remove(str(user_id))
        save_json(BANNED_FILE, banned)
        return True
    return False

# ============ USERS ============
def register_user(user_id, username, first_name):
    users = load_json(USERS_FILE, {})
    if not isinstance(users, dict):
        users = {}
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "username": username,
            "name": first_name,
            "joined": str(datetime.now()),
            "dice_rolls": 0,
            "coin_flips": 0
        }
        save_json(USERS_FILE, users)
        return True
    return False

def update_user_stats(user_id, game_type):
    users = load_json(USERS_FILE, {})
    if not isinstance(users, dict):
        return
    uid = str(user_id)
    if uid in users:
        if game_type == "dice":
            users[uid]["dice_rolls"] = users[uid].get("dice_rolls", 0) + 1
        elif game_type == "coin":
            users[uid]["coin_flips"] = users[uid].get("coin_flips", 0) + 1
        save_json(USERS_FILE, users)

def get_all_users():
    data = load_json(USERS_FILE, {})
    if not isinstance(data, dict):
        return {}
    return data

# ============ GROUP ADMIN CHECK ============
async def is_group_admin(context, user_id, chat_id):
    """Check if user is admin in the group"""
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False

# ============ GAME ============
class DiceGame:
    def __init__(self):
        self.next_dice = None
        self.next_coin = None
    
    def roll_dice(self):
        if self.next_dice:
            result = self.next_dice
            self.next_dice = None
            return result
        return random.randint(1, 6)
    
    def flip_coin(self):
        if self.next_coin:
            result = self.next_coin
            self.next_coin = None
            return result
        return random.choice(["Heads", "Tails"])
    
    def set_dice(self, n):
        self.next_dice = n
    
    def set_coin(self, c):
        self.next_coin = c

game = DiceGame()

# ============ COMMANDS ============

async def start_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    first_name = user.first_name or "User"
    
    register_user(user_id, username, first_name)
    
    if is_banned(user_id):
        await update.message.reply_text("🚫 You are banned!")
        return
    
    msg = f"""
{get_emoji_html('stars')} WELCOME {get_emoji_html('stars')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{get_emoji_html('verified')} Hello {to_fancy(first_name)}!

{get_emoji_html('fire')} Commands:
/dice - Roll dice (Group Admins only)
/flipcoin - Flip coin (Group Admins only)
/owner - Admin panel
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def dice_command(update, context):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id
    
    # Check if user is group admin
    if not await is_group_admin(context, user_id, chat_id):
        await update.message.reply_text(
            f"{get_emoji_html('angry')} Only group admins can roll dice!"
        )
        return
    
    if is_banned(user_id):
        await update.message.reply_text("🚫 You are banned!")
        return
    
    result = game.roll_dice()
    dice_art = {1:"⚀",2:"⚁",3:"⚂",4:"⚃",5:"⚄",6:"⚅"}
    
    update_user_stats(user_id, "dice")
    
    msg = f"""
{get_emoji_html('dice')} DICE ROLLED {get_emoji_html('dice')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{get_emoji_html('eye')} Admin: {to_fancy(user.first_name)}
{get_emoji_html('fire')} Result: {dice_art.get(result, '🎲')} {result}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def coin_command(update, context):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id
    
    # Check if user is group admin
    if not await is_group_admin(context, user_id, chat_id):
        await update.message.reply_text(
            f"{get_emoji_html('angry')} Only group admins can flip coin!"
        )
        return
    
    if is_banned(user_id):
        await update.message.reply_text("🚫 You are banned!")
        return
    
    result = game.flip_coin()
    emoji = "👑" if result == "Heads" else "🦅"
    
    update_user_stats(user_id, "coin")
    
    msg = f"""
{get_emoji_html('money')} COIN FLIPPED {get_emoji_html('money')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{get_emoji_html('eye')} Admin: {to_fancy(user.first_name)}
{get_emoji_html('money')} Result: {emoji} {result}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def owner_command(update, context):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    users = get_all_users()
    total_users = len(users)
    
    msg = f"""
{get_emoji_html('crown')} OWNER PANEL {get_emoji_html('crown')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 Owner ID: {OWNER_ID}
👥 Total Users: {total_users}

📊 Commands:
/users - List all users
/approve ID - Add admin
/removeadmin ID - Remove admin
/ban ID - Ban user
/unban ID - Unban user
/forcedice 1-6 - Force dice
/forcecoin h/t - Force coin
/showdice - Preview dice
/showcoin - Preview coin
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def users_command(update, context):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    users = get_all_users()
    
    if not users:
        await update.message.reply_text("No users yet!")
        return
    
    msg = f"👥 TOTAL USERS: {len(users)}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for uid, data in list(users.items())[:20]:
        status = "🚫 BANNED" if is_banned(int(uid)) else "✅ ACTIVE"
        uname = data.get('username', 'Unknown')
        dice = data.get('dice_rolls', 0)
        coin = data.get('coin_flips', 0)
        msg += f"ID: {uid} | @{uname}\n"
        msg += f"🎲 {dice} | 🪙 {coin} | {status}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if len(users) > 20:
        msg += f"\n... and {len(users)-20} more"
    
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def approve_command(update, context):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only bot owner can approve!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /approve USER_ID")
        return
    
    try:
        new_admin = int(context.args[0])
        if add_admin(new_admin):
            await update.message.reply_text(f"✅ User {new_admin} approved as admin!")
        else:
            await update.message.reply_text(f"⚠️ User {new_admin} already admin!")
    except:
        await update.message.reply_text("❌ Invalid user ID!")

async def removeadmin_command(update, context):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only bot owner can remove admins!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /removeadmin USER_ID")
        return
    
    try:
        admin_id = int(context.args[0])
        if remove_admin(admin_id):
            await update.message.reply_text(f"✅ Admin {admin_id} removed!")
        else:
            await update.message.reply_text(f"⚠️ Cannot remove {admin_id}")
    except:
        await update.message.reply_text("❌ Invalid user ID!")

async def ban_command(update, context):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban USER_ID")
        return
    
    try:
        target_id = int(context.args[0])
        if target_id == OWNER_ID:
            await update.message.reply_text("❌ Cannot ban owner!")
            return
        if ban_user(target_id):
            await update.message.reply_text(f"✅ User {target_id} banned!")
        else:
            await update.message.reply_text(f"⚠️ User {target_id} already banned!")
    except:
        await update.message.reply_text("❌ Invalid user ID!")

async def unban_command(update, context):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban USER_ID")
        return
    
    try:
        target_id = int(context.args[0])
        if unban_user(target_id):
            await update.message.reply_text(f"✅ User {target_id} unbanned!")
        else:
            await update.message.reply_text(f"⚠️ User {target_id} not banned!")
    except:
        await update.message.reply_text("❌ Invalid user ID!")

async def forcedice_command(update, context):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /forcedice 1-6")
        return
    
    try:
        n = int(context.args[0])
        if n < 1 or n > 6:
            raise ValueError
        game.set_dice(n)
        await update.message.reply_text(f"✅ Next dice forced to: {n}")
    except:
        await update.message.reply_text("❌ Enter number 1-6")

async def forcecoin_command(update, context):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /forcecoin h/t")
        return
    
    s = context.args[0].lower()
    if s in ['h', 'head', 'heads']:
        game.set_coin("Heads")
        await update.message.reply_text("✅ Next coin forced to: Heads")
    elif s in ['t', 'tail', 'tails']:
        game.set_coin("Tails")
        await update.message.reply_text("✅ Next coin forced to: Tails")
    else:
        await update.message.reply_text("❌ Use 'h' or 't'")

async def showdice_command(update, context):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    n = game.next_dice if game.next_dice else random.randint(1, 6)
    await update.message.reply_text(f"🎲 Next dice: {n}")

async def showcoin_command(update, context):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    c = game.next_coin if game.next_coin else random.choice(["Heads", "Tails"])
    await update.message.reply_text(f"🪙 Next coin: {c}")

# ============ MAIN ============
def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("flipcoin", coin_command))
    
    # Admin commands
    application.add_handler(CommandHandler("owner", owner_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("forcedice", forcedice_command))
    application.add_handler(CommandHandler("forcecoin", forcecoin_command))
    application.add_handler(CommandHandler("showdice", showdice_command))
    application.add_handler(CommandHandler("showcoin", showcoin_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    
    # Owner only
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("removeadmin", removeadmin_command))
    
    print("="*60)
    print("✅ BOT STARTED SUCCESSFULLY!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📝 Admins: {get_admins()}")
    print(f"📋 Group ID: {GROUP_ID}")
    print("="*60)
    
    application.run_polling()

if __name__ == "__main__":
    main()
