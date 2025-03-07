import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Application, ContextTypes
from app.models import User
from fastapi import Depends
from dotenv import load_dotenv

from app.database import get_session
from app.dependency_injection import Depends, inject_dependencies
load_dotenv()
# Replace 'YOUR_API_TOKEN' with your actual bot token from BotFather
API_TOKEN = os.getenv("API_TOKEN")


async def show_option_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='button_1')],
        [InlineKeyboardButton("Option 2", callback_data='button_2')],
        [InlineKeyboardButton("Option 3", callback_data='button_3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)

@inject_dependencies
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, db: AsyncSession = Depends(get_session)) -> None:
    print(update.effective_user)
    
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()
    print(users)
    await update.message.reply_text("Welcome to the Simple Telegram Bot!")
    await show_option_buttons(update, context)

async def button_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f'You selected option: {query.data.split("_")[1]}')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'I can respond to the following commands:\n/start - Start the bot\n/help - Get help information'
    )

def main():
    application = Application.builder().token(API_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button_selection_handler, pattern='^button_'))
    application.run_polling()

if __name__ == '__main__':
    main()