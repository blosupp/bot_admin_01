from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TEST_CHANNEL_ID = int(os.getenv("TEST_CHANNEL_ID", "-1000000000000"))