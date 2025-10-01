#8366269150:AAEoaiS6IO5trTKYUPbVH3o29RBcSww73YU
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Налаштування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Словник вимови
SOUND_MAP = {
    'a': 'е', 'e': 'і', 'i': 'ай', 'o': 'оу', 'u': 'ю', 'y': 'ай',
    'b': 'б', 'c': 'к', 'd': 'д', 'f': 'ф', 'g': 'г', 'h': 'х',
    'j': 'дж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'p': 'п',
    'q': 'к', 'r': 'р', 's': 'с', 't': 'т', 'v': 'в', 'w': 'в',
    'x': 'кс', 'z': 'з', 'ch': 'ч', 'sh': 'ш', 'th': 'с', 'ph': 'ф',
    'ck': 'к', 'ng': 'нг', 'wh': 'в', 'qu': 'кв'
}

def make_sound(word):
    word = word.lower()
    result = []
    i = 0
    
    while i < len(word):
        if i + 1 < len(word) and word[i:i+2] in SOUND_MAP:
            result.append(SOUND_MAP[word[i:i+2]])
            i += 2
        elif word[i] in SOUND_MAP:
            result.append(SOUND_MAP[word[i]])
            i += 1
        else:
            result.append(word[i])
            i += 1
    
    return ''.join(result)

# Команди
async def start(update, context):
    text = """
👋 Привіт! Я бот-перекладач вимови!

📝 Напиши англійське слово, а я покажу як його вимовляти.

Приклади:
• hello → хелоу
• cat → кет
• thanks → сенкс

Спробуй! Напиши слово 🎯
    """
    await update.message.reply_text(text)

async def handle_word(update, context):
    word = update.message.text.strip().lower()
    
    if ' ' in word:
        await update.message.reply_text("⚠️ Напиши тільки одне слово!")
        return
    
    if not word.isalpha():
        await update.message.reply_text("⚠️ Тільки букви!")
        return
    
    sound = make_sound(word)
    
    response = f"""
🔤 Слово: {word}
🔊 Вимова: {sound}

💡 Читай так, як написано!
    """
    
    await update.message.reply_text(response)

# Головна функція
def main():
    # Отримуємо токен з Railway
    TOKEN = os.environ.get('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ Не знайшов токен! Перевір змінні Railway")
        return
    
    # Створюємо бота
    app = Application.builder().token(TOKEN).build()
    
    # Додаємо команди
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_word))
    
    # Запускаємо
    logger.info("🤖 Бот запускається на Railway...")
    app.run_polling()

if __name__ == "__main__":
    main()
