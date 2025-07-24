import os
import logging
import re
import random
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)
import psycopg2
from psycopg2 import sql

# Configuration
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Conversation states
NAME, SURNAME, EMAIL = range(3)

# Initialize database connection
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Create tables if not exists
def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    key_code TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

# Keys list (use exactly 100 keys from your list)
KEYS = [
    "1 J7#kL9@mN2!pQ", "xY5$fT8&zR1*wP", "qW3^bV6%nM4#sX", "8K@dH5!jL9$rF2", "pE7&mU3*zT6#qY",
    "aB4$cN8!kO2%jI", "9X#gZ5@hP1&lK3", "rS6^vD2*wF7%mQ", "3L@kY9!tR5$jH8", "bN7%mW4#qV1&pX",
    "5T#fK8@jH2!lP6", "wQ3$dM7%nB4^vZ", "7G!kX5@mN9#rT2", "yV4&pL6*zH1%qW", "2J#bR8@cK5!sF9",
    "eD6$fN3%mP7^wQ", "8H@kL1!jM4$rB5", "sX7%vZ2*wK9#pY", "4F#gT6@hQ3!lR8", "nB5$cV9%mW2^jX",
    "1K@mY7!tP4$jH6", "qZ3&wD8*zF5%rS", "6L#bN9@kM2!sV4", "dR5$fH7%nJ1^wT", "9P!gX3@mQ6#rK8",
    "yW4&pB1*zL7%vN", "3T#jR5@cK8!sF2", "eM6$dN9%mP4^qV", "7H@kL2!jX5$rB8", "sZ1%vQ6*wK3#pY",
    "5F#gT7@hR4!lN9", "nV8$cW2%mX1^jB", "2K@mY6!tP9$jH3", "qD4&wZ7*zF8%rS", "8L#bN3@kM5!sV7",
    "dH1$fR6%nJ9^wT", "4P!gX2@mQ5#rK7", "yB8&pL3*zN6%vW", "1T#jR4@cK7!sF9", "eN5$dM8%mP2^qV",
    "6H@kL9!jX3$rB7", "sQ2%vZ5*wK8#pY", "3F#gT4@hR1!lN6", "nW7$cX9%mB2^jV", "9K@mY5!tP8$jH4",
    "qZ6&wD3*zF7%rS", "5L#bN2@kM4!sV8", "dR8$fH1%nJ6^wT", "2P!gX7@mQ3#rK5", "yB4&pL9*zN1%vW",
    "7T#jR3@cK6!sF8", "eM9$dN5%mP2^qV", "4H@kL8!jX1$rB6", "sQ5%vZ2*wK7#pY", "1F#gT9@hR4!lN3",
    "nW6$cX8%mB5^jV", "8K@mY4!tP7$jH2", "qD3&wZ9*zF6%rS", "6L#bN1@kM7!sV5", "dH2$fR5%nJ8^wT",
    "3P!gX6@mQ4#rK9", "yB7&pL2*zN5%vW", "9T#jR1@cK4!sF7", "eN8$dM3%mP6^qV", "5H@kL7!jX2$rB9",
    "sQ4%vZ1*wK6#pY", "2F#gT8@hR5!lN4", "nW3$cX7%mB9^jV", "7K@mY2!tP5$jH1", "qZ8&wD4*zF9%rS",
    "4L#bN6@kM3!sV8", "dR9$fH4%nJ7^wT", "1P!gX5@mQ2#rK6", "yB3&pL8*zN7%vW", "6T#jR9@cK2!sF5",
    "eM7$dN1%mP4^qV", "3H@kL6!jX9$rB2", "sQ8%vZ3*wK5#pY", "9F#gT1@hR6!lN7", "nW4$cX2%mB8^jV",
    "5K@mY8!tP3$jH7", "qD2&wZ6*zF1%rS", "7L#bN4@kM9!sV3", "dH5$fR8%nJ2^wT", "2P!gX9@mQ7#rK4",
    "yB6&pL1*zN3%vW", "8T#jR7@cK1!sF4", "eN3$dM6%mP9^qV", "4H@kL5!jX8$rB1", "sQ7%vZ4*wK2#pY",
    "1F#gT2@hR9!lN6", "nW5$cX1%mB7^jV", "6K@mY9!tP4$jH8", "qZ7&wD5*zF2%rS", "3L#bN8@kM6!sV1",
    "dR2$fH9%nJ5^wT", "9P!gX8@mQ1#rK3", "yB1&pL7*zN4%vW", "5T#jR6@cK9!sF2", "eM4$dN7%mP3^qV"
]

# Start command
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "🚀 Welcome to Airdrop Bot!\n\n"
        "Please enter your first name:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

# Name handler
def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text("Please enter your last name:")
    return SURNAME

# Surname handler
def surname(update: Update, context: CallbackContext) -> int:
    context.user_data['surname'] = update.message.text
    update.message.reply_text("Please enter your email address:")
    return EMAIL

# Email handler and key assignment
def email(update: Update, context: CallbackContext) -> int:
    email_text = update.message.text.strip()
    
    # Simple email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email_text):
        update.message.reply_text("❌ Invalid email format. Please enter a valid email:")
        return EMAIL
    
    # Check key availability
    if not KEYS:
        update.message.reply_text("⌛ All keys have been distributed. Please check back next month!")
        return ConversationHandler.END
    
    # Get random key
    key = random.choice(KEYS)
    KEYS.remove(key)
    
    # Save to database
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (telegram_id, name, surname, email, key_code)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        update.message.from_user.id,
                        context.user_data['name'],
                        context.user_data['surname'],
                        email_text,
                        key
                    )
                )
                conn.commit()
    except psycopg2.IntegrityError:
        update.message.reply_text("⚠️ You've already participated in this airdrop!")
        return ConversationHandler.END
    
    # Send success message
    update.message.reply_text(
        f"🎉 Congratulations! Here's your unique key:\n\n"
        f"<code>{key}</code>\n\n"
        "Use this key to access your tokens.",
        parse_mode='HTML'
    )
    return ConversationHandler.END

# Cancel handler
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("❌ Operation cancelled")
    return ConversationHandler.END

# Error handler
def error(update: Update, context: CallbackContext):
    logging.error(f"Update {update} caused error {context.error}")
    update.message.reply_text("⚠️ An error occurred. Please try again later.")

# Main function
def main():
    # Initialize database
    init_db()
    
    # Create bot
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            SURNAME: [MessageHandler(Filters.text & ~Filters.command, surname)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)

    # Start bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
