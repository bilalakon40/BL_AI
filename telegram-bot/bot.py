import os
import httpx
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
API_URL = os.environ.get('API_URL', 'http://api:8000')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', '')

API_BASE = f'{API_URL}/api'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🤖 AI Trading Bot\n\n'
        'Commands:\n'
        '/status - System status\n'
        '/kill - Emergency stop\n'
        '/balance - Account balance\n'
        '/agents - List agents\n'
        '/unlock <password> - Unlock system'
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_CHAT_ID:
        await update.message.reply_text('Unauthorized')
        return
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{API_BASE}/orchestrator/state')
        data = resp.json()
    await update.message.reply_text(
        f'Status: {"🟢 Running" if data["is_running"] else "🔴 Stopped"}\n'
        f'Locked: {"🔒 Yes" if data["is_locked"] else "🔓 No"}\n'
        f'Reason: {data["lock_reason"] or "None"}\n'
        f'Active Agents: {data["active_agents"]}/{data["total_agents"]}\n'
        f'Markets: {", ".join(data["market_symbols"])}'
    )


async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_CHAT_ID:
        await update.message.reply_text('Unauthorized')
        return
    async with httpx.AsyncClient() as client:
        resp = await client.post(f'{API_BASE}/orchestrator/stop')
        data = resp.json()
    await update.message.reply_text(f'🛑 {data["message"]}')
    await update.message.reply_text('All orders cancelled. System locked.')


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_CHAT_ID:
        await update.message.reply_text('Unauthorized')
        return
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{API_BASE}/balance')
        data = resp.json()
    await update.message.reply_text(
        f'Balance: {data["free"]:.2f} {data["asset"]}\n'
        f'Total: {data["total"]:.2f} {data["asset"]}'
    )


async def agents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_CHAT_ID:
        await update.message.reply_text('Unauthorized')
        return
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{API_BASE}/agents')
        data = resp.json()
    msg = 'Agents:\n'
    for a in data:
        status_icon = '🟢' if a['is_active'] else '🔴'
        perf = a['performance']
        msg += f'{status_icon} {a["agent_id"]} ({a["strategy"]})\n'
        msg += f'   Trades: {perf["trades"]} | Win Rate: {perf["win_rate"]:.1%} | PnL: {perf["total_pnl"]:.2f}\n'
    await update.message.reply_text(msg)


async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_CHAT_ID:
        await update.message.reply_text('Unauthorized')
        return
    if not context.args:
        await update.message.reply_text('Usage: /unlock <password>')
        return
    async with httpx.AsyncClient() as client:
        resp = await client.post(f'{API_BASE}/risk/unlock', json={'password': context.args[0]})
        if resp.status_code == 200:
            await update.message.reply_text('✅ System unlocked')
        else:
            await update.message.reply_text('❌ Invalid password')


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(CommandHandler('kill', kill))
    app.add_handler(CommandHandler('balance', balance))
    app.add_handler(CommandHandler('agents', agents))
    app.add_handler(CommandHandler('unlock', unlock))

    print('Telegram bot started')
    app.run_polling()


if __name__ == '__main__':
    main()
