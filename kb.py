from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo
import db


menu = [
    [InlineKeyboardButton(text="👕 Каталог",  callback_data="katalog"),
    InlineKeyboardButton(text="🟣 Примерить", callback_data="dress")],
    [InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
    InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
    [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
    InlineKeyboardButton(text="🖼 Галерея", callback_data="gallery")],
    [InlineKeyboardButton(text="🔎 Помощь", callback_data="help"),
    InlineKeyboardButton(text="🛠 Тех.Поддержка", callback_data="tech_helper")],
    [InlineKeyboardButton(text="💳 Купить примерки", callback_data="shop_prem")]
]



admin_tech_id = 967026526
tech = [
    [InlineKeyboardButton(text="📩 Написать в поддержку", url=f"tg://user?id={admin_tech_id}")],
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]






profile = [
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu"),
     InlineKeyboardButton(text="✏️ Изменить данные", callback_data="menu")]
]





profkb1 = [
    [InlineKeyboardButton(text="Создать профиль", callback_data="profile_h1"),
     InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]




profkb2 = [
    [InlineKeyboardButton(text="Изменить профиль", callback_data="profile_h1"),
     InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]



dress_new = [
    [InlineKeyboardButton(text="📸 Добавить фото", callback_data="add_photo"),
     InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]

dress_last = [
    [InlineKeyboardButton(text="⏩ Продолжить", callback_data="add_clothes"),
     InlineKeyboardButton(text="📸 Изменить фото", callback_data="add_photo")],
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]

clothes_photo = [
    [InlineKeyboardButton(text="Добавить одежду из каталога 🚫", callback_data="add_photo_from_webapp")],
    [InlineKeyboardButton(text="Добавить свою одежду", callback_data="add_photo_from_person")]
]


defult = [
    [InlineKeyboardButton(text="Купить токены", callback_data="buy_tokens")],
    [InlineKeyboardButton(text="DRESSPREM SILVER|550₽", callback_data="buy_prem_silver")],
    [InlineKeyboardButton(text="DRESSPREM GOLD|750₽", callback_data="buy_prem_gold")],
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]
silver = [
    [InlineKeyboardButton(text="Купить токены", callback_data="buy_tokens")],
    [InlineKeyboardButton(text="DRESSPREM GOLD|200₽", callback_data="update_to_gold")],
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]
gold = [
    [InlineKeyboardButton(text="Купить токены", callback_data="buy_tokens")],
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]

tokens = [
    [InlineKeyboardButton(text=" 100⭐️|20₽", callback_data="buy_tokens_100"),
     InlineKeyboardButton(text=" 300⭐️|55₽", callback_data="buy_tokens_300")],
    [InlineKeyboardButton(text=" 500⭐️|90₽", callback_data="buy_tokens_500"),
     InlineKeyboardButton(text=" 750⭐️|140₽", callback_data="buy_tokens_750")],
    [InlineKeyboardButton(text="1000⭐️|180₽", callback_data="buy_tokens_1000"),
     InlineKeyboardButton(text="1500⭐️|270₽", callback_data="buy_tokens_1500")],
    [InlineKeyboardButton(text="2000⭐️|350₽", callback_data="buy_tokens_2000"),
     InlineKeyboardButton(text="3000⭐️|530₽", callback_data="buy_tokens_3000")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="shop_prem")]
]

balance = [[InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="shop_prem")],
          [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
]
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])
to_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Меню", callback_data="menu")]])

iexit_kb1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👁‍ Скрыть", callback_data="menu_1")]])

convert = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Запустить примерку 🧬", callback_data="convert_AI")]])


cph = InlineKeyboardMarkup(inline_keyboard=clothes_photo)
dn = InlineKeyboardMarkup(inline_keyboard=dress_new)
dl = InlineKeyboardMarkup(inline_keyboard=dress_last)
menu = InlineKeyboardMarkup(inline_keyboard=menu)
btn_tech = InlineKeyboardMarkup(inline_keyboard=tech)
profile = InlineKeyboardMarkup(inline_keyboard=profile)
profile_add = InlineKeyboardMarkup(inline_keyboard=profkb1)
profile_edit = InlineKeyboardMarkup(inline_keyboard=profkb2)


shop_kb_defult = InlineKeyboardMarkup(inline_keyboard=defult)
shop_kb_silver = InlineKeyboardMarkup(inline_keyboard=silver)
shop_kb_gold = InlineKeyboardMarkup(inline_keyboard=gold)

tokens_kb = InlineKeyboardMarkup(inline_keyboard=tokens)

balance_kb = InlineKeyboardMarkup(inline_keyboard=balance)




def settings_d(user_id):
    with db.connection.cursor() as cursor: #db - ваше подключение к БД
        cursor.execute("SELECT * FROM users_settings WHERE id = %s", (user_id))
        result = cursor.fetchone()
        if result['notifications_enabled'] == 0:
            notifications_enabled = True
        else:
            notifications_enabled = False

        if result['save_to_gallery'] == 0:
            save_to_gallery = True
        else:
            save_to_gallery = False

    if notifications_enabled == True:
        emoji = "🔔"
    else:
        emoji = "🔕"
    text = f"{emoji} Уведомления"

    if save_to_gallery == True:
        emoji2 = "📗"
    else:
        emoji2 = "📕"
    text2 = f"{emoji2} Сохранять обработки"

    settings_k = [
        [InlineKeyboardButton(text=text, callback_data="mute"),
         InlineKeyboardButton(text=text2, callback_data="save_photo")],
        [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]

    ]
    return InlineKeyboardMarkup(inline_keyboard=settings_k)
# web_app=WebAppInfo('https://<your_domain>')