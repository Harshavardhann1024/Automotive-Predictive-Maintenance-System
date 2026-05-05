import asyncio
from backend.services.email_service import send_email
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    print(f"User: {os.getenv('EMAIL_USER')}")
    success = await send_email("mayurkirankumar@gmail.com", "Test", "<h1>Test</h1>")
    print(f"Success: {success}")

if __name__ == "__main__":
    asyncio.run(main())
