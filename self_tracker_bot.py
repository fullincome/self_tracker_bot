import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from todoist_api import TodoistAPI
from yougile_api import YougileAPI
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
YOUGILE_TOKEN = os.getenv('YOUGILE_TOKEN')
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
    client = YougileAPI(YOUGILE_TOKEN, default_location=yougile_location)
else:
    raise ValueError("Unknown SERVICE value. Must be 'todoist' or 'yougile'.")

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
    try:
        if SERVICE == 'todoist':
            task = client.create_task(
                content=update.message.text,
                priority=4
            )
            await update.message.reply_text(f"✅ Задача создана в Todoist: {task['content']}")
        elif SERVICE == 'yougile':
            task = client.create_task(
                title=update.message.text
            )
            await update.message.reply_text(f"✅ Задача создана в Yougile: {update.message.text}")
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
        # Пробуем несколько моделей для лучшего распознавания
        models_to_try = [
            'general:rc',  # Улучшенная модель с пунктуацией
            'general',     # Базовая модель
            'spontaneous'  # Модель для спонтанной речи
        ]
        text = ""
        for model_name in models_to_try:
            try:
                # Настраиваем модель распознавания
                model = model_repository.recognition_model()
                model.model = model_name
                model.language = 'ru-RU'
                model.audio_processing_type = AudioProcessingType.Full
                # Дополнительные настройки для лучшего распознавания
                model.profanity_filter = False
                model.literature_text = False
                # Распознаем речь
                result = model.transcribe_file(temp_file)
                if result and len(result) > 0:
                    text = result[0].raw_text.strip()
                    if text:
                        logger.info(f"Successfully recognized with model '{model_name}': {text}")
                        break
            except Exception as model_error:
                logger.warning(f"Model '{model_name}' failed: {model_error}")
                continue
        # Удаляем временный файл
        os.remove(temp_file)
        if not text:
            raise ValueError("Не удалось распознать речь ни одной из моделей")
        # Создаем задачу из распознанного текста
        if SERVICE == 'todoist':
            task = client.create_task(
                content=text,
                priority=4
            )
            await update.message.reply_text(f"✅ Задача создана из голосового сообщения: {task['content']}")
        elif SERVICE == 'yougile':
            task = client.create_task(
                title=text
            )
            await update.message.reply_text(f"✅ Задача создана в Yougile из голосового сообщения: {text}")
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