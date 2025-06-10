import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from todoist_api import TodoistAPI
from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType
import io

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
ALLOWED_USER_ID = int(os.getenv('TELEGRAM_USER_ID', '0'))  # ID пользователя, которому разрешен доступ

if not TELEGRAM_TOKEN or not TODOIST_TOKEN or not YANDEX_SPEECHKIT_TOKEN:
    raise ValueError("TELEGRAM_TOKEN, TODOIST_TOKEN and YANDEX_SPEECHKIT_TOKEN must be set in environment variables")

if ALLOWED_USER_ID == 0:
    raise ValueError("TELEGRAM_USER_ID must be set in environment variables")

# Инициализируем клиенты
todoist = TodoistAPI(TODOIST_TOKEN)

# Настраиваем SpeechKit
configure_credentials(
    yandex_credentials=creds.YandexCredentials(
        api_key=YANDEX_SPEECHKIT_TOKEN
    )
)

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
    
    await update.message.reply_text(
        "Привет! Я бот для создания задач в Todoist.\n"
        "Просто отправь мне текст или голосовое сообщение, "
        "и я создам из него задачу."
    )

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
    
    try:
        # Создаем задачу из текста сообщения
        task = todoist.create_task(
            content=update.message.text,
            priority=4
        )
        await update.message.reply_text(f"✅ Задача создана: {task['content']}")
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        await update.message.reply_text("❌ Не удалось создать задачу. Попробуйте позже.")

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
        
        # Настраиваем модель распознавания
        model = model_repository.recognition_model()
        model.model = 'general'
        model.language = 'ru-RU'
        model.audio_processing_type = AudioProcessingType.Full
        
        # Распознаем речь
        result = model.transcribe_file(temp_file)
        text = result[0].raw_text if result else ""
        
        # Удаляем временный файл
        os.remove(temp_file)
        
        if not text:
            raise ValueError("Не удалось распознать речь")
        
        # Создаем задачу из распознанного текста
        task = todoist.create_task(
            content=text,
            priority=4
        )
        await update.message.reply_text(f"✅ Задача создана из голосового сообщения: {task['content']}")
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