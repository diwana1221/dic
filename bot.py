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

# Спробуємо імпортувати g2p-en для точної транскрипції
try:
    from g2p_en import G2p
    G2P_AVAILABLE = True
    g2p = G2p()
    logger.info("✅ g2p-en успішно імпортовано")
except ImportError as e:
    G2P_AVAILABLE = False
    logger.error(f"❌ g2p-en не встановлено: {e}")

# Велика база даних з транскрипцією та перекладом
WORD_DATABASE = {
    # Популярні слова
    'hello': {'pronunciation': 'хелоу', 'translation': 'привіт', 'phonemes': 'h ə l ˈoʊ'},
    'thanks': {'pronunciation': 'сенкс', 'translation': 'дякую', 'phonemes': 'θ æ ŋ k s'},
    'thank you': {'pronunciation': 'сенк ю', 'translation': 'дякую', 'phonemes': 'θ æ ŋ k j u'},
    'please': {'pronunciation': 'пліз', 'translation': 'будь ласка', 'phonemes': 'p l i z'},
    'sorry': {'pronunciation': 'сорі', 'translation': 'вибач', 'phonemes': 'ˈs ɑ r i'},
    'yes': {'pronunciation': 'ес', 'translation': 'так', 'phonemes': 'j ɛ s'},
    'no': {'pronunciation': 'ноу', 'translation': 'ні', 'phonemes': 'n oʊ'},
    'goodbye': {'pronunciation': 'гудбай', 'translation': 'до побачення', 'phonemes': 'ɡ ʊ d ˈb aɪ'},
    
    # Числа
    'one': {'pronunciation': 'ван', 'translation': 'один', 'phonemes': 'w ʌ n'},
    'two': {'pronunciation': 'ту', 'translation': 'два', 'phonemes': 't u'},
    'three': {'pronunciation': 'срі', 'translation': 'три', 'phonemes': 'θ r i'},
    'four': {'pronunciation': 'фор', 'translation': 'чотири', 'phonemes': 'f ɔ r'},
    'five': {'pronunciation': 'файв', 'translation': 'п\'ять', 'phonemes': 'f aɪ v'},
    'six': {'pronunciation': 'сікс', 'translation': 'шість', 'phonemes': 's ɪ k s'},
    'seven': {'pronunciation': 'севен', 'translation': 'сім', 'phonemes': 'ˈs ɛ v ə n'},
    'eight': {'pronunciation': 'ейт', 'translation': 'вісім', 'phonemes': 'eɪ t'},
    'nine': {'pronunciation': 'найн', 'translation': 'дев\'ять', 'phonemes': 'n aɪ n'},
    'ten': {'pronunciation': 'тен', 'translation': 'десять', 'phonemes': 't ɛ n'},
    
    # Кольори
    'red': {'pronunciation': 'ред', 'translation': 'червоний', 'phonemes': 'r ɛ d'},
    'blue': {'pronunciation': 'блу', 'translation': 'синій', 'phonemes': 'b l u'},
    'green': {'pronunciation': 'грін', 'translation': 'зелений', 'phonemes': 'ɡ r i n'},
    'yellow': {'pronunciation': 'елоу', 'translation': 'жовтий', 'phonemes': 'ˈj ɛ l oʊ'},
    'black': {'pronunciation': 'блек', 'translation': 'чорний', 'phonemes': 'b l æ k'},
    'white': {'pronunciation': 'вайт', 'translation': 'білий', 'phonemes': 'w aɪ t'},
    
    # Сім'я
    'family': {'pronunciation': 'фемілі', 'translation': 'родина', 'phonemes': 'ˈf æ m ə l i'},
    'mother': {'pronunciation': 'мазер', 'translation': 'мати', 'phonemes': 'ˈm ʌ ð ər'},
    'father': {'pronunciation': 'фазер', 'translation': 'батько', 'phonemes': 'ˈf ɑ ð ər'},
    'brother': {'pronunciation': 'бразер', 'translation': 'брат', 'phonemes': 'ˈb r ʌ ð ər'},
    'sister': {'pronunciation': 'сістер', 'translation': 'сестра', 'phonemes': 'ˈs ɪ s t ər'},
    'child': {'pronunciation': 'чайлд', 'translation': 'дитина', 'phonemes': 'tʃ aɪ l d'},
    'man': {'pronunciation': 'мен', 'translation': 'чоловік', 'phonemes': 'm æ n'},
    'woman': {'pronunciation': 'вумен', 'translation': 'жінка', 'phonemes': 'ˈw ʊ m ə n'},
    
    # Їжа
    'apple': {'pronunciation': 'еппл', 'translation': 'яблуко', 'phonemes': 'ˈæ p ə l'},
    'banana': {'pronunciation': 'банана', 'translation': 'банан', 'phonemes': 'b ə ˈn æ n ə'},
    'orange': {'pronunciation': 'орендж', 'translation': 'апельсин', 'phonemes': 'ˈɔ r ɪ n dʒ'},
    'water': {'pronunciation': 'вотер', 'translation': 'вода', 'phonemes': 'ˈw ɔ t ər'},
    'food': {'pronunciation': 'фуд', 'translation': 'їжа', 'phonemes': 'f u d'},
    'bread': {'pronunciation': 'бред', 'translation': 'хліб', 'phonemes': 'b r ɛ d'},
    'milk': {'pronunciation': 'мілк', 'translation': 'молоко', 'phonemes': 'm ɪ l k'},
    'coffee': {'pronunciation': 'кофі', 'translation': 'кава', 'phonemes': 'ˈk ɔ f i'},
    'tea': {'pronunciation': 'ті', 'translation': 'чай', 'phonemes': 't i'},
    
    # Тварини
    'cat': {'pronunciation': 'кет', 'translation': 'кіт', 'phonemes': 'k æ t'},
    'dog': {'pronunciation': 'дог', 'translation': 'собака', 'phonemes': 'd ɔ ɡ'},
    'bird': {'pronunciation': 'берд', 'translation': 'птах', 'phonemes': 'b ɜ r d'},
    'fish': {'pronunciation': 'фіш', 'translation': 'риба', 'phonemes': 'f ɪ ʃ'},
    'horse': {'pronunciation': 'хорс', 'translation': 'кінь', 'phonemes': 'h ɔ r s'},
    
    # Будинок
    'house': {'pronunciation': 'хаус', 'translation': 'будинок', 'phonemes': 'h aʊ s'},
    'home': {'pronunciation': 'хоум', 'translation': 'дім', 'phonemes': 'h oʊ m'},
    'room': {'pronunciation': 'рум', 'translation': 'кімната', 'phonemes': 'r u m'},
    'door': {'pronunciation': 'дор', 'translation': 'двері', 'phonemes': 'd ɔ r'},
    'window': {'pronunciation': 'віндоу', 'translation': 'вікно', 'phonemes': 'ˈw ɪ n d oʊ'},
    
    # Додаткові слова
    'computer': {'pronunciation': 'комп\'ютер', 'translation': 'комп\'ютер', 'phonemes': 'k ə m ˈp j u t ər'},
    'phone': {'pronunciation': 'фон', 'translation': 'телефон', 'phonemes': 'f oʊ n'},
    'book': {'pronunciation': 'бук', 'translation': 'книга', 'phonemes': 'b ʊ k'},
    'friend': {'pronunciation': 'френд', 'translation': 'друг', 'phonemes': 'f r ɛ n d'},
    'time': {'pronunciation': 'тайм', 'translation': 'час', 'phonemes': 't aɪ m'},
    'love': {'pronunciation': 'лав', 'translation': 'кохати', 'phonemes': 'l ʌ v'},
    'school': {'pronunciation': 'скул', 'translation': 'школа', 'phonemes': 's k u l'},
    'work': {'pronunciation': 'ворк', 'translation': 'робота', 'phonemes': 'w ɜ r k'},
    'city': {'pronunciation': 'сіті', 'translation': 'місто', 'phonemes': 'ˈs ɪ t i'},
    'world': {'pronunciation': 'ворлд', 'translation': 'світ', 'phonemes': 'w ɜ r l d'},
    'beautiful': {'pronunciation': 'б\'ютіфул', 'translation': 'красивий', 'phonemes': 'ˈb j u t ɪ f ʊ l'},
    'answer': {'pronunciation': 'енсер', 'translation': 'відповідь', 'phonemes': 'ˈæ n s ər'},
    'question': {'pronunciation': 'квесчен', 'translation': 'питання', 'phonemes': 'ˈk w ɛ s tʃ ən'},
    'water': {'pronunciation': 'вотер', 'translation': 'вода', 'phonemes': 'ˈw ɔ t ər'},
    'people': {'pronunciation': 'піпл', 'translation': 'люди', 'phonemes': 'ˈp i p əl'},
    'because': {'pronunciation': 'бікоз', 'translation': 'тому що', 'phonemes': 'b ɪ ˈk ɔ z'},
}

def get_accurate_pronunciation(word):
    """Отримує точну транскрипцію через g2p-en"""
    word_lower = word.lower()
    
    # Спочатку шукаємо в нашій базі даних
    if word_lower in WORD_DATABASE:
        data = WORD_DATABASE[word_lower]
        return data['pronunciation'], data['translation'], data['phonemes'], "база даних"
    
    # Спробуємо використати g2p-en для точної фонетичної транскрипції
    phonemes_text = ""
    if G2P_AVAILABLE:
        try:
            phonemes = g2p(word_lower)
            phonemes_text = ' '.join(phonemes)
            # Конвертуємо фонеми в кириличну транскрипцію
            cyrillic = phonemes_to_cyrillic(phonemes)
            return cyrillic, "переклад не знайдено", phonemes_text, "фонетична транскрипція"
        except Exception as e:
            logger.error(f"Помилка g2p конвертації: {e}")
    
    # Якщо g2p не спрацював - використовуємо автоматичну транскрипцію
    auto_pronunciation = auto_transcribe(word_lower)
    return auto_pronunciation, "переклад не знайдено", "", "автоматична транскрипція"

def phonemes_to_cyrillic(phonemes):
    """Конвертує фонеми в кириличну транскрипцію"""
    # Словник для конвертації фонем в кирилицю
    phoneme_to_cyr = {
        # Голосні
        'æ': 'е', 'ɑ': 'а', 'ɔ': 'о', 'ə': 'е', 'ʌ': 'а', 'ɛ': 'е',
        'ɪ': 'і', 'i': 'і', 'ʊ': 'у', 'u': 'у', 
        'aɪ': 'ай', 'aʊ': 'ау', 'eɪ': 'ей', 'oʊ': 'оу', 'ɔɪ': 'ой',
        
        # Приголосні
        'b': 'б', 'd': 'д', 'f': 'ф', 'g': 'г', 'h': 'х', 'j': 'й',
        'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'ŋ': 'нг', 'p': 'п',
        'r': 'р', 's': 'с', 'ʃ': 'ш', 't': 'т', 'tʃ': 'ч', 'θ': 'с',
        'ð': 'з', 'v': 'в', 'w': 'в', 'z': 'з', 'ʒ': 'ж', 'dʒ': 'дж',
        
        # Спеціальні символи
        'ˈ': '', 'ˌ': '', ':': ''
    }
    
    # Об'єднуємо фонеми в строку для обробки
    phoneme_str = ''.join(phonemes)
    
    # Спочатку обробляємо дифтонги та сполучення
    combinations = ['aɪ', 'aʊ', 'eɪ', 'oʊ', 'ɔɪ', 'tʃ', 'dʒ']
    for combo in combinations:
        if combo in phoneme_str:
            phoneme_str = phoneme_str.replace(combo, phoneme_to_cyr.get(combo, combo))
    
    # Потім окремі символи
    result = []
    for char in phoneme_str:
        result.append(phoneme_to_cyr.get(char, char))
    
    cyrillic = ''.join(result)
    
    # Видаляємо зайві символи
    cyrillic = re.sub(r'[ˈˌː]', '', cyrillic)
    
    return cyrillic if cyrillic and cyrillic != phoneme_str else auto_transcribe(''.join(phonemes))

def auto_transcribe(word):
    """Автоматична транскрипція як резервний варіант"""
    # Покращені правила вимови
    rules = [
        # Сполучення приголосних
        (r'th', 'с'), (r'ch', 'ч'), (r'sh', 'ш'), (r'ph', 'ф'),
        (r'wh', 'в'), (r'ck', 'к'), (r'ng', 'нг'), (r'qu', 'кв'),
        (r'gh', 'г'), (r'rh', 'р'), (r'kn', 'н'), (r'wr', 'р'),
        (r'psy', 'сай'), (r'pn', 'н'), (r'ps', 'с'),
        
        # Голосні комбінації
        (r'augh', 'оф'), (r'ough', 'оф'), (r'eigh', 'ей'), (r'igh', 'ай'),
        (r'oi', 'ой'), (r'oy', 'ой'), (r'ou', 'ау'), (r'ow', 'ау'),
        (r'ea', 'і'), (r'ee', 'і'), (r'oo', 'у'), (r'oa', 'оу'),
        (r'ai', 'ей'), (r'ay', 'ей'), (r'ei', 'ей'), (r'ey', 'ей'),
        (r'ie', 'і'), (r'ue', 'у'), (r'ui', 'у'), (r'ae', 'е'), (r'oe', 'і'),
        
        # Кінцівки
        (r'tion$', 'шен'), (r'sion$', 'жен'), (r'cian$', 'шен'),
        (r'cious$', 'шес'), (r'tious$', 'шес'), (r'cial$', 'шел'),
        (r'tial$', 'шел'), (r'able$', 'ейбл'), (r'ible$', 'ібл'),
        (r'ful$', 'фул'), (r'less$', 'лес'), (r'ness$', 'нес'),
        (r'ment$', 'мент'), (r'ing$', 'інг'), (r'ed$', 'ед'),
        (r'er$', 'ер'), (r'est$', 'ест'), (r'ly$', 'лі')
    ]
    
    result = word.lower()
    
    # Застосовуємо правила у правильному порядку
    for pattern, replacement in rules:
        result = re.sub(pattern, replacement, result)
    
    # Базові голосні (після всіх комбінацій)
    result = re.sub(r'a', 'е', result)
    result = re.sub(r'e', 'і', result)
    result = re.sub(r'i', 'ай', result)
    result = re.sub(r'o', 'о', result)
    result = re.sub(r'u', 'у', result)
    result = re.sub(r'y', 'і', result)
    
    # Базові приголосні
    consonants = {
        'b': 'б', 'c': 'к', 'd': 'д', 'f': 'ф', 'g': 'г', 'h': 'х',
        'j': 'дж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'p': 'п',
        'q': 'к', 'r': 'р', 's': 'с', 't': 'т', 'v': 'в', 'w': 'в',
        'x': 'кс', 'z': 'з'
    }
    
    for eng, ukr in consonants.items():
        result = result.replace(eng, ukr)
    
    return result

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    g2p_status = "✅ увімкнено" if G2P_AVAILABLE else "❌ вимкнено"
    
    welcome_text = f"""
👋 Привіт, {user.first_name}!

🤖 Я бот з **точною фонетичною транскрипцією**!

🎯 Надішліть англійське слово і я:
• 🔊 Покажу **вимову** українськими буквами
• 🌐 Надам **переклад** українською
• 📝 Покажу **фонетичну транскрипцію**
• 📚 Використаю базу з **{len(WORD_DATABASE)}** слів

🔧 **Стан системи:**
• Фонетичний аналіз: {g2p_status}

🔊 **Приклади:**
• `hello` → `хелоу` [h ə l ˈoʊ] (привіт)
• `computer` → `комп'ютер` [k ə m ˈp j u t ər] (комп'ютер)
• `thanks` → `сенкс` [θ æ ŋ k s] (дякую)

💡 **Спробуйте ці слова для тесту:**
cat, water, family, beautiful, question

Напиши слово і спробуй! 🎯
    """
    await update.message.reply_text(welcome_text)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g2p_status = "✅ доступний" if G2P_AVAILABLE else "❌ недоступний"
    
    help_text = f"""
📖 **Довідка по боту:**

🎯 **Точна транскрипція:**
• Використовую **g2p-en** для фонетичного аналізу
• Конвертую фонеми в кириличну вимову
• База з {len(WORD_DATABASE)} слів з точними транскрипціями

🔧 **Технології:**
• Фонетичний аналіз: {g2p_status}
• Автоматична конвертація: ✅ увімкнено
• Резервна транскрипція: ✅ увімкнено

📊 **Що таке фонеми?**
Це мовні звуки, які точно описують вимову.
Наприклад: 
• `θ` - звук "th" як в "think"
• `ʃ` - звук "sh" як в "ship"  
• `ŋ` - звук "ng" як в "sing"

⚠️ **Обмеження:**
• Деякі складні слова можуть мати неточну транскрипцію
• Фонеми працюють тільки для англійських слів

💡 **Порада:** Використовуйте /stats для деталей
    """
    await update.message.reply_text(help_text)

# Команда /stats
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_words = len(WORD_DATABASE)
    g2p_status = "🟢 працює" if G2P_AVAILABLE else "🔴 не працює"
    
    stats_text = f"""
📊 **Статистика системи:**

• Слів у базі: **{total_words}**
• Фонетичний аналіз: **{g2p_status}**
• Методи транскрипції: база даних, фонетична, автоматична

🔧 **Технічна інформація:**
• Хостинг: Railway
• Бібліотека: python-telegram-bot + g2p-en
• Мова: Python 3.9

💡 **Як це працює:**
1. Перевірка в базі даних
2. Фонетичний аналіз g2p-en (якщо доступний)  
3. Автоматична транскрипція (резерв)

Система працює стабільно! 🚀
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
    pronunciation, translation, phonemes_text, method = get_accurate_pronunciation(user_message)
    
    # Формуємо відповідь
    response = f"""
🔤 **Слово:** `{user_message}`
🔊 **Вимова:** `{pronunciation}`
🌐 **Переклад:** `{translation}`
"""
    
    # Додаємо фонеми якщо є
    if phonemes_text:
        response += f"📝 **Фонеми:** `[{phonemes_text}]`\n"
    
    response += f"🎯 **Метод:** {method}\n"

    # Додаткові нотатки
    if method == "база даних":
        response += "💡 *Точна транскрипція з перевіреної бази*"
    elif method == "фонетична транскрипція":
        response += "💡 *Точна фонетична транскрипція через g2p-en*"
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
    
    logger.info("🚀 Бот з фонетичною транскрипцією запускається...")
    logger.info(f"📊 База: {len(WORD_DATABASE)} слів, G2P: {G2P_AVAILABLE}")
    application.run_polling()

if __name__ == "__main__":
    main()
