import os
from telegram import Bot
from telegram.error import TelegramError

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = Bot(token=self.bot_token) if self.bot_token and self.chat_id else None

    async def send_alert(self, trends):
        if not self.bot or not trends:
            return

        message = "🚨 *HIGH-SCORE TRENDS* 🚨\n\n"
        for trend in trends:
            strategy = trend.get('strategy', 'N/A')
            message += (
                f"📈 *{trend['keyword']}*\n"
                f"   Score: {trend['monetization_score']}/10\n"
                f"   Velocity: {trend['velocity']:.0f}\n"
                f"   Source: {trend['source']}\n"
                f"   Strategy: `{strategy}`\n\n"
            )
        message += f"⏰ {trends[0]['detected_at']}"

        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')
            print(f"Sent alert for {len(trends)} trends")
        except TelegramError as e:
            print(f"Telegram error: {e}")
