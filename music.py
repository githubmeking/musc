import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.stream import AudioPiped
from dotenv import load_dotenv
import yt_dlp as youtube_dl

# .env dosyasını yükle
load_dotenv()

# Logger yapılandırması
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Çevresel değişkenlerden API bilgilerini al
API_ID = os.getenv('24302768')
API_HASH = os.getenv('7082b3b3331e7d12971ea9ef19e2d58b')
BOT_TOKEN = os.getenv('7565773520:AAH-vc44jhplQznKbD3q9uAmq9QAPl0PBz8')

if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("API_ID, API_HASH ve BOT_TOKEN çevresel değişkenlerinden alınamadı.")
    exit(1)

# Pyrogram istemcisini oluştur
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# PyTgCalls istemcisini oluştur
pytgcalls = PyTgCalls(app)

# YouTube'dan ses çekme fonksiyonu
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info.get('url')
    return audio_url

# /oynat komutu
@app.on_message(filters.command("oynat") & filters.group)
async def play(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Lütfen bir şarkı adı veya YouTube bağlantısı girin.")
        return
    query = " ".join(message.command[1:])
    try:
        audio_url = download_audio(query)
        if not audio_url:
            await message.reply("⚠️ Ses kaynağı bulunamadı.")
            return
        audio_stream = AudioPiped(audio_url)
        await pytgcalls.join_group_call(message.chat.id, audio_stream)
        await message.reply(f"🎶 Oynatılıyor: {query}")
        logger.info(f"Oynatılıyor: {query} in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Oynat komutu hata: {e}")
        await message.reply(f"❌ Bir hata oluştu: {e}")

# /duraklat komutu
@app.on_message(filters.command("duraklat") & filters.group)
async def pause(client, message: Message):
    try:
        await pytgcalls.pause_stream(message.chat.id)
        await message.reply("⏸️ Müzik duraklatıldı.")
        logger.info(f"Müzik duraklatıldı in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Duraklat komutu hata: {e}")
        await message.reply(f"❌ Bir hata oluştu: {e}")

# /devamet komutu
@app.on_message(filters.command("devamet") & filters.group)
async def resume(client, message: Message):
    try:
        await pytgcalls.resume_stream(message.chat.id)
        await message.reply("▶️ Müzik devam ediyor.")
        logger.info(f"Müzik devam ediyor in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Devamet komutu hata: {e}")
        await message.reply(f"❌ Bir hata oluştu: {e}")

# /durdur komutu
@app.on_message(filters.command("durdur") & filters.group)
async def stop(client, message: Message):
    try:
        await pytgcalls.leave_group_call(message.chat.id)
        await message.reply("⏹️ Müzik durduruldu ve çıkış yapıldı.")
        logger.info(f"Müzik durduruldu ve çıkış yapıldı in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Durdur komutu hata: {e}")
        await message.reply(f"❌ Bir hata oluştu: {e}")

# Botu başlat
if __name__ == "__main__":
    try:
        app.start()
        pytgcalls.start()
        logger.info("Bot çalışıyor!")
        print("Bot çalışıyor!")
        app.idle()
    except Exception as e:
        logger.critical(f"Bot başlatılamadı: {e}")
        print(f"Bot başlatılamadı: {e}")
