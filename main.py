import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from datetime import datetime, timedelta

# Place your bot token here
BOT_TOKEN = "8044348316:AAF4NohbxnKakZ48SIFRhY3B0JeZVF9QX4U"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Subscription management dictionaries
users_status = {}
allowed_users = set()
vip_users = set()
all_users = {}
all_vip_users = {}

# Initial search counts and restore times
INITIAL_SEARCHES = 5
BASIC_SEARCHES = 5
VIP_SEARCHES = 15
TRIAL_NOTIFICATIONS = 15
restore_timers = {}

# Define start command handler with updated main menu
async def start(update: Update, context: CallbackContext) -> None:
    if update.message:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    
    user_id = update.effective_user.id
    if user_id not in context.user_data:
        context.user_data[user_id] = {"search_count": INITIAL_SEARCHES, "language": "ru"}  # Default to Russian language
    
    language = context.user_data[user_id].get("language", "ru")
    message, reply_markup = get_main_menu_keyboard(language)
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)

# Helper function to get the main menu keyboard
def get_main_menu_keyboard(language="ru"):
    """Returns the main menu message and keyboard based on the selected language."""
    if language == "ru":
        message = (
            "⭐ <b>Gifts Minter - универсальный бот с самым важным функционалом про подарки Telegram. "
            "Пользуйтесь Gifts Minter когда вам удобно и где вам удобно!</b>\n\n"
            "🔍 <b>Поиск подарков</b> - ищите подарки по моделям, фонам и узорам в пару кликов!\n\n"
            "💰 <b>Gifts Mints</b> - следите какие номера у NFT подарков сейчас минтятся, чтобы словить себе самый красивый коллекционный номер\n\n"
            "👁️ <b>Глаз Подарков</b> - узнайте информацию о подарках человека, сколько было отправлено подарков другим людям или сколько подарков скрыто\n\n"
            "Взаимодействуйте с кнопками ниже, чтобы узнать еще больше о функционале бота, мы уверены, вам понравится!"
        )
        keyboard = [
            [InlineKeyboardButton("🤖 Автопокупка подарков", callback_data='autopurchase')],
            [InlineKeyboardButton("🔍 Поиск подарков", callback_data='search'), InlineKeyboardButton("Gifts Mints 💰", callback_data='mints')],
            [InlineKeyboardButton("👀 Глаз Подарков", callback_data='eye'), InlineKeyboardButton("Соглашение 📄", callback_data='agreement')],
            [InlineKeyboardButton("🔔 Всё о подарках", callback_data='notifications'), InlineKeyboardButton("Кабинет 🪪", callback_data='cabinet')],
            [InlineKeyboardButton("⭐ Купить подписку", callback_data='subscribe'), InlineKeyboardButton("Тарифы 🏦", callback_data='tariffs')],
            [InlineKeyboardButton("🌍 Язык / lang", callback_data='language')]
        ]
    else:  # Default to English
        message = (
            "⭐ <b>Gifts Minter - a universal bot with the most important functionality for Telegram gifts. "
            "Use Gifts Minter whenever and wherever you want!</b>\n\n"
            "🔍 <b>Gift Search</b> - search for gifts by models, backgrounds, and patterns in just a few clicks!\n\n"
            "💰 <b>Gifts Mints</b> - track which NFT gift numbers are being minted now to grab the most beautiful collectible number\n\n"
            "👁️ <b>Gift Eye</b> - find out information about a person's gifts, how many gifts they have sent to others, or how many gifts are hidden\n\n"
            "Interact with the buttons below to learn even more about the bot's functionality. We are sure you will love it!"
        )
        keyboard = [
            [InlineKeyboardButton("🤖 Auto Gift Purchase", callback_data='autopurchase')],
            [InlineKeyboardButton("🔍 Gift Search", callback_data='search'), InlineKeyboardButton("Gifts Mints 💰", callback_data='mints')],
            [InlineKeyboardButton("👀 Gift Eye", callback_data='eye'), InlineKeyboardButton("Agreement 📄", callback_data='agreement')],
            [InlineKeyboardButton("🔔 All About Gifts", callback_data='notifications'), InlineKeyboardButton("Cabinet 🪪", callback_data='cabinet')],
            [InlineKeyboardButton("⭐ Buy Subscription", callback_data='subscribe'), InlineKeyboardButton("Plans 🏦", callback_data='tariffs')],
            [InlineKeyboardButton("🌍 Language / Язык", callback_data='language')]
        ]
    return message, InlineKeyboardMarkup(keyboard)

