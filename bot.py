#8366269150:AAEoaiS6IO5trTKYUPbVH3o29RBcSww73YU
import os
import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Налаштування логування для Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Спробуємо імпортувати eng-to-ipa
try:
    import eng_to_ipa as ipa
    IPA_AVAILABLE = True
    logger.info("✅ eng-to-ipa успішно імпортовано")
except ImportError as e:
    IPA_AVAILABLE = False
    logger.error(f"❌ eng-to-ipa не встановлено: {e}")

# Велика база даних з транскрипцією та перекладом
WORD_DATABASE = {
    # Популярні слова
    'hello': {'pronunciation': 'хелоу', 'translation': 'привіт', 'ipa': 'həˈloʊ'},
    'thanks': {'pronunciation': 'сенкс', 'translation': 'дякую', 'ipa': 'θæŋks'},
    'please': {'pronunciation': 'пліз', 'translation': 'будь ласка', 'ipa': 'pliz'},
    'sorry': {'pronunciation': 'сорі', 'translation': 'вибач', 'ipa': 'ˈsɑri'},
    'yes': {'pronunciation': 'ес', 'translation': 'так', 'ipa': 'jɛs'},
    'no': {'pronunciation': 'ноу', 'translation': 'ні', 'ipa': 'noʊ'},
    'goodbye': {'pronunciation': 'гудбай', 'translation': 'до побачення', 'ipa': 'ɡʊdˈbaɪ'},
    
    # Числа
    'one': {'pronunciation': 'ван', 'translation': 'один', 'ipa': 'wʌn'},
    'two': {'pronunciation': 'ту', 'translation': 'два', 'ipa': 'tu'},
    'three': {'pronunciation': 'срі', 'translation': 'три', 'ipa': 'θri'},
    'four': {'pronunciation': 'фор', 'translation': 'чотири', 'ipa': 'fɔr'},
    'five': {'pronunciation': 'файв', 'translation': 'п\'ять', 'ipa': 'faɪv'},
    'six': {'pronunciation': 'сікс', 'translation': 'шість', 'ipa': 'sɪks'},
    'seven': {'pronunciation': 'севен', 'translation': 'сім', 'ipa': 'ˈsɛvən'},
    'eight': {'pronunciation': 'ейт', 'translation': 'вісім', 'ipa': 'eɪt'},
    'nine': {'pronunciation': 'найн', 'translation': 'дев\'ять', 'ipa': 'naɪn'},
    'ten': {'pronunciation': 'тен', 'translation': 'десять', 'ipa': 'tɛn'},
    
    # Кольори
    'red': {'pronunciation': 'ред', 'translation': 'червоний', 'ipa': 'rɛd'},
    'blue': {'pronunciation': 'блу', 'translation': 'синій', 'ipa': 'blu'},
    'green': {'pronunciation': 'грін', 'translation': 'зелений', 'ipa': 'ɡrin'},
    'yellow': {'pronunciation': 'елоу', 'translation': 'жовтий', 'ipa': 'ˈjɛloʊ'},
    'black': {'pronunciation': 'блек', 'translation': 'чорний', 'ipa': 'blæk'},
    'white': {'pronunciation': 'вайт', 'translation': 'білий', 'ipa': 'waɪt'},
    
    # Сім'я
    'family': {'pronunciation': 'фемілі', 'translation': 'родина', 'ipa': 'ˈfæməli'},
    'mother': {'pronunciation': 'мазер', 'translation': 'мати', 'ipa': 'ˈmʌðər'},
    'father': {'pronunciation': 'фазер', 'translation': 'батько', 'ipa': 'ˈfɑðər'},
    'brother': {'pronunciation': 'бразер', 'translation': 'брат', 'ipa': 'ˈbrʌðər'},
    'sister': {'pronunciation': 'сістер', 'translation': 'сестра', 'ipa': 'ˈsɪstər'},
    'child': {'pronunciation': 'чайлд', 'translation': 'дитина', 'ipa': 'tʃaɪld'},
    'man': {'pronunciation': 'мен', 'translation': 'чоловік', 'ipa': 'mæn'},
    'woman': {'pronunciation': 'вумен', 'translation': 'жінка', 'ipa': 'ˈwʊmən'},
    
    # Їжа
    'apple': {'pronunciation': 'еппл', 'translation': 'яблуко', 'ipa': 'ˈæpəl'},
    'banana': {'pronunciation': 'банана', 'translation': 'банан', 'ipa': 'bəˈnænə'},
    'orange': {'pronunciation': 'орендж', 'translation': 'апельсин', 'ipa': 'ˈɔrɪndʒ'},
    'water': {'pronunciation': 'вотер', 'translation': 'вода', 'ipa': 'ˈwɔtər'},
    'food': {'pronunciation': 'фуд', 'translation': 'їжа', 'ipa': 'fud'},
    'bread': {'pronunciation': 'бред', 'translation': 'хліб', 'ipa': 'brɛd'},
    'milk': {'pronunciation': 'мілк', 'translation': 'молоко', 'ipa': 'mɪlk'},
    'coffee': {'pronunciation': 'кофі', 'translation': 'кава', 'ipa': 'ˈkɔfi'},
    'tea': {'pronunciation': 'ті', 'translation': 'чай', 'ipa': 'ti'},
    
    # Тварини
    'cat': {'pronunciation': 'кет', 'translation': 'кіт', 'ipa': 'kæt'},
    'dog': {'pronunciation': 'дог', 'translation': 'собака', 'ipa': 'dɔɡ'},
    'bird': {'pronunciation': 'берд', 'translation': 'птах', 'ipa': 'bɜrd'},
    'fish': {'pronunciation': 'фіш', 'translation': 'риба', 'ipa': 'fɪʃ'},
    'horse': {'pronunciation': 'хорс', 'translation': 'кінь', 'ipa': 'hɔrs'},
    
    # Будинок
    'house': {'pronunciation': 'хаус', 'translation': 'будинок', 'ipa': 'haʊs'},
    'home': {'pronunciation': 'хоум', 'translation': 'дім', 'ipa': 'hoʊm'},
    'room': {'pronunciation': 'рум', 'translation': 'кімната', 'ipa': 'rum'},
    'door': {'pronunciation': 'дор', 'translation': 'двері', 'ipa': 'dɔr'},
    'window': {'pronunciation': 'віндоу', 'translation': 'вікно', 'ipa': 'ˈwɪndoʊ'},
    
    # Додаткові слова
    'computer': {'pronunciation': 'комп\'ютер', 'translation': 'комп\'ютер', 'ipa': 'kəmˈpjutər'},
    'phone': {'pronunciation': 'фон', 'translation': 'телефон', 'ipa': 'foʊn'},
    'book': {'pronunciation': 'бук', 'translation': 'книга', 'ipa': 'bʊk'},
    'friend': {'pronunciation': 'френд', 'translation': 'друг', 'ipa': 'frɛnd'},
    'time': {'pronunciation': 'тайм', 'translation': 'час', 'ipa': 'taɪm'},
    'love': {'pronunciation': 'лав', 'translation': 'кохати', 'ipa': 'lʌv'},
    'school': {'pronunciation': 'скул', 'translation': 'школа', 'ipa': 'skul'},
    'work': {'pronunciation': 'ворк', 'translation': 'робота', 'ipa': 'wɜrk'},
    'city': {'pronunciation': 'сіті', 'translation': 'місто', 'ipa': 'ˈsɪti'},
    'world': {'pronunciation': 'ворлд', 'translation': 'світ', 'ipa': 'wɜrld'},
}

def get_accurate_pronunciation(word):
    """Отримує точну транскрипцію через IPA"""
    word_lower = word.lower()
    
    # Спочатку шукаємо в нашій базі даних
    if word_lower in WORD_DATABASE:
        data = WORD_DATABASE[word_lower]
        return data['pronunciation'], data['translation'], data['ipa'], "база даних"
    
    # Спробуємо використати eng-to-ipa для точного IPA
    ipa_transcription = ""
    if IPA_AVAILABLE:
        try:
            ipa_result = ipa.convert(word_lower)
            if ipa_result and ipa_result != word_lower:
                ipa_transcription = ipa_result
                # Конвертуємо IPA в кириличну транскрипцію
                cyrillic = ipa_to_cyrillic(ipa_transcription)
                return cyrillic, "переклад не знайдено", ipa_transcription, "IPA транскрипція"
        except Exception as e:
            logger.error(f"Помилка IPA конвертації: {e}")
    
    # Якщо IPA не спрацював - використовуємо автоматичну транскрипцію
    auto_pronunciation = auto_transcribe(word_lower)
    return auto_pronunciation, "переклад не знайдено", "", "автоматична транскрипція"

def ipa_to_cyrillic(ipa_text):
    """Конвертує IPA транскрипцію в кириличну"""
    # Словник для конвертації IPA в кирилицю
    ipa_to_cyr = {
        # Голосні
        'æ': 'е', 'ɑ': 'а', 'ɔ': 'о', 'ə': 'е', 'ʌ': 'а', 'ɛ': 'е',
        'ɪ': 'і', 'i': 'і', 'ʊ': 'у', 'u': 'у', 
        'aɪ': 'ай', 'aʊ': 'ау', 'eɪ': 'ей', 'oʊ': 'оу', 'ɔɪ': 'ой',
        'ɪə': 'іе', 'eə': 'ее', 'ʊə': 'уе',
        
        # Приголосні
        'b': 'б', 'd': 'д', 'f': 'ф', 'g': 'г', 'h': 'х', 'j': 'й',
        'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'ŋ': 'нг', 'p': 'п',
        'r': 'р', 's': 'с', 'ʃ': 'ш', 't': 'т', 'tʃ': 'ч', 'θ': 'с',
        'ð': 'з', 'v': 'в', 'w': 'в', 'z': 'з', 'ʒ': 'ж', 'dʒ': 'дж',
        
        # Спеціальні символи
        'ˈ': '', 'ˌ': '', ':': ''
    }
    
    result = ipa_text
    
    # Спочатку обробляємо дифтонги та сполучення
    combinations = ['aɪ', 'aʊ', 'eɪ', 'oʊ', 'ɔɪ', 'ɪə', 'eə', 'ʊə', 'tʃ', 'dʒ']
    for combo in combinations:
        if combo in result:
            result = result.replace(combo, ipa_to_cyr.get(combo, combo))
    
    # Потім окремі символи
    for ipa_char, cyr_char in ipa_to_cyr.items():
        if ipa_char in result:
            result = result.replace(ipa_char, cyr_char)
    
    # Видаляємо зайві символи
    result = re.sub(r'[ˈˌː]', '', result)
    
    return result if result else auto_transcribe(ipa_text)

def auto_transcribe(word):
    """Автоматична транскрипція як резервний варіант"""
    # Спрощені правила
    rules = [
        (r'th', 'с'), (r'ch', 'ч'), (r'sh', 'ш'), (r'ph', 'ф'),
        (r'wh', 'в'), (r'ck', 'к'), (r'ng', 'нг'), (r'qu', 'кв'),
        (r'ee', 'і'), (r'ea', 'і'), (r'oo', 'у'), (r'oa', 'оу'),
        (r'ai', 'ей'), (r'ay', 'ей'), (r'ei', 'ей'), (r'ey', 'ей'),
        (r'tion', 'шен'), (r'sion', 'жен'), (r'ing', 'інг'),
    ]
    
    result = word.lower()
    for pattern, replacement in rules:
        result = re.sub(pattern, replacement, result)
    
    # Базові звуки
    result = re.sub(r'a', 'е', result)
    result = re.sub(r'e', 'і', result)
    result = re.sub(r'i', 'ай', result)
    result = re.sub(r'o', 'о', result)
    result = re.sub(r'u', 'у', result)
    result = re.sub(r'y', 'і', result)
    
    return result

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ipa_status = "✅ увімкнено" if IPA_AVAILABLE else "❌ вимкнено"
    
    welcome_text = f"""
👋 Привіт, {user.first_name}!

🤖 Я бот з **точною фонетичною транскрипцією**!

🎯 Надішліть англійське слово і я:
• 🔊 Покажу **вимову** українськими буквами
• 📝 Покажу **IPA транскрипцію** (міжнародну)
• 📚 Використаю базу з **{len(WORD_DATABASE)}** слів

🔧 **Стан системи:**
• IPA транскрипція: {ipa_status}

🔊 **Приклади:**
• `hello` → `хелоу` /həˈloʊ/ 
• `computer` → `комп'ютер` /kəmˈpjutər/ 
• `thanks` → `сенкс` /θæŋks/ 
💡 **Спробуйте ці слова для тесту:**
cat, water, family, beautiful, question

    """
    await update.message.reply_text(welcome_text)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ipa_status = "✅ доступна" if IPA_AVAILABLE else "❌ недоступна"
    
    help_text = f"""
📖 **Довідка по боту:**

🎯 **Точна транскрипція:**
• Використовую **IPA** (International Phonetic Alphabet)
• Конвертую IPA в кириличну вимову
• База з {len(WORD_DATABASE)} слів з точними транскрипціями

💡 **Порада:** Використовуйте /stats для деталей
    """
    await update.message.reply_text(help_text)

# Команда /stats
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_words = len(WORD_DATABASE)
    ipa_status = "🟢 працює" if IPA_AVAILABLE else "🔴 не працює"
    
    stats_text = f"""
📊 **Статистика системи:**

• Слів у базі: **{total_words}**
• IPA транскрипція: **{ipa_status}**
• Методи транскрипції: база даних, IPA, автоматична

"""
    await update.message.reply_text(stats_text)

# Обробка текстових повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    
    if user_message.startswith('/'):
        return
    
    if ' ' in user_message:
        await update.message.reply_text("⚠️ Будь ласка, надішліть тільки **одне** слово")
        return
    
    if not user_message.isalpha():
        await update.message.reply_text("⚠️ Використовуйте тільки літери")
        return
    
    # Отримуємо точну транскрипцію
    pronunciation, translation, ipa_text, method = get_accurate_pronunciation(user_message)
    
    # Формуємо відповідь
    response = f"""
🔤 **Слово:** `{user_message}`
🔊 **Вимова:** `{pronunciation}`
🌐 **Переклад:** `{translation}`
"""
    
    # Додаємо IPA якщо є
    if ipa_text:
        response += f"📝 **IPA:** `/{ipa_text}/`\n"
    
    response += f"🎯 **Метод:** {method}\n"

    # Додаткові нотатки
    if method == "база даних":
        response += "💡 *Точна транскрипція з перевіреної бази*"
    elif method == "IPA транскрипція":
        response += "💡 *Точна фонетична транскрипція через IPA*"
    else:
        response += "💡 *Автоматична транскрипція - слово відсутнє в базі*"
    
    await update.message.reply_text(response)

# Обробка помилок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Помилка: {context.error}")
    await update.message.reply_text("❌ Сталася помилка. Спробуйте ще раз пізніше.")

def main():
    TOKEN = os.environ.get('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ BOT_TOKEN не знайдено! Додайте у змінні середовища на Railway")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    logger.info("🚀 Бот з IPA транскрипцією запускається...")
    logger.info(f"📊 База: {len(WORD_DATABASE)} слів, IPA: {IPA_AVAILABLE}")
    application.run_polling()

if __name__ == "__main__":
    main()
