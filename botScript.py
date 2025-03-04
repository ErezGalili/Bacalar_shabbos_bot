import logging
import asyncio
import aiohttp
import certifi
import ssl
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# טוקן של הבוט מטלגרם
# כאן שמים את שורת הטוקן
# קוד העיר של בקאלר, מקסיקו
GEONAME_ID = 3530597

# הפעלת הלוגים
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_shabbat_times():
    """פונקציה ששולפת זמני שבת מ-Hebcal"""
    try:
        # Method 1: Using certifi for SSL certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        url = f"https://www.hebcal.com/shabbat?cfg=json&geo=pos&latitude=18.6813&longitude=-88.3910&tzid=America/Cancun&M=on"
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Initialize the response text
                times = "🕯️ זמני שבת בבקאלר, מקסיקו:\n\n"
                
                # Add parasha information
                parasha = next((item for item in data["items"] if item["category"] == "parashat"), None)
                if parasha:
                    times += f"📖 {parasha['hebrew']}\n"
                    times += f"   {parasha['title']}\n\n"
                
                # Add special Shabbat if exists
                special_shabbat = next((item for item in data["items"] if item["category"] == "holiday" and item["subcat"] == "shabbat"), None)
                if special_shabbat:
                    times += f"✨ {special_shabbat['hebrew']}\n"
                    times += f"   {special_shabbat['title']}\n\n"
                
                # Add candle lighting and havdalah times
                for item in data["items"]:
                    if item["category"] == "candles":
                        date_str = item['date'].split('T')[1][:5]
                        times += f"🕯️ {item['hebrew']}: {date_str}\n"
                    elif item["category"] == "havdalah":
                        date_str = item['date'].split('T')[1][:5]
                        times += f"✨ {item['hebrew']}: {date_str}\n"
                
                return times
    except Exception as e:
        logger.error(f"Error fetching Shabbat times: {e}")
        # Try alternative method if the first fails
        try:
            logger.info("Trying alternative method with disabled verification...")
            # Method 2: Disable SSL verification entirely as fallback
            conn = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=conn) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # The same processing as above
                    times = "🕯️ זמני שבת בבקאלר, מקסיקו:\n\n"
                    
                    parasha = next((item for item in data["items"] if item["category"] == "parashat"), None)
                    if parasha:
                        times += f"📖 {parasha['hebrew']}\n"
                        times += f"   {parasha['title']}\n\n"
                    
                    special_shabbat = next((item for item in data["items"] if item["category"] == "holiday" and item["subcat"] == "shabbat"), None)
                    if special_shabbat:
                        times += f"✨ {special_shabbat['hebrew']}\n"
                        times += f"   {special_shabbat['title']}\n\n"
                    
                    for item in data["items"]:
                        if item["category"] == "candles":
                            date_str = item['date'].split('T')[1][:5]
                            times += f"🕯️ {item['hebrew']}: {date_str}\n"
                        elif item["category"] == "havdalah":
                            date_str = item['date'].split('T')[1][:5]
                            times += f"✨ {item['hebrew']}: {date_str}\n"
                    
                    return times
        except Exception as e2:
            logger.error(f"Alternative method also failed: {e2}")
            return "מצטער, לא הצלחתי לקבל את זמני השבת כרגע."

async def shabbat(update: Update, context: CallbackContext) -> None:
    """פקודה שמחזירה את זמני השבת"""
    times = await get_shabbat_times()
    await update.message.reply_text(times)

async def start(update: Update, context: CallbackContext) -> None:
    """פקודת התחלה שמסבירה את השימוש בבוט"""
    await update.message.reply_text("שלום! שלח /shabbat כדי לקבל את זמני השבת בבקאלר, מקסיקו.")

def main() -> None:
    """Start the bot."""
    # Initialize the application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("shabbat", shabbat))
    
    # Start the bot
    logger.info("הבוט פועל...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()