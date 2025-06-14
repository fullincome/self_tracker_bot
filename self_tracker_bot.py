import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from todoist_api import TodoistAPI
from yougile_api import YougileAPI
import io
import requests
# Импортируем класс YandexGPT
from yandex_gpt import YandexGPT

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TODOIST_TOKEN = os.getenv('TODOIST_TOKEN')
YANDEX_SPEECHKIT_TOKEN = os.getenv('YANDEX_SPEECHKIT_TOKEN')
YOUGILE_TOKEN = os.getenv('YOUGILE_TOKEN')
YANDEX_GPT_APIKEY = os.getenv('YANDEX_GPT_APIKEY')
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')
ALLOWED_USER_ID = int(os.getenv('TELEGRAM_USER_ID', '0'))  # ID пользователя, которому разрешен доступ

# Получаем сервис из переменной окружения или по наличию токена
SERVICE = os.getenv('SERVICE', 'todoist')

if not TELEGRAM_TOKEN or not YANDEX_SPEECHKIT_TOKEN:
    raise ValueError("TELEGRAM_TOKEN and YANDEX_SPEECHKIT_TOKEN must be set in environment variables")
if SERVICE == 'todoist' and not TODOIST_TOKEN:
    raise ValueError("TODOIST_TOKEN must be set in environment variables for todoist mode")
if SERVICE == 'yougile' and not YOUGILE_TOKEN:
    raise ValueError("YOUGILE_TOKEN must be set in environment variables for yougile mode")

if ALLOWED_USER_ID == 0:
    raise ValueError("TELEGRAM_USER_ID must be set in environment variables")

# Инициализируем клиента только для выбранного сервиса
client = None
gpt = None
if SERVICE == 'todoist':
    if not TODOIST_TOKEN:
        raise ValueError("TODOIST_TOKEN must be set in environment variables for todoist mode")
    client = TodoistAPI(TODOIST_TOKEN)
elif SERVICE == 'yougile':
    if not YOUGILE_TOKEN:
        raise ValueError("YOUGILE_TOKEN must be set in environment variables for yougile mode")
    yougile_location = os.getenv('YOUGILE_LOCATION')
    if not yougile_location:
        raise ValueError("YOUGILE_LOCATION must be set in environment variables for yougile mode")
    client = YougileAPI(YOUGILE_TOKEN, location=yougile_location)
else:
    raise ValueError("Unknown SERVICE value. Must be 'todoist' or 'yougile'.")

# Инициализируем YandexGPT для любого сервиса
if not YANDEX_GPT_APIKEY or not YANDEX_FOLDER_ID:
    raise ValueError("YANDEX_GPT_APIKEY и YANDEX_FOLDER_ID должны быть заданы в переменных окружения для работы с LLM")
gpt = YandexGPT(YANDEX_GPT_APIKEY, YANDEX_FOLDER_ID)

def recognize_speech_yandex(audio_path, api_key, folder_id, lang="ru-RU"):
    """
    Распознаёт речь с помощью Yandex SpeechKit REST API.
    :param audio_path: путь к аудиофайлу (ogg, wav, mp3 и др.)
    :param api_key: API-ключ Yandex Cloud
    :param folder_id: folder_id Yandex Cloud
    :param lang: язык (по умолчанию ru-RU)
    :return: распознанный текст или None
    """
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/octet-stream",
    }
    params = {
        "folderId": folder_id,
        "lang": lang
    }
    url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    response = requests.post(url, headers=headers, params=params, data=audio_data)
    result = response.json()
    if result.get("result"):
        return result["result"]
    else:
        print("Ошибка распознавания:", result)
        return None

async def check_user(update: Update) -> bool:
    """Проверяет, разрешен ли доступ пользователю"""
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔️ У вас нет доступа к этому боту.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    if not await check_user(update):
        return
    if SERVICE == 'todoist':
        await update.message.reply_text(
            "Привет! Я бот для создания задач в Todoist.\n"
            "Просто отправь мне текст или голосовое сообщение, и я создам из него задачу."
        )
    elif SERVICE == 'yougile':
        await update.message.reply_text(
            "Привет! Я бот для создания задач в Yougile.\n"
            "Просто отправь мне текст или голосовое сообщение, и я создам из него задачу."
        )
    else:
        await update.message.reply_text("❌ Сервис не настроен. Обратитесь к администратору.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    if not await check_user(update):
        return
    
    await update.message.reply_text(
        "Я могу создавать задачи в Todoist из:\n"
        "- Текстовых сообщений\n"
        "- Голосовых сообщений\n\n"
        "Просто отправь мне сообщение, и я создам задачу."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    if not await check_user(update):
        return
    text = update.message.text.strip()
    if SERVICE == 'todoist':
        # Извлекаем параметры задачи через LLM
        params = gpt.extract_todoist_task_params(text)
        task = client.create_task(**params)
        await update.message.reply_text(f"✅ Задача создана: {task['content']}")
    elif SERVICE == 'yougile':
        params = gpt.extract_yougile_task_params(text)
        task = client.create_task(**params)
        await update.message.reply_text(f"✅ Задача создана в Yougile: {params.get('title', text)}")
    else:
        await update.message.reply_text("❌ Сервис не настроен. Обратитесь к администратору.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений"""
    if not await check_user(update):
        return
    try:
        # Получаем голосовое сообщение
        voice = await update.message.voice.get_file()
        # Скачиваем файл
        voice_ogg = io.BytesIO()
        await voice.download_to_memory(voice_ogg)
        voice_ogg.seek(0)
        # Сохраняем временный файл
        temp_file = "temp_voice.ogg"
        with open(temp_file, "wb") as f:
            f.write(voice_ogg.getvalue())
        # Распознаём речь через REST API
        text = recognize_speech_yandex(temp_file, YANDEX_SPEECHKIT_TOKEN, YANDEX_FOLDER_ID)
        # Удаляем временный файл
        os.remove(temp_file)
        if not text:
            raise ValueError("Не удалось распознать речь")
        if SERVICE == 'todoist':
            params = gpt.extract_todoist_task_params(text)
            task = client.create_task(**params)
            await update.message.reply_text(f"✅ Задача создана из голосового сообщения: {task['content']}")
        elif SERVICE == 'yougile':
            params = gpt.extract_yougile_task_params(text)
            task = client.create_task(**params)
            await update.message.reply_text(f"✅ Задача создана в Yougile из голосового сообщения: {params.get('title', text)}")
        else:
            await update.message.reply_text("❌ Сервис не настроен. Обратитесь к администратору.")
    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        await update.message.reply_text("❌ Не удалось обработать голосовое сообщение. Попробуйте позже.")

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main() 