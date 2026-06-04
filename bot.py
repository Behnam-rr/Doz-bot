import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

def create_board():
    return [" "] * 9

def render_board(board):
    keyboard = []
    for i in range(0, 9, 3):
        row = [InlineKeyboardButton(board[i+j] if board[i+j] != " " else "⬜", callback_data=str(i+j)) for j in range(3)]
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def check_winner(board):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != " ":
            return board[a]
    return None

def bot_move(board):
    empty = [i for i, x in enumerate(board) if x == " "]
    return random.choice(empty)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["board"] = create_board()
    await update.message.reply_text("بازی دوز! تو ❌ هستی", reply_markup=render_board(context.user_data["board"]))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    board = context.user_data.get("board")
    if not board:
        await query.edit_message_text("برای شروع /start بزن")
        return
    idx = int(query.data)
    if board[idx] != " ":
        return
    board[idx] = "❌"
    winner = check_winner(board)
    if winner:
        await query.edit_message_text("🎉 تو بردی!", reply_markup=render_board(board))
        context.user_data["board"] = None
        return
    if " " not in board:
        await query.edit_message_text("مساوی شد!", reply_markup=render_board(board))
        context.user_data["board"] = None
        return
    move = bot_move(board)
    board[move] = "⭕"
    winner = check_winner(board)
    if winner:
        await query.edit_message_text("🤖 ربات برد!", reply_markup=render_board(board))
        context.user_data["board"] = None
        return
    if " " not in board:
        await query.edit_message_text("مساوی شد!", reply_markup=render_board(board))
        context.user_data["board"] = None
        return
    await query.edit_message_reply_markup(reply_markup=render_board(board))

TOKEN = os.environ["TOKEN"]
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
