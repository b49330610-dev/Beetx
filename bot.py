import os
import sys
import json
import random
import threading
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

print("="*60)
print("🔥 PREMIUM EMOJI BETTING BOT STARTING...")
print("="*60)

# ============ FLASK FOR RENDER ============
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "Premium Emoji Bot is running!", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

# ============ CONFIG - ENVIRONMENT VARIABLES ============
BOT_TOKEN = os.environ.get('BOT_TOKEN', "YOUR_BOT_TOKEN_HERE")
OWNER_ID = int(os.environ.get('OWNER_ID', 8986441675))
ADMIN_IDS_FILE = "admins.json"
USERS_FILE = "users.json"

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
    """Har line ke aage aur piche premium emoji"""
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
    msg = f"""
{get_emoji_html('stars')} WELCOME {get_emoji_html('stars')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{get_emoji_html('verified')} Hello {to_fancy(user.first_name)}!
{get_emoji_html('fire')} Commands:
/dice - Roll dice
/flipcoin - Flip coin
/owner - Admin panel
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def dice_command(update, context):
    user = update.effective_user
    result = game.roll_dice()
    dice_art = {1:"⚀",2:"⚁",3:"⚂",4:"⚃",5:"⚄",6:"⚅"}
    msg = f"""
{get_emoji_html('dice')} DICE ROLLED {get_emoji_html('dice')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{get_emoji_html('eye')} Player: {to_fancy(user.first_name)}
{get_emoji_html('fire')} Result: {dice_art.get(result, '🎲')} {result}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def coin_command(update, context):
    user = update.effective_user
    result = game.flip_coin()
    emoji = "👑" if result == "Heads" else "🦅"
    msg = f"""
{get_emoji_html('money')} COIN FLIPPED {get_emoji_html('money')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{get_emoji_html('eye')} Player: {to_fancy(user.first_name)}
{get_emoji_html('money')} Result: {emoji} {result}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

async def owner_command(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    msg = f"""
{get_emoji_html('crown')} ADMIN PANEL {get_emoji_html('crown')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{get_emoji_html('fire')} Commands:
/forcedice 1-6 - Force dice
/forcecoin h/t - Force coin
/showdice - Preview dice
/showcoin - Preview coin
/users - List users
/approve ID - Add admin
/removeadmin ID - Remove admin
━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await update.message.reply_text(format_with_emojis(msg), parse_mode="HTML")

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

async def users_command(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    users = load_json(USERS_FILE, {})
    await update.message.reply_text(f"👥 Total Users: {len(users)}")

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

# ============ MAIN ============
def main():
    # Start Flask
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Bot
    application = Application.builder().token(BOT_TOKEN).build()
    
    # User commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("flipcoin", coin_command))
    
    # Admin commands
    application.add_handler(CommandHandler("owner", owner_command))
    application.add_handler(CommandHandler("forcedice", forcedice_command))
    application.add_handler(CommandHandler("forcecoin", forcecoin_command))
    application.add_handler(CommandHandler("showdice", showdice_command))
    application.add_handler(CommandHandler("showcoin", showcoin_command))
    application.add_handler(CommandHandler("users", users_command))
    
    # Owner only
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("removeadmin", removeadmin_command))
    
    print("="*60)
    print("✅ BOT STARTED SUCCESSFULLY!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📝 Admins: {get_admins()}")
    print("="*60)
    
    application.run_polling()

if __name__ == "__main__":
    main()