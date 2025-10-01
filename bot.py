#8366269150:AAEoaiS6IO5trTKYUPbVH3o29RBcSww73YU
import os
import logging
import re
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Налаштування логування для Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словник транскрипції та перекладів
PRONUNCIATION_DB = {
    # Транскрипції
    'pronunciation': {
        'the': 'зе', 'and': 'енд', 'you': 'ю', 'are': 'ар', 'your': 'йор',
        'their': 'зер', 'there': 'зер', 'they': 'зей', 'what': 'уот', 
        'when': 'вен', 'where': 'вер', 'why': 'вай', 'who': 'ху', 
        'which': 'віч', 'this': 'зис', 'that': 'зет', 'with': 'віз',
        'have': 'хев', 'give': 'гів', 'live': 'лів', 'love': 'лав',
        'some': 'сам', 'come': 'кам', 'done': 'дан', 'one': 'ван',
        'two': 'ту', 'three': 'срі', 'four': 'фор', 'five': 'файв',
        'six': 'сікс', 'seven': 'севен', 'eight': 'ейт', 'nine': 'найн',
        'ten': 'тен', 'answer': 'енсер', 'hello': 'хелоу', 'thanks': 'сенкс',
        'computer': 'комп\'ютер', 'water': 'вотер', 'people': 'піпл',
        'because': 'бікоз', 'family': 'фемілі', 'friend': 'френд',
        'school': 'скул', 'house': 'хаус', 'car': 'кар', 'book': 'бук',
        'phone': 'фон', 'time': 'тайм', 'day': 'дей', 'night': 'найт',
        'sun': 'сан', 'moon': 'мун', 'star': 'стар', 'tree': 'трі',
        'flower': 'флавер', 'food': 'фуд', 'good': 'гуд', 'bad': 'бед',
        'happy': 'хепі', 'sad': 'сед', 'big': 'біг', 'small': 'смол',
        'hot': 'хот', 'cold': 'колд', 'new': 'ню', 'old': 'олд',
        'beautiful': 'б\'ютіфул', 'ugly': 'аглі', 'fast': 'фест',
        'slow': 'слоу', 'high': 'хай', 'low': 'лоу', 'right': 'райт',
        'left': 'left', 'up': 'ап', 'down': 'даун', 'yes': 'ес',
        'no': 'ноу', 'please': 'пліз', 'sorry': 'сорі', 'thank you': 'сенк ю',
        'goodbye': 'гудбай', 'morning': 'морнінг', 'evening': 'івнінг',
        'apple': 'еппл', 'banana': 'банана', 'orange': 'орендж',
        'mother': 'мазер', 'father': 'фазер', 'brother': 'бразер',
        'sister': 'сістер', 'child': 'чайлд', 'man': 'мен', 'woman': 'вумен'
    },
    
    # Переклади
    'translation': {
        'the': 'the (артикль)', 'and': 'і', 'you': 'ти/ви', 'are': 'є', 
        'your': 'твій/ваш', 'their': 'їхній', 'there': 'там', 'they': 'вони',
        'what': 'що', 'when': 'коли', 'where': 'де', 'why': 'чому', 
        'who': 'хто', 'which': 'який', 'this': 'цей', 'that': 'той',
        'with': 'з', 'have': 'мати', 'give': 'давати', 'live': 'жити',
        'love': 'кохати', 'some': 'деякі', 'come': 'приходити',
        'done': 'зроблено', 'one': 'один', 'two': 'два', 'three': 'три',
        'four': 'чотири', 'five': 'п\'ять', 'six': 'шість', 'seven': 'сім',
        'eight': 'вісім', 'nine': 'дев\'ять', 'ten': 'десять',
        'answer': 'відповідь', 'hello': 'привіт', 'thanks': 'дякую',
        'computer': 'комп\'ютер', 'water': 'вода', 'people': 'люди',
        'because': 'тому що', 'family': 'родина', 'friend': 'друг',
        'school': 'школа', 'house': 'будинок', 'car': 'автомобіль',
        'book': 'книга', 'phone': 'телефон', 'time': 'час', 'day': 'день',
        'night': 'ніч', 'sun': 'сонце', 'moon': 'місяць', 'star': 'зірка',
        'tree': 'дерево', 'flower': 'квітка', 'food': 'їжа', 'good': 'добре',
        'bad': 'погано', 'happy': 'щасливий', 'sad': 'сумний', 'big': 'великий',
        'small': 'малий', 'hot': 'гарячий', 'cold': 'холодний', 'new': 'новий',
        'old': 'старий', 'beautiful': 'красивий', 'ugly': 'потворний',
        'fast': 'швидкий', 'slow': 'повільний', 'high': 'високий',
        'low': 'низький', 'right': 'правий/право', 'left': 'лівий/ліворуч',
        'up': 'вгору', 'down': 'вниз', 'yes': 'так', 'no': 'ні',
        'please': 'будь ласка', 'sorry': 'вибач', 'thank you': 'дякую',
        'goodbye': 'до побачення', 'morning': 'ранок', 'evening': 'вечір',
        'apple': 'яблуко', 'banana': 'банан', 'orange': 'апельсин',
        'mother': 'мати', 'father': 'батько', 'brother': 'брат',
        'sister': 'сестра', 'child': 'дитина', 'man': 'чоловік', 'woman': 'жінка'
    }
}

def get_pronunciation(word):
    """Отримує транскрипцію слова"""
    word_lower = word.lower()
    
    # Спочатку шукаємо в базі даних
    if word_lower in PRONUNCIATION_DB['pronunciation']:
        return PRONUNCIATION_DB['pronunciation'][word_lower], "база даних"
    
    # Автоматична транскрипція для нових слів
    return auto_pronunciation(word_lower), "автоматична транскрипція"

def get_translation(word):
    """Отримує переклад слова"""
    word_lower = word.lower()
    return PRONUNCIATION_DB['translation'].get(word_lower, "переклад не знайдено")

def auto_pronunciation(word):
    """Автоматична транскрипція на основі правил"""
    # Основний правила вимови
    rules = [
        (r'th', 'с'), (r'ch', 'ч'), (r'sh', 'ш'), (r'ph', 'ф'), (r'wh', 'в'),
        (r'ck', 'к'), (r'ng', 'нг'), (r'qu', 'кв'), (r'kn', 'н'), (r'wr', 'р'),
        (r'gh', 'г'), (r'rh', 'р'), (r'psy', 'сай'), (r'pn', 'н'), (r'ps', 'с')
    ]
    
    # Голосні та їх комбінації
    vowels = [
        (r'augh', 'оф'), (r'ough', 'оф'), (r'eigh', 'ей'), (r'igh', 'ай'),
        (r'augh', 'аф'), (r'oi', 'ой'), (r'oy', 'ой'), (r'ou', 'ау'),
        (r'ow', 'ау'), (r'ea', 'і'), (r'ee', 'і'), (r'oo', 'у'), (r'oa', 'оу'),
        (r'ai', 'ей'), (r'ay', 'ей'), (r'ei', 'ей'), (r'ey', 'ей'),
        (r'ie', 'і'), (r'ue', 'у'), (r'ui', 'у'), (r'ae', 'е'), (r'oe', 'і')
    ]
    
    # Кінцеві правила
    endings = [
        (r'tion$', 'шен'), (r'sion$', 'жен'), (r'cian$', 'шен'),
        (r'cious$', 'шес'), (r'tious$', 'шес'), (r'cial$', 'шел'),
        (r'tial$', 'шел'), (r'able$', 'ейбл'), (r'ible$', 'ібл'),
        (r'ful$', 'фул'), (r'less$', 'лес'), (r'ness$', 'нес'),
        (r'ment$', 'мент'), (r'ing$', 'інг'), (r'ed$', 'ед'),
        (r'er$', 'ер'), (r'est$', 'ест'), (r'ly$', 'лі')
    ]
    
    result = word.lower()
    
    # Застосовуємо правила у правильному порядку
    for pattern, replacement in endings + vowels + rules:
        result = re.sub(pattern, replacement, result)
    
    # Базові голосні
    result = re.sub(r'a', 'е', result)
    result = re.sub(r'e', 'і', result) 
    result = re.sub(r'i', 'ай', result)
    result = re.sub(r'o', 'о', result)
    result = re.sub(r'u', 'у', result)
    result = re.sub(r'y', 'і', result)
    
    # Приголосні
    result = re.sub(r'b', 'б', result)
    result = re.sub(r'c', 'к', result)
    result = re.sub(r'd', 'д', result)
    result = re.sub(r'f', 'ф', result)
    result = re.sub(r'g', 'г', result)
    result = re.sub(r'h', 'х', result)
    result = re.sub(r'j', 'дж', result)
    result = re.sub(r'k', 'к', result)
    result = re.sub(r'l', 'л', result)
    result = re.sub(r'm', 'м', result)
    result = re.sub(r'n', 'н', result)
    result = re.sub(r'p', 'п', result)
    result = re.sub(r'q', 'к', result)
    result = re.sub(r'r', 'р', result)
    result = re.sub(r's', 'с', result)
    result = re.sub(r't', 'т', result)
    result = re.sub(r'v', 'в', result)
    result = re.sub(r'w', 'в', result)
    result = re.sub(r'x', 'кс', result)
    result = re.sub(r'z', 'з', result)
    
    return result

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""
👋 Привіт, {user.first_name}!

🤖 Я бот для вивчення англійської вимови!

🎯 Надішліть мені англійське слово і я:
• 🔊 Покажу **транскрипцію** українськими буквами
• 🌐 Надам **переклад** українською
• 📚 Використаю базу з 100+ слів

🔊 **Приклади:**
• `hello` → `хелоу` (привіт)
• `computer` → `комп'ютер` (комп'ютер)
• `thanks` → `сенкс` (дякую)

💡 **Доступні команди:**
/start - початок роботи
/help - допомога
/stats - статистика

Напиши слово і спробуй! 🎯
    """
    await update.message.reply_text(welcome_text)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 **Довідка по боту:**

🎯 **Що я вмію:**
• Транскрибувати англійські слова українськими буквами
• Надавати переклад українською
• Працювати з базою з 100+ популярних слів
• Автоматично транскрибувати нові слова

🔊 **Як це працює:**
1. Я перевіряю слово в моїй базі даних
2. Якщо слова немає - використовую автоматичні правила
3. Повертаю транскрипцію та переклад

⚠️ **Обмеження:**
• Працює тільки з окремими словами
• Автоматична транскрипція може бути неточною для складних слів

💡 **Порада:** Почніть з простих слів як `hello`, `cat`, `book`
    """
    await update.message.reply_text(help_text)

# Команда /stats
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_words = len(PRONUNCIATION_DB['pronunciation'])
    stats_text = f"""
📊 **Статистика бази даних:**

• Слів у базі: **{total_words}**
• Категорії: побутові слова, числа, родина, їжа
• Методи: база даних + автоматична транскрипція

🔧 **Технічна інформація:**
• Хостинг: Railway
• Мова: Python
• Бібліотека: python-telegram-bot

База постійно оновлюється! 🚀
    """
    await update.message.reply_text(stats_text)

# Обробка текстових повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    
    # Ігноруємо команди
    if user_message.startswith('/'):
        return
    
    # Перевірка на одне слово
    if ' ' in user_message:
        await update.message.reply_text("⚠️ Будь ласка, надішліть тільки **одне** слово")
        return
    
    if not user_message.isalpha():
        await update.message.reply_text("⚠️ Використовуйте тільки літери (без цифр чи спецсимволів)")
        return
    
    if len(user_message) > 20:
        await update.message.reply_text("⚠️ Слово занадто довге. Максимум 20 символів")
        return
    
    # Отримуємо транскрипцію та переклад
    pronunciation, method = get_pronunciation(user_message)
    translation = get_translation(user_message)
    
    # Формуємо відповідь
    response = f"""
🔤 **Слово:** `{user_message}`
🔊 **Вимова:** `{pronunciation}`
🌐 **Переклад:** `{translation}`
📝 **Метод:** {method}

💡 *Працює на Railway 24/7!*
    """
    
    await update.message.reply_text(response)

# Обробка помилок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Помилка: {context.error}")
    await update.message.reply_text("❌ Сталася помилка. Спробуйте ще раз пізніше.")

def main():
    # Отримуємо токен з змінних середовища
    TOKEN = os.environ.get('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ BOT_TOKEN не знайдено! Додайте його у змінні середовища на Railway")
        return
    
    # Створюємо додаток
    application = Application.builder().token(TOKEN).build()
    
    # Додаємо обробники
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Запускаємо бота
    logger.info("🚀 Бот запускається на Railway...")
    logger.info(f"📊 База містить {len(PRONUNCIATION_DB['pronunciation'])} слів")
    application.run_polling()

if __name__ == "__main__":
    main()