# Define mints command handler with English support
async def mints(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")

    if language == "ru":
        if user_id in vip_users:
            text = (
                "💰 <b>Вступите в частную группу с различными топиками для минтов</b>\n\n"
                "Так как вы обладатель VIP подписки - вы можете вступить в нашу приватную группу, "
                "где каждый подарок рассортирован по топикам в группе, чтобы вам было легче следить за минтами.\n\n"
                "Напишите нашему администратору, перейдя по ссылке - https://t.me/m/k3V2OgINNDUy чтобы он отправил вам ссылку на группу."
            )
        elif user_id in allowed_users:
            text = (
                "💰 <b>Получите ссылку на частную группу</b>\n\n"
                "Напишите нашему администратору перейдя по данной ссылке: https://t.me/m/DKeqXuU7OTM6 "
                "и получите ссылку на частную группу с минтами подарков.\n\n"
                "<b>⭐ Купите VIP подписку чтобы получить доступ к группе, где каждый подарок рассортирован по топикам, "
                "и вам было удобнее следить за минтами.</b>"
            )
        else:
            text = (
                "💰 <b>Gifts Mints доступна для пользователей с Базовой или VIP подпиской</b>\n\n"
                "С данной функцией вы получите доступ к приватной группе с топиками, куда публикуются уведомления о новых минтах подарков.\n\n"
                "Таким образом, вы можете словить для себя красивый номер для вашего подарка.\n\n"
                "⭐ <b>Нажмите кнопку ниже, чтобы перейти к покупке одной из подписок:</b>"
            )
    else:  # English
        if user_id in vip_users:
            text = (
                "💰 <b>Join the private group with various mint topics</b>\n\n"
                "As a VIP subscriber, you can join our private group, "
                "where each gift is sorted by topics in the group to make it easier for you to track mints.\n\n"
                "Contact our administrator via the link - https://t.me/m/k3V2OgINNDUy to receive the group link."
            )
        elif user_id in allowed_users:
            text = (
                "💰 <b>Get the link to the private group</b>\n\n"
                "Contact our administrator via this link: https://t.me/m/DKeqXuU7OTM6 "
                "to receive the link to the private group with gift mints.\n\n"
                "<b>⭐ Purchase a VIP subscription to gain access to the group where each gift is sorted by topics, "
                "making it more convenient to keep track of mints.</b>"
            )
        else:
            text = (
                "💰 <b>Gifts Mints is available for Basic or VIP subscribers</b>\n\n"
                "With this feature, you will gain access to a private group with topics where notifications about new gift mints are published.\n\n"
                "This way, you can catch a nice number for your gift.\n\n"
                "⭐ <b>Click the button below to proceed with purchasing a subscription:</b>"
            )

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Базовая" if language == "ru" else "🎁 Basic", url="https://t.me/buygiftsminterbot"),
         InlineKeyboardButton("⭐ VIP", url="https://t.me/buyvipminterbot")],
        [InlineKeyboardButton("🔙 Назад" if language == "ru" else "🔙 Back", callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define back command handler
async def back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    main_menu_message = (
        "⭐ <b>Gifts Minter - универсальный бот с самым важным функционалом про подарки Telegram. "
        "Пользуйтесь Gifts Minter когда вам удобно и где вам удобно!</b>\n\n"
        "🔍 <b>Поиск подарков</b> - ищите подарки по моделям, фонам и узорам в пару кликов!\n\n"
        "💰 <b>Gifts Mints</b> - следите какие номера у NFT подарков сейчас минтятся, чтобы словить себе самый красивый коллекционный номер\n\n"
        "👁️ <b>Глаз Подарков</b> - узнайте информацию о подарках человека, сколько было отправлено подарков другим людям или сколько подарков скрыто\n\n"
        "Взаимодействуйте с кнопками ниже, чтобы узнать еще больше о функционале бота, мы уверены, вам понравится!"
    )
    keyboard = [
        [InlineKeyboardButton("🤖 Автопокупка подарков", callback_data='autopurchase')],
        [InlineKeyboardButton("🔍 Поиск подарков", callback_data='search'), InlineKeyboardButton("Gifts Mints 💰", callback_data='mints')],
        [InlineKeyboardButton("👁️ Глаз Подарков", callback_data='eye'), InlineKeyboardButton("Соглашение 📄", callback_data='agreement')],
        [InlineKeyboardButton("🔔 Все о подарках", callback_data='notifications'), InlineKeyboardButton("Кабинет 🪪", callback_data='cabinet')],
        [InlineKeyboardButton("⭐ Купить подписку", callback_data='subscribe'), InlineKeyboardButton("Тарифы 🏦", callback_data='tariffs')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(main_menu_message, parse_mode='HTML', reply_markup=reply_markup)

# Define agreement command handler with English support
async def agreement(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    
    if language == "ru":
        text = (
            "<b>📄 Соглашение Gifts Minter</b>\n\n"
            "Используя данный бот, Вы автоматически соглашаетесь с соглашением. "
            "Пожалуйста, ознакомьтесь с ним как можно раньше, чтобы позже - у вас не возникало лишних вопросов или проблем."
        )
        button_text = "Соглашение 📄"
        back_button_text = "🔙 Назад"
    else:
        text = (
            "<b>📄 Gifts Minter Agreement</b>\n\n"
            "By using this bot, you automatically agree to the terms of the agreement. "
            "Please familiarize yourself with it as soon as possible to avoid any questions or issues later."
        )
        button_text = "Agreement 📄"
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(button_text, url="https://telegra.ph/Soglashenie-03-31-3")],
        [InlineKeyboardButton(back_button_text, callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define support command handler with English support
async def support(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    
    if language == "ru":
        text = (
            "🧑‍💻 <b>Остались вопросы? Не стесняйтесь задавать!</b>\n\n"
            "Мы с радостью поможем Вам, если вы столкнулись с чем-то, что невозможно решить самому! "
            "Наши почтовые голуби уже натренированы, чтобы передать Ваш вопрос или проблему."
        )
        ask_question_text = "❓ Задать вопрос"
        report_problem_text = "❗ Сообщить о проблеме"
        back_button_text = "🔙 Назад"
    else:
        text = (
            "🧑‍💻 <b>Have any questions? Feel free to ask!</b>\n\n"
            "We are happy to assist you if you encounter something that you cannot resolve yourself! "
            "Our carrier pigeons are already trained to deliver your question or issue."
        )
        ask_question_text = "❓ Ask a Question"
        report_problem_text = "❗ Report a Problem"
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(ask_question_text, url="https://t.me/m/Pn4A6iU5MjM6")],
        [InlineKeyboardButton(report_problem_text, url="https://t.me/m/nc-Bn-0FYzli")],
        [InlineKeyboardButton(back_button_text, callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define search gifts command handler with English support
async def search_gifts(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    
    if language == "ru":
        text = (
            "🔍 <b>Поиск подарков по параметрам</b>\n\n"
            "• Модель\n"
            "• Фон\n"
            "• Узор\n"
            "• Номер\n"
            "• Владелец\n\n"
            "Перейдите в список ваших чатов, найдите чат с ботом и нажмите кнопку рядом \"Открыть\"\n\n"
            "⭐ <b>Функция доступна только для владельцев VIP плана</b>"
        )
        buy_vip_text = "⭐ Купить VIP план"
        back_button_text = "🔙 Назад"
    else:
        text = (
            "🔍 <b>Search for gifts by parameters</b>\n\n"
            "• Model\n"
            "• Background\n"
            "• Pattern\n"
            "• Number\n"
            "• Owner\n\n"
            "Go to your chats list, find the chat with the bot and click the button next to \"Open\"\n\n"
            "⭐ <b>This feature is only available for VIP plan subscribers</b>"
        )
        buy_vip_text = "⭐ Buy VIP Plan"
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(buy_vip_text, url="https://t.me/buyvipminterbot")],
        [InlineKeyboardButton(back_button_text, callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define autopurchase command handler with English support
async def autopurchase(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")

    if language == "ru":
        text = (
            "🤖 <b>Автопокупка подарков</b>\n\n"
            "<b>Как это работает?</b>\n"
            "Вы настраиваете бота, под нужные вам параметры, а именно:\n\n"
            "• <b>Тираж подарка</b> (саплай)\n"
            "• <b>Мин. и макс. стоимость подарка</b>\n\n"
            "При появлении новых подарков - бот автоматически купит их вам\n\n"
            "Бот полностью бесплатный, но имеет комиссию на пополнение\n\n"
            "🤖 <b>Автопокупка подарков - <a href=\"https://t.me/AutoGiftRobot?start=_tgr_D7aIRUlmM2Yy\">@AutoGiftRobot</a></b>"
        )
    else:  # English
        text = (
            "🤖 <b>Auto Gift Purchase</b>\n\n"
            "<b>How does it work?</b>\n"
            "You configure the bot with the parameters you need, namely:\n\n"
            "• <b>Gift supply</b>\n"
            "• <b>Min. and max. gift price</b>\n\n"
            "When new gifts appear, the bot will automatically buy them for you\n\n"
            "The bot is completely free but has a commission for top-ups\n\n"
            "🤖 <b>Auto Gift Purchase - <a href=\"https://t.me/AutoGiftRobot?start=_tgr_D7aIRUlmM2Yy\">@AutoGiftRobot</a></b>"
        )

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Автопокупка" if language == "ru" else "🤖 Auto Purchase", url="https://t.me/AutoGiftRobot?start=_tgr_D7aIRUlmM2Yy")],
        [InlineKeyboardButton("🔙 Назад" if language == "ru" else "🔙 Back", callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define tariffs command handler with English support
async def tariffs(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")

    if language == "ru":
        text = (
            "🏦 <b>Тарифы Gifts Minter</b>\n\n"
            "Выберите интересующую вас подписку:"
        )
        basic_text = "🎁 Базовая подписка"
        vip_text = "⭐ VIP план"
        back_button_text = "🔙 Назад"
    else:
        text = (
            "🏦 <b>Gifts Minter Plans</b>\n\n"
            "Choose the subscription you are interested in:"
        )
        basic_text = "🎁 Basic Subscription"
        vip_text = "⭐ VIP Plan"
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(basic_text, callback_data='basic_subscription')],
        [InlineKeyboardButton(vip_text, callback_data='vip_plan')],
        [InlineKeyboardButton(back_button_text, callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define basic subscription command handler with English support
async def basic_subscription(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    
    if language == "ru":
        text = (
            "🎁 <b>Базовая подписка</b>\n\n"
            "• Дает доступ к группе Gifts Mints (все минты в одном топике)"
        )
        buy_basic_text = "🎁 Купить Базовую подписку"
        back_button_text = "🔙 Назад"
    else:
        text = (
            "🎁 <b>Basic Subscription</b>\n\n"
            "• Grants access to the Gifts Mints group (all mints in one topic)"
        )
        buy_basic_text = "🎁 Buy Basic Subscription"
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(buy_basic_text, url="https://t.me/buygiftsminterbot")],
        [InlineKeyboardButton(back_button_text, callback_data='tariffs')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define VIP plan command handler with English support
async def vip_plan(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    
    if language == "ru":
        text = (
            "⭐ <b>VIP план</b>\n\n"
            "• Дает доступ к расширенной группе Gifts Mints (каждый минт отдельного подарка распределен по топикам в группе)\n"
            "• Доступ к функции Поиск подарков\n"
            "• Ранний доступ к новым функциям в бот\n\n"
            "⭐ <b>Оформить VIP план можно только после покупки Базовой подписки</b>"
        )
        buy_vip_text = "⭐ Купить VIP план"
        back_button_text = "🔙 Назад"
    else:
        text = (
            "⭐ <b>VIP Plan</b>\n\n"
            "• Grants access to the extended Gifts Mints group (each mint of a gift is sorted by topics in the group)\n"
            "• Access to the Gift Search feature\n"
            "• Early access to new bot features\n\n"
            "⭐ <b>You can subscribe to the VIP plan only after purchasing the Basic subscription</b>"
        )
        buy_vip_text = "⭐ Buy VIP Plan"
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(buy_vip_text, url="https://t.me/buyvipminterbot")],
        [InlineKeyboardButton(back_button_text, callback_data='tariffs')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define notifications command handler with English support
async def notifications(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    
    if language == "ru":
        text = (
            "🔔 <b>Уведомления о новых подарках</b>\n\n"
            'В нашем публичном канале <b><a href="https://t.me/tggiftsnews">Telegram Gifts News</a></b> уведомления о новых подарках публикуются моментально.\n\n'
            "Наш бот по нахождению новых подарков работает без остановки, и без перерывов на покушать."
        )
        button_text = "🔔 Telegram Gifts News"
        back_button_text = "🔙 Назад"
    else:
        text = (
            "🔔 <b>Notifications about new gifts</b>\n\n"
            'In our public channel <b><a href="https://t.me/tggiftsnews">Telegram Gifts News</a></b>, notifications about new gifts are published instantly.\n\n'
            "Our bot for finding new gifts works nonstop and without breaks to eat."
        )
        button_text = "🔔 Telegram Gifts News"
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(button_text, url="https://t.me/tggiftsnews")],
        [InlineKeyboardButton(back_button_text, callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define cabinet command handler with English support
async def cabinet(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    subscription_status = "Не куплена" if language == "ru" else "Not Purchased"
    
    if user_id in vip_users:
        subscription_status = "VIP"
    elif user_id in allowed_users:
        subscription_status = "Базовая" if language == "ru" else "Basic"
    
    if language == "ru":
        text = (
            "🪪 <b>Личный кабинет</b>\n\n"
            f"⭐ <b>Статус подписки:</b> {subscription_status}\n"
            f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>"
        )
        back_button_text = "🔙 Назад"
    else:
        text = (
            "🪪 <b>Personal Cabinet</b>\n\n"
            f"⭐ <b>Subscription Status:</b> {subscription_status}\n"
            f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>"
        )
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(back_button_text, callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define subscribe command handler with English support
async def subscribe(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    
    if language == "ru":
        text = (
            "⭐ <b>Купить подписку в Gifts Minter</b>\n\n"
            "Приобрести Базовую подписку можно здесь: <b>@BuyGiftsMinterBot</b>\n"
            "Приобрести VIP план можно здесь: <b>@BuyVIPMinterBot</b>\n\n"
            "📄 <i>Учтите, что VIP план будет оформлен на ваш аккаунт только после покупки Базовой подписки! "
            "Мы не сможем вернуть вам звезды если вы оформили VIP план, но не имеете Базовой подписки</i>"
        )
        back_button_text = "🔙 Назад"
    else:
        text = (
            "⭐ <b>Subscribe to Gifts Minter</b>\n\n"
            "You can purchase the Basic subscription here: <b>@BuyGiftsMinterBot</b>\n"
            "You can purchase the VIP plan here: <b>@BuyVIPMinterBot</b>\n\n"
            "📄 <i>Please note that the VIP plan will only be activated on your account after purchasing the Basic subscription! "
            "We cannot refund your stars if you subscribe to the VIP plan without having the Basic subscription</i>"
        )
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(back_button_text, callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define back command handler
async def back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    # Main menu message (same as in the start function)
    main_menu_message = (
        "⭐ <b>Gifts Minter - универсальный бот с самым важным функционалом про подарки Telegram. "
        "Пользуйтесь Gifts Minter когда вам удобно и где вам удобно!</b>\n\n"
        "🔍 <b>Поиск подарков</b> - ищите подарки по моделям, фонам и узорам в пару кликов!\n\n"
        "💰 <b>Gifts Mints</b> - следите какие номера у NFT подарков сейчас минтятся, чтобы словить себе самый красивый коллекционный номер\n\n"
        "👁️ <b>Глаз Подарков</b> - узнайте информацию о подарках человека, сколько было отправлено подарков другим людям или сколько подарков скрыто\n\n"
        "Взаимодействуйте с кнопками ниже, чтобы узнать еще больше о функционале бота, мы уверены, вам понравится!"
    )
    # Inline keyboard buttons (same as in the start function)
    keyboard = [
        [InlineKeyboardButton("🤖 Автопокупка подарков", callback_data='autopurchase')],
        [InlineKeyboardButton("🔍 Поиск подарков", callback_data='search'), InlineKeyboardButton("Gifts Mints 💰", callback_data='mints')],
        [InlineKeyboardButton("👁️ Глаз Подарков", callback_data='eye'), InlineKeyboardButton("Соглашение 📄", callback_data='agreement')],
        [InlineKeyboardButton("🔔 Все о подарках", callback_data='notifications'), InlineKeyboardButton("Кабинет 🪪", callback_data='cabinet')],
        [InlineKeyboardButton("⭐ Купить подписку", callback_data='subscribe'), InlineKeyboardButton("Тарифы 🏦", callback_data='tariffs')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(main_menu_message, parse_mode='HTML', reply_markup=reply_markup)

# Define eye command handler with English support
async def eye(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    
    if language == "ru":
        text = (
            "👀 <b>Глаз Подарков - узнайте информацию о человеке</b>\n\n"
            "Наш бот - <b>@EyeOfGiftBot</b>\n\n"
            "Наша администрация не несет ответственности за любую информацию, которую о вас могут узнать в данном бот "
            "(вы можете скрыть информацию о себе, для этого перейдите в бот и введите команду /delete_account)"
        )
        back_button_text = "🔙 Назад"
    else:
        text = (
            "👀 <b>Gift Eye - find out information about a person</b>\n\n"
            "Our bot - <b>@EyeOfGiftBot</b>\n\n"
            "Our administration is not responsible for any information that can be found about you in this bot "
            "(you can hide your information by going to the bot and entering the command /delete_account)."
        )
        back_button_text = "🔙 Back"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(back_button_text, callback_data='back')]
    ])
    await query.edit_message_text(text=text, parse_mode='HTML', reply_markup=reply_markup)

# Define give searches command handler
async def givesearches(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != 1267171169:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    args = context.args
    if len(args) != 2 or not args[0].isdigit() or not args[1].isdigit():
        await update.message.reply_text("Usage: /givesearches <number> <user_id>")
        return
    
    number_of_searches = int(args[0])
    user_id = int(args[1])
    
    # Add searches to the user's balance
    context.user_data.setdefault(user_id, {"search_count": INITIAL_SEARCHES})  # Default to 5 searches if not set
    context.user_data[user_id]["search_count"] += number_of_searches
    
    # Notify the user who received the searches
    await context.bot.send_message(chat_id=user_id, text=(
        f"👁️ <b>Вы получили Поиски на свой баланс!</b>\n\n"
        f"Администратор выдал вам {number_of_searches} Поисков, и вы можете потратить их в бот"
    ), parse_mode='HTML')

    await update.message.reply_text(f"Successfully granted {number_of_searches} searches to user {user_id}.")

# Define addtgid command handler
async def addtgid(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id == 1267171169:  # Replace with your admin ID
        try:
            user_ids = context.args
            added_users = []
            for user_id in user_ids:
                new_user_id = int(user_id)
                allowed_users.add(new_user_id)
                # Reset notifications balance
                context.user_data.setdefault(new_user_id, {"search_count": BASIC_SEARCHES})
                users_status[new_user_id] = {"status": "active"}
                # Get new user username
                new_user = await context.bot.get_chat(new_user_id)
                all_users[new_user_id] = new_user.username
                added_users.append(f"{new_user_id} (@{new_user.username})")
            await update.message.reply_text(f"Пользователям с ID {', '.join(added_users)} предоставлен доступ.")
        except (IndexError, ValueError):
            await update.message.reply_text("Пожалуйста, укажите корректные Telegram user ID.")
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {e}")
    else:
        await update.message.reply_text("У вас нет прав для добавления пользователей.")

# Define addvip command handler
async def addvip(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id == 1267171169:  # Replace with your admin ID
        try:
            user_ids = context.args
            added_vips = []
            for user_id in user_ids:
                new_vip_id = int(user_id)
                vip_users.add(new_vip_id)
                # Reset notifications balance
                context.user_data.setdefault(new_vip_id, {"search_count": VIP_SEARCHES})
                users_status[new_vip_id] = {"status": "active"}
                # Get new VIP user username
                new_vip_user = await context.bot.get_chat(new_vip_id)
                all_vip_users[new_vip_id] = new_vip_user.username
                added_vips.append(f"{new_vip_id} (@{new_vip_user.username})")
            await update.message.reply_text(f"Пользователям с ID {', '.join(added_vips)} предоставлен VIP статус.")
        except (IndexError, ValueError):
            await update.message.reply_text("Пожалуйста, укажите корректные Telegram user ID.")
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {e}")
    else:
        await update.message.reply_text("У вас нет прав для добавления VIP пользователей.")

# Define seepeople command handler
async def seepeople(update: Update, context: CallbackContext) -> None:
    if all_users:
        users_list = "\n\n".join([f"{user_id} (@{username})" for user_id, username in all_users.items()])
        await update.message.reply_text(f"Пользователи с доступом:\n\n{users_list}")
    else:
        await update.message.reply_text("Пока что никому не предоставлен доступ.")

# Define seevips command handler
async def seevips(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id in [1267171169, 6695944947]:  # Replace with your admin IDs
        if all_vip_users:
            vip_list = "\n\n".join([f"{user_id} (@{username})" for user_id, username in all_vip_users.items()])
            await update.message.reply_text(f"VIP пользователи:\n\n{vip_list}")
        else:
            await update.message.reply_text("Пока что никому не предоставлен VIP статус.")
    else:
        await update.message.reply_text("У вас нет прав для просмотра VIP пользователей.")

def restore_searches():
    now = datetime.now()
    for user_id, data in list(context.user_data.items()):
        if user_id in vip_users:
            max_searches = VIP_SEARCHES
        elif user_id in allowed_users:
            max_searches = BASIC_SEARCHES
        else:
            max_searches = INITIAL_SEARCHES

        if data.get("last_restore_time"):
            last_restore_time = datetime.strptime(data["last_restore_time"], "%Y-%m-%d %H:%M:%S")
            if now - last_restore_time >= timedelta(days=1):
                data["search_count"] = max_searches
                data["last_restore_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["last_restore_time"] = now.strftime("%Y-%m-%d %H:%M:%S")

# Define language selection handler
async def language(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=(
            "🇷🇺 <b>Выберите язык:</b>\n\n"
            "🇺🇸 <b>Select language:</b>"
        ),
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇷🇺 Русский", callback_data='set_language_ru'), InlineKeyboardButton("English 🇺🇸", callback_data='set_language_en')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back')]
        ])
    )

# Define back command handler
async def back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    language = context.user_data.get(user_id, {}).get("language", "ru")
    message, reply_markup = get_main_menu_keyboard(language)
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)

# Define language setters
async def set_language_ru(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    context.user_data[user_id]["language"] = "ru"
    await query.answer()
    message, reply_markup = get_main_menu_keyboard(language="ru")
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)

async def set_language_en(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = update.effective_user.id
    context.user_data[user_id]["language"] = "en"
    await query.answer()
    message, reply_markup = get_main_menu_keyboard(language="en")
    await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)

def main() -> None:
    # Initialize the bot and dispatcher
    application = Application.builder().token(BOT_TOKEN).build()

    # Register the handlers
    application.add_handler(CallbackQueryHandler(language, pattern='^language$'))
    application.add_handler(CallbackQueryHandler(set_language_ru, pattern='^set_language_ru$'))
    application.add_handler(CallbackQueryHandler(set_language_en, pattern='^set_language_en$'))
    application.add_handler(CallbackQueryHandler(back, pattern='^back$'))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(mints, pattern='^mints$'))
    application.add_handler(CallbackQueryHandler(back, pattern='^back$'))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(agreement, pattern='^agreement$'))
    application.add_handler(CallbackQueryHandler(support, pattern='^support$'))
    application.add_handler(CallbackQueryHandler(search_gifts, pattern='^search$'))
    application.add_handler(CallbackQueryHandler(autopurchase, pattern='^autopurchase$'))
    application.add_handler(CallbackQueryHandler(tariffs, pattern='^tariffs$'))
    application.add_handler(CallbackQueryHandler(basic_subscription, pattern='^basic_subscription$'))
    application.add_handler(CallbackQueryHandler(vip_plan, pattern='^vip_plan$'))
    application.add_handler(CallbackQueryHandler(notifications, pattern='^notifications$'))
    application.add_handler(CallbackQueryHandler(cabinet, pattern='^cabinet$'))
    application.add_handler(CallbackQueryHandler(subscribe, pattern='^subscribe$'))
    application.add_handler(CallbackQueryHandler(back, pattern='^back$'))
    application.add_handler(CallbackQueryHandler(eye, pattern='^eye$'))
    application.add_handler(CommandHandler("givesearches", givesearches))
    application.add_handler(CommandHandler("addtgid", addtgid))
    application.add_handler(CommandHandler("addvip", addvip))
    application.add_handler(CommandHandler("seepeople", seepeople))
    application.add_handler(CommandHandler("seevips", seevips))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()