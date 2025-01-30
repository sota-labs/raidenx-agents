import asyncio
import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

class TelegramMessenger:
    def __init__(self):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.group_id = int(os.getenv("GROUP_ID"))
        self.session_name = 'bot_session'
        
    async def send_message(self, message: str) -> None:
        """
        Gửi tin nhắn đến Telegram group
        
        Args:
            message (str): Nội dung tin nhắn cần gửi
        """
        try:
            async with TelegramClient(self.session_name, self.api_id, self.api_hash) as client:
                await client.connect()
                await client.send_message(self.group_id, message)
        except TimeoutError:
            print("Gửi tin nhắn bị timeout, thử lại sau 5 giây...")
            await asyncio.sleep(5)
            async with TelegramClient(self.session_name, self.api_id, self.api_hash) as client:
                await client.connect()
                await client.send_message(self.group_id, message)
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn: {str(e)}")

# async def main():
#     messenger = TelegramMessenger()
#     await messenger.send_message("test bot")

# if __name__ == "__main__":
#     asyncio.run(main())