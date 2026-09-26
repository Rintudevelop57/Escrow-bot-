import logging
import sqlite3
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Owner IDs (Aapne jo edit ki hain)
OWNER_IDS = [8815891603, 8626677676]

# Database Initialization
def init_db():
    conn = sqlite3.connect('escrow_deals.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            amount REAL
        )
    ''')
    conn.commit()
    conn.close()

# Deal Add Command: Sirf Owner/Admin use kar sakta hai
async def add_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Security Check: Agar user Owner nahi hai toh reject kar do
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ Sirf Bot Owner hi deals add kar sakta hai!")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /adddeal @username <amount>")
        return

    raw_user = context.args[0].replace("@", "").lower()
    try:
        amount = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Valid amount likhein.")
        return

    conn = sqlite3.connect('escrow_deals.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO deals (user_id, username, amount) VALUES (?, ?, ?)",
        (None, raw_user, amount)
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Successful Deal Added!\nUser: @{raw_user}\nAmount: ₹{amount}")

# Stats Command: Anyone can check stats
async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        target_user = context.args[0].replace("@", "").lower()
    elif update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user.username
        if target_user:
            target_user = target_user.lower()
        else:
            await update.message.reply_text("❌ Is user ka username nahi hai.")
            return
    else:
        await update.message.reply_text("❌ Usage: /stats @username ya message ko reply karein.")
        return

    conn = sqlite3.connect('escrow_deals.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*), SUM(amount) FROM deals WHERE username = ?",
        (target_user,)
    )
    result = cursor.fetchone()
    conn.close()

    total_deals = result[0] if result[0] else 0
    total_amount = result[1] if result[1] else 0.0

    msg = (
        f"📊 Escrow Stats for @{target_user}\n\n"
        f"🔄 Total Deals: {total_deals}\n"
        f"💰 Total Volume: ₹{total_amount:.2f}"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

# Main Function
def main():
    init_db()
    
    # BotFather Token
    TOKEN = "8750941343:AAGC-LYWPdzwFeckpfwfl3-jDavwN0_Fv_E"
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("adddeal", add_deal))
    app.add_handler(CommandHandler("stats", get_stats))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
  
