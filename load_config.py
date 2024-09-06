import os
import dotenv

dotenv.load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
discord_token = os.getenv("DC_TOKEN")