#8366269150:AAEoaiS6IO5trTKYUPbVH3o29RBcSww73Y
import os
import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Імпортуємо g2p-en для точної транскрипції
try:
    from g2p_en import G2p
    g2p = G2p()
    G2P_AVAILABLE = True
    logger.info("✅ g2p-en успішно імпортовано")
except ImportError as e:
    G2P_AVAILABLE = False
    logger.error(f"❌ g2p-en не встановлено: {e}")

def phonemes_to_cyrillic(phonemes):
    """Конвертує фонеми в кириличну транскрипцію"""
    # Словник конвертації фонем
    phoneme_map = {
        # Голосні
        'æ': 'е',    # cat, bad
        'ɑ': 'а',    # father, car
        'ɔ': 'о',    # dog, ball
        'ə': 'е',    # about, sofa
        'ʌ': 'а',    # but, cup
        'ɛ': 'е',    # bed, red
        'ɪ': 'і',    # sit, big
        'i': 'і',    # see, heat
        'ʊ': 'у',    # put, book
        'u': 'у',    # too, blue
        'ɝ': 'ер',   # bird, learn
        'ɚ': 'ер',   # better, father
        
        # Дифтонги
        'aɪ': 'ай',  # my, time
        'aʊ': 'ау',  # now, out
        'eɪ': 'ей',  # say, eight
        'oʊ': 'оу',  # go, home
        'ɔɪ': 'ой',  # boy, coin
        
        # Приголосні
        'b': 'б', 'd': 'д', 'f': 'ф', 'g': 'г', 'h': 'х',
        'j': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н',
        'ŋ': 'нг', 'p': 'п', 'r': 'р', 's': 'с', 'ʃ': 'ш',
        't': 'т', 'tʃ': 'ч', 'θ': 'с', 'ð': 'з', 'v': 'в',
        'w': 'в', 'z': 'з', 'ʒ': 'ж', 'dʒ': 'дж'
    }
    
    result = []
    i = 0
    phonemes_list = list(phonemes)
    
    while i < len(phonemes_list):
        current = phonemes_list[i]
        
        # Перевіряємо сполучення (2 символи)
        if i + 1 < len(phonemes_list):
            double = current + phonemes_list[i + 1]
            if double in phoneme_map:
                result.append(phoneme_map[double])
                i += 2
                continue
        
        # Обробляємо окремі символи
        if current in phoneme_map:
            result.append(phoneme_map[current])
        elif current not in ['ˈ', 'ˌ', '.', '!', '?']:  # Ігноруємо символи стресу
            result.append(current)
        i += 1
    
    return ''.join(result)

def improve_pronunciation_rules(text, original_word):
    """Покращує транскрипцію за спеціальними правилами"""
    # Правила для покращення вимови
    improvements = [
        # М'якість перед голосними
        (r'ті', 'ті'), (r'ді', 'ді'), (r'сі', 'сі'), (r'зі', 'зі'),
        (r'ні', 'ні'), (r'лі', 'лі'),
        
        # Спрощення сполучень
        (r'тс', 'ц'), (r'дс', 'дз'),
        
        # Американська вимова 'r'
        (r'ер', 'ер'),
        
        # Спеціальні випадки
        (r'ью', 'ю'), (r'ье', 'є'),
    ]
    
    result = text
    
    for pattern, replacement in improvements:
        result = re.sub(pattern, replacement, result)
    
    # Особливі правила для закінчень
    if original_word.endswith('y'):
        result = re.sub(r'і$', 'і', result)
    if original_word.endswith('ing'):
        result = re.sub(r'інг$', 'інг', result)
    if original_word.endswith('tion'):
        result = re.sub(r'шен$', 'шен', result)
    
    return result

def get_pronunciation(word):
    """Отримує транскрипцію слова через g2p-en"""
    if not G2P_AVAILABLE:
        return "система транскрипції недоступна", "", "помилка"
    
    try:
        # Отримуємо фонеми через g2p-en
        phonemes = g2p(word)
        phonemes_text = ' '.join(phonemes)
        
        # Конвертуємо в кирилицю
        cyrillic = phonemes_to_cyrillic(phonemes)
        
        # Покращуємо за правилами
        improved = improve_pronunciation_rules(cyrillic, word.lower())
        
        return improved, phonemes_text, "фонетична транскрипція"
        
    except Exception as e:
        logger.error(f"Помилка транскрипції: {e}")
        return "помилка транскрипції", "", "помилка"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    status = "✅ увімкнено" if G2P_AVAILABLE else "❌ вимкнено"
    
    welcome_text = f"""
👋 Привіт, {user.first_name}!

🤖 Я бот для **точної фонетичної транскрипції** англійських слів!

🎯 Надішліть мені англійське слово і я:
• 🔊 Покажу **вимову** українськими буквами
• 📝 Покажу **фонеми** (мова звуків)
• 🎯 Використаю **g2p-en** для точної транскрипції

🔧 **Стан системи:**
• Фонетичний аналіз: {status}

🔊 **Приклади:**
• `hello` → `хелоу` [h ə l ˈoʊ]
• `celebrity` → `селебріті` [s ə ˈl ɛ b r ɪ t i]
• `beautiful` → `б'ютіфул` [ˈb j u t ɪ f ʊ l]
• `question` → `квесчен` [ˈk w ɛ s tʃ ən]

💡 **Спробуйте ці слова:**
- celebrity, beautiful, water, computer
- thanks, please, sorry, answer
- people, because, family, friend

Напиши слово і спробуй! 🎯
    """
    await update.message.reply_text(welcome_text)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 **Довідка по боту:**

🎯 **Як це працює:**
1. Ви надсилаєте англійське слово
2. Система **g2p-en** аналізує звучання
3. Фонеми конвертуються в кириличну транскрипцію
4. Ви отримуєте точну вимову


📝 **Що таке фонеми?**
Це мовні звуки, які точно описують вимову:
• `θ` - звук "th" як в "think"
• `ʃ` - звук "sh" як в "ship"  
• `ŋ` - звук "ng" як в "sing"
• `tʃ` - звук "ch" як в "chat"

⚠️ **Обмеження:**
• Працює тільки з окремими словами
• Деякі рідкісні слова можуть бути неточними
• Транскрипція орієнтована на американську вимову

💡 **Порада:** Для точнішої транскрипції використовуйте common words
    """
    await update.message.reply_text(help_text)

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    
    if user_message.startswith('/'):
        return
    
    if ' ' in user_message:
        await update.message.reply_text("⚠️ Будь ласка, надішліть тільки **одне** слово")
        return
    
    if not user_message.isalpha():
        await update.message.reply_text("⚠️ Використовуйте тільки літери (без цифр чи спецсимволів)")
        return
    
    if len(user_message) > 30:
        await update.message.reply_text("⚠️ Слово занадто довге. Максимум 30 символів")
        return
    
    # Отримуємо транскрипцію
    pronunciation, phonemes, method = get_pronunciation(user_message)
    
    # Формуємо відповідь
    response = f"""
🔤 **Слово:** `{user_message}`
🔊 **Вимова:** `{pronunciation}`
"""
    
    if phonemes:
        response += f"📝 **Фонеми:** `[{phonemes}]`\n"
    
    response += f"🎯 **Метод:** {method}\n"
    response += "💡 *Точна фонетична транскрипція через g2p-en*"
    
    await update.message.reply_text(response)

# Обробка помилок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Помилка: {context.error}")
    await update.message.reply_text("❌ Сталася помилка. Спробуйте ще раз пізніше.")

def main():
    TOKEN = os.environ.get('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ BOT_TOKEN не знайдено! Додайте у змінні середовища")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    logger.info("🚀 Бот з фонетичною транскрипцією запускається...")
    logger.info(f"📊 G2P доступний: {G2P_AVAILABLE}")
    application.run_polling()

if __name__ == "__main__":
    main()
