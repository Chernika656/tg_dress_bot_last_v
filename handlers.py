import asyncio
import json
import os
from pyexpat.errors import messages
import mysql.connector
from aiogram import F, Router, types
from aiogram.enums import ContentType




from aiogram.filters import Command, CommandObject

from aiogram.types import Message, WebAppInfo, FSInputFile, URLInputFile, BufferedInputFile, InputMediaPhoto, \
    InputMedia, InputFile
from aiogram import flags
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
import asyncpg
from pymysql import IntegrityError
from aiogram import Bot
import time
import datetime
import random

import kb
import prices
import text
import db
import admin
import states
import img
import oot_diffusion
import config
import admin

router = Router()
Bot_h = Bot(token=config.BOT_TOKEN)

# РАССЫЛКА СООБЩЕНИЙ
@router.message(Command("send_all"))
async def cmd_settimer(msg: Message, command: CommandObject):
    if admin.admins_db_id(msg.from_user.id):
        with db.connection.cursor() as cursor:
            cursor.execute('SELECT id FROM users_settings WHERE notifications_enabled = %s', (0))
            result = cursor.fetchall()
            for elem in result:
                await Bot_h.send_message(elem['id'], text=command.args)



# СТАРТ
@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.to_menu)
    user_id = msg.from_user.id
    with db.connection.cursor() as cursor:
        cursor.execute(f"INSERT IGNORE INTO profile (id) VALUES ({user_id})")
        cursor.execute(f"INSERT IGNORE INTO users_settings (id) VALUES ({user_id})")
        cursor.execute(f"INSERT IGNORE INTO photo_user (id) VALUES ({user_id})")
        db.connection.commit()

# МЕНЮ
@router.callback_query(F.data == "menu")
async def menu2(clbck: CallbackQuery, state: FSMContext):
    global msg_m
    media = InputMediaPhoto(media=img.menu)
    await clbck.message.edit_media(media=media)
    await clbck.message.edit_reply_markup(reply_markup=kb.menu)


# КАТАЛОГ
@router.callback_query(F.data == "katalog")
async def katalog_integration(clbck: CallbackQuery, state: FSMContext):
    media = InputMediaPhoto(media=img.katalog, caption=text.web_app)
    await clbck.message.edit_media(media=media)
    await clbck.message.edit_reply_markup(reply_markup=kb.iexit_kb)


# ТЕХ ПОДДЕРЖКА
@router.callback_query(F.data == "tech_helper")
async def tech_help(clbck: CallbackQuery, state: FSMContext):
    media = InputMediaPhoto(media=img.techi, caption=text.tech)
    await clbck.message.edit_media(media=media)
    await clbck.message.edit_reply_markup(reply_markup=kb.btn_tech)






# ПРОФИЛЬ
@router.callback_query(F.data == "profile")
async def profile_first(clbck: CallbackQuery, state: FSMContext):
    with db.connection.cursor() as cursor:
        cursor.execute(f"SELECT height, weight, shoe_size, 1 FROM profile WHERE id = {clbck.from_user.id}")
        result = cursor.fetchone()
        if result['height'] != 0:
            prof = f'{clbck.from_user.full_name}, твой профиль.⬇️\n\n ID:{clbck.from_user.id}\n\n Рост: {result["height"]} см.\n Вес: {result["weight"]} кг.\n Размер обуви: {result["shoe_size"]}'
            media = InputMediaPhoto(media=img.profi, caption=prof)
            await clbck.message.edit_media(media=media)
            await clbck.message.edit_reply_markup(reply_markup=kb.profile_edit)
        else:
            media1 = InputMediaPhoto(media=img.profi, caption=text.text_profile)
            await clbck.message.edit_media(media=media1)
            await clbck.message.edit_reply_markup(reply_markup=kb.profile_add)






# ЗАПОЛНИТЬ АНКЕТУ
@router.callback_query(F.data == "profile_h1")
async def profile_1(clbck: CallbackQuery, state: FSMContext):
    global msg
    media1 = InputMediaPhoto(media=img.profi, caption=text.profile_text1)
    msg = await clbck.message.edit_media(media=media1)
    await state.update_data(msg_id1=msg.message_id)
    await state.set_state(states.ProfileStates.height)


# РОСТ
@router.message(states.ProfileStates.height)
async def process_height(msg: types.Message, state: FSMContext):
    global msg2
    height = msg.text
    await state.update_data(height=height)
    msg2 = await msg.answer(text.profile_text2)
    await state.update_data(msg_id2=msg2.message_id)
    await state.set_state(states.ProfileStates.weight)
    await msg.delete()


# ВЕС
@router.message(states.ProfileStates.weight)
async def process_weight(message: types.Message, state: FSMContext):
    global msg3
    weight = message.text
    await state.update_data(weight=weight)
    msg3 = await message.answer(text.profile_text3)
    await state.update_data(msg_id3=msg3.message_id)
    await state.set_state(states.ProfileStates.shoesize)
    await message.delete()


# РАЗМЕР
@router.message(states.ProfileStates.shoesize)
async def process_shoesize(message: types.Message, state: FSMContext):
    global msg
    global msg2
    global msg3
    shoesize = message.text
    await state.update_data(shoesize=shoesize)
    data = await state.get_data()
    await message.delete()
    try:
        with db.connection.cursor() as cursor:
            cursor.execute("UPDATE profile SET height = %s, weight = %s, shoe_size = %s WHERE id = %s",
                               (data['height'], data['weight'], shoesize, message.from_user.id))
            db.connection.commit()
            await message.answer(f"✅ Данные сохранены:\nРост: {data['height']}\nВес: {data['weight']}\nРазмер обуви: {shoesize}", reply_markup=kb.iexit_kb)

            await msg.delete()
            await msg2.delete()
            await msg3.delete()

            await state.clear()
    except asyncpg.exceptions.PostgresError as e:
        print(f"Ошибка при сохранении данных в базу данных: {e}")
        await state.clear()
        return False
    return True





# АДМИН-КЛЮЧ
@router.message(Command("hg7hf8h8y2rb2", prefix="$"))
async def admin_id(msg: Message):
    admin.add_admin(msg.from_user.id)
    msg1 = await msg.answer(text.admin_text.format(name=msg.from_user.full_name))
    await asyncio.sleep(5)
    await msg.delete()
    await asyncio.sleep(5)
    await msg1.delete()



#НАСТРОЙКИ
@router.callback_query(F.data == "settings")
async def setting(clbck: CallbackQuery, state: FSMContext):
    media1 = InputMediaPhoto(media=img.settingsi)
    await clbck.message.edit_media(media=media1)
    await clbck.message.edit_reply_markup(reply_markup=kb.settings_d(clbck.from_user.id))

#СОХРАНЯТЬ ФОТО
@router.callback_query(F.data == "save_photo")
async def save(clbck: CallbackQuery, state: FSMContext):
    user_id = clbck.from_user.id
    with db.connection.cursor() as cursor: #db - ваше подключение к БД
        cursor.execute("SELECT save_to_gallery FROM users_settings WHERE id = %s", (user_id))
        result = cursor.fetchone()
        if result['save_to_gallery'] == 0:
            save_to_gallery = 1
        else:
            save_to_gallery = 0

    # Обновляем состояние в базе данных
    with db.connection.cursor() as cursor:
        cursor.execute("UPDATE users_settings SET save_to_gallery = %s WHERE id = %s", (save_to_gallery, user_id))
        db.connection.commit()

    await  update_save_button(clbck, save_to_gallery)


# ОБНОВЛЕНИЕ ИНЛАЙН КЛАВИАТУРЫ ПРИ НАЖАТИИ НА КНОПКУ СОХРАНЕНИЯ В ГАЛЕРЕЮ
async def update_save_button(clbck: CallbackQuery, save_to_gallery: int):
    markup = kb.settings_d(clbck.from_user.id) # Передаем ID пользователя для обновления
    await clbck.message.edit_reply_markup(reply_markup=markup)


#УВЕДОМЛЕНИЯ
@router.callback_query(F.data == "mute")
async def mute(clbck: CallbackQuery, state: FSMContext):
    user_id = clbck.from_user.id
    # Получаем текущее состояние уведомлений из базы данных
    with db.connection.cursor() as cursor: #db - ваше подключение к БД
        cursor.execute("SELECT notifications_enabled FROM users_settings WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if result['notifications_enabled'] == 0:
            notifications_enabled = 1
        else:
            notifications_enabled = 0

    # Обновляем состояние в базе данных
    with db.connection.cursor() as cursor:
        cursor.execute("UPDATE users_settings SET notifications_enabled = %s WHERE id = %s", (notifications_enabled, user_id))
        db.connection.commit()

    await  update_mute_button(clbck, notifications_enabled)


# ОБНОВЛЕНИЕ ИНЛАЙН КЛАВИАТУРЫ ПРИ НАЖАТИИ НА КНОПКУ УВЕДОМЛЕНИЯ
async def update_mute_button(clbck: CallbackQuery, notifications_enabled: int):
    markup = kb.settings_d(clbck.from_user.id) # Передаем ID пользователя для обновления
    await clbck.message.edit_reply_markup(reply_markup=markup)



#ПОМОЩЬ
@router.callback_query(F.data == "help")
async def help_1(clbck: CallbackQuery, state: FSMContext):
    media = InputMediaPhoto(media=img.help, caption=text.helper)
    await clbck.message.edit_media(media=media)
    await clbck.message.edit_reply_markup(reply_markup=kb.iexit_kb)


# ГАЛЕРЕЯ
@router.callback_query(F.data == "gallery")
async def gallery_hide(clbck: CallbackQuery, state: FSMContext):
    with db.connection.cursor() as cursor:
        cursor.execute('SELECT gallery FROM photo_user WHERE id = %s', (clbck.from_user.id))
        result = cursor.fetchone()
        if result["gallery"].count('|') == 1 or result["gallery"].count('|') == 0:
            photo = result['gallery'].replace('|', '')
            media = InputMediaPhoto(media=photo)
            await clbck.message.edit_media(media=media)
            await clbck.message.edit_reply_markup(reply_markup=kb.iexit_kb)



# ПРИМЕРКА
@router.callback_query(F.data == "dress")
async def dress(clbck: CallbackQuery, state: FSMContext):
    global msg_m
    msg_m = 0
    with db.connection.cursor() as cursor:
        cursor.execute(f"SELECT user_photo FROM photo_user WHERE id = {clbck.from_user.id}")
        result = cursor.fetchone()
    if result['user_photo'] == '0':
        media = InputMediaPhoto(media=img.dress_new, caption=text.dress_new_text)
        msg_m = await clbck.message.edit_media(media=media)
        await clbck.message.edit_reply_markup(reply_markup=kb.dn)
    else:
        media = InputMediaPhoto(media=result['user_photo'], caption=text.dress_text)
        msg_m = await clbck.message.edit_media(media=media)
        await clbck.message.edit_reply_markup(reply_markup=kb.dl)


# НАЧАЛО СОСТОЯНИЯ ДЛЯ ОТПРАВКИ ФОТО ПОЛЬЗОВАТЕЛЯ
@router.callback_query(lambda c: c.data == 'add_photo')
async def process_callback_add_photo(query: types.CallbackQuery, state: FSMContext):
    global msg_m
    await query.answer(text.edit_foto, show_alert=True)
    await state.set_state(states.Form.wait_for_photo)
    await msg_m.delete()





# ПРИЁМ ФОТО ОТ ПОЛЬЗОВАТЕЛЯ
@router.message(F.photo, states.Form.wait_for_photo)
async def process_photo_change(message: types.Message, state: FSMContext):
    global msg_m
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        await state.update_data(key_img=file_id)
        with db.connection.cursor() as cursor:
            cursor.execute("UPDATE photo_user SET user_photo = %s WHERE id = %s", (file_id, message.from_user.id))
            db.connection.commit()
        await state.clear() #Сбрасываем состояние после успешного изменения


        await asyncio.sleep(3)
        await message.delete()
        msg_m = await message.answer_photo(photo=file_id, caption=text.dress_true, reply_markup=kb.dl)
    else:
        msg5 = await message.reply("Это не фото, попробуйте ещё раз")
        await asyncio.sleep(3)
        await msg5.delete()
        await message.delete()


# ВЫБОР ОТКУДА БУДЕТ ДОБАВЛЕНА ОДЕЖДА
@router.callback_query(F.data == "add_clothes")
async def add_clothes_photo(clbck: CallbackQuery, state: FSMContext):
    global msg_p
    media = InputMediaPhoto(media=img.profi)
    msg_p = await clbck.message.edit_media(media=media)
    await clbck.message.edit_reply_markup(reply_markup=kb.cph)


# НАЧАЛО СОСТОЯНИЯ ДЛЯ ОТПРАВКИ ФОТО ОДЕЖДЫ
@router.callback_query(F.data == "add_photo_from_person")
async def clothes_from_user(clbck: CallbackQuery, state: FSMContext):
    global msg_p
    await clbck.answer(text.clothes_from_ur, show_alert=True)
    await state.set_state(states.Form.wait_for_photo1) # Устанавливаем состояние ожидания фото
    await msg_p.delete()


# ПРИЁМ ФОТО ОТ ПОЛЬЗОВАТЕЛЯ
@router.message(F.photo, states.Form.wait_for_photo1)
async def process_user_photo(message: types.Message, state: FSMContext, bot: Bot_h):
    global msg_g1
    global msg_g2
    global msg_t
    user_photo = message.photo[-1]
    user_photo_file_id = user_photo.file_id
    await message.delete()
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT user_photo FROM photo_user WHERE id = %s", (message.from_user.id,))
        result = cursor.fetchone()

    if result is None:
        await message.answer("Фотография пользователя не найдена в базе данных.")
        return

    existing_photo_file_id = result['user_photo']
    if not isinstance(existing_photo_file_id, str):
        await message.answer("Неверный формат данных в базе данных.")
        return


    msg_g = await message.answer_media_group([
        InputMediaPhoto(media=existing_photo_file_id),
        InputMediaPhoto(media=user_photo_file_id)
    ])
    msg_g1 = msg_g[0]
    msg_g2 = msg_g[1]
    msg_t = await message.answer("Альбом для примерки ⬆️", reply_markup=kb.convert) #kb.convert должен генерировать кнопки с callback_data
    try:
        await add_photo_to_db(message.from_user.id, user_photo_file_id)
        if not user_photo_file_id:
            await message.answer("Ошибка загрузки фотографии одежды.")
            return
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
        print(f"Error: {e}") # для отладки
        await state.clear()

# ВЫБОР СПОСОБА ОПЛАТЫ ОБРАБОТКИ (ТОКЕНЫ/БЕСПЛАТНЫЕ ОБРАБОТКИ)
def sub_or_prem(user_id):
    with db.connection.cursor() as cursor:
        qy = "SELECT * FROM users_settings WHERE id = %s"
        cursor.execute(qy, user_id)
        result = cursor.fetchone()
        rd = random.randint(50,100)
        if result['prem_tok_day'] > 0:
            return 1
        elif result['tokens'] >= rd:
            return rd
        else:
            return False

# ОБРАБОТКА ФОТО
@router.callback_query(F.data == 'convert_AI')
async def convertation(clbck: CallbackQuery, state: FSMContext, bot: Bot_h):
    global msg_g1
    global msg_g2
    global msg_t
    await msg_g1.delete()
    await msg_g2.delete()
    await msg_t.delete()
    msg_g1, msg_g2, msg_t = 0, 0, 0
    sop = sub_or_prem(clbck.from_user.id)
    if sop != False:
        await clbck.answer('Обработка началась... ~ 1 min', show_alert=True)

        with db.connection.cursor() as cursor:
            add_photo_query1 = "SELECT * FROM photo_user WHERE id = %s"
            data = clbck.from_user.id
            cursor.execute(add_photo_query1, data)
            f1 = cursor.fetchone()
            user_photo_path = await download_file(bot, f1['user_photo'], "user_photo.jpg")
            garment_photo_path = await download_file(bot, f1['photo_from_user'], "garment_photo.jpg")

        processed_image_path = await asyncio.to_thread(oot_diffusion.AI_CONVERT, user_photo_path, garment_photo_path)
        for elem in processed_image_path:
            image_from_url = FSInputFile(elem['image'])
            result = await clbck.message.answer_photo(
                image_from_url,
                caption=f"Обработанное изображение\n Было потрачено: {sop}", reply_markup=kb.iexit_kb
            )
            photo = result.photo[-1]
            file_id = photo.file_id
            with (db.connection.cursor() as cursor):
                add_photo_to_gallery = "SELECT * FROM users_settings WHERE id = %s"
                cursor.execute(add_photo_to_gallery, data)
                res = cursor.fetchone()
                gallery_value = 0
                if res['save_to_gallery'] == 0:
                    if res['stat'] == 'defult_user':
                        gallery_value = file_id + "|"
                    if (f1['gallery'] == 0 or (len(f1['gallery'].split('|')) < 5)) and res['stat'] == 'silver_user':
                        if f1['gallery'] == 0:
                            gallery_value = file_id + "|"
                        else:
                            gallery_value = file_id + "|" + f1['gallery']
                    if (f1['gallery'] == 0 or (len(f1['gallery'].split('|')) < 10)) and res['stat'] == 'silver_user':
                        if f1['gallery'] == 0:
                            gallery_value = file_id + "|"
                        else:
                            gallery_value = file_id + "|" + f1['gallery']
            if gallery_value != 0:
                with db.connection.cursor() as cursor:
                    cursor.execute("UPDATE photo_user SET gallery = %s WHERE id = %s", (gallery_value, data))
                    db.connection.commit()
        os.remove(user_photo_path)
        os.remove(garment_photo_path)
        with db.connection.cursor() as cursor:
            if sop >= 50:
                cursor.execute('UPDATE users_settings SET tokens = tokens - %s WHERE id = %s', (sop, data))
                db.connection.commit()
            else:
                cursor.execute('UPDATE users_settings SET prem_tok_day = prem_tok_day - %s WHERE id = %s', (sop, data))
                db.connection.commit()
    else:
        await (clbck.message.answer_photo(photo=img.DEFULT,
                                caption="🙁 У вас не хватает токенов на обработку.", reply_markup=kb.balance_kb))

# СКАЧИВАНИЕ ФАЙЛОВ ДЛЯ ЗАГРУЗКИ В НЕЙРОСЕТЬ
async def download_file(bot: Bot_h, file_id, filename: str) -> str | None:
    try:
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_path_local = os.path.join(os.getcwd(), filename) # Сохранение в текущем каталоге
        await bot.download_file(file_path, file_path_local)
        return file_path_local
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return None

# ДОБАВЛЕНИЕ ФОТО В БД
async def add_photo_to_db(user_id: int, photo_path):
    try:
        with db.connection.cursor() as cursor:
            add_photo_query = "UPDATE photo_user SET photo_from_user = %s WHERE id = %s"
            data = (photo_path, user_id)
            cursor.execute(add_photo_query, data)
            db.connection.commit()
            print(f"Фотография добавлена в базу данных для пользователя {user_id}")

    except mysql.connector.Error as err:
        print(f"Ошибка добавления фотографии в базу данных: {err}")



# БАЛАНС
@router.callback_query(F.data == "balance")
async def balance(clbck: CallbackQuery, state: FSMContext):
    with db.connection.cursor() as cursor:
        qy = "SELECT * FROM users_settings WHERE id = %s"
        cursor.execute(qy, clbck.from_user.id)
        result = cursor.fetchone()
        if result['stat'] == 'defult_user':
            media = InputMediaPhoto(media=img.DEFULT_B, caption=f"{clbck.from_user.full_name}, твой баланс:\n\nТокены: {result['tokens']}⭐️\n\nУ вас нет DRESSPREM")
            await clbck.message.edit_media(media=media)
            await clbck.message.edit_reply_markup(reply_markup=kb.balance_kb)
        if result['stat'] == 'silver_user':
            media = InputMediaPhoto(media=img.SILVER, caption=f"{clbck.from_user.full_name}, твой баланс:\n\nБесплатные обработки: {result['prem_tok_day']}\n\nТокены: {result['tokens']}⭐️\n\nDRESSPREM: SILVER\nДо окончания подписки: {time_sub_day(clbck.from_user.id)}")
            await clbck.message.edit_media(media=media)
            await clbck.message.edit_reply_markup(reply_markup=kb.balance_kb)
        if result['stat'] == 'gold_user':
            media = InputMediaPhoto(media=img.GOLD, caption=f"{clbck.from_user.full_name}, твой баланс:\n\nБесплатные обработки: {result['prem_tok_day']}\n\nТокены: {result['tokens']}⭐️\n\nDRESSPREM: GOLD\nДо окончания подписки: {time_sub_day(clbck.from_user.id)}")
            await clbck.message.edit_media(media=media)
            await clbck.message.edit_reply_markup(reply_markup=kb.balance_kb)



# ГЛАВНЫЙ РАЗДЕЛ МАГАЗИНА С ПОДПИСКАМИ
@router.callback_query(F.data == "shop_prem")
async def shop(clbck: CallbackQuery, state: FSMContext):
    global msg_shop
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT stat FROM users_settings WHERE id = %s", (clbck.from_user.id))
        result = cursor.fetchone()
    if result['stat'] == 'defult_user':
        media = InputMediaPhoto(media=img.DEFULT, caption=text.shop_defult.format(name=clbck.from_user.full_name))
        msg_shop = await clbck.message.edit_media(media=media)
        await clbck.message.edit_reply_markup(reply_markup=kb.shop_kb_defult)
    if result['stat'] == 'silver_user':
        media = InputMediaPhoto(media=img.SILVER, caption=text.shop_silver.format(name=clbck.from_user.full_name))
        msg_shop = await clbck.message.edit_media(media=media)
        await clbck.message.edit_reply_markup(reply_markup=kb.shop_kb_silver)
    if result['stat'] == 'gold_user':
        media = InputMediaPhoto(media=img.GOLD, caption=text.shop_gold.format(name=clbck.from_user.full_name))
        msg_shop = await clbck.message.edit_media(media=media)
        await clbck.message.edit_reply_markup(reply_markup=kb.shop_kb_gold)

# РАЗДЕЛ С ПОКУПКОЙ ТОКЕНОВ
@router.callback_query(F.data == "buy_tokens")
async def process_buy_command4(clbck: CallbackQuery, state: FSMContext):
    global msg_shop
    if config.PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
        media = InputMediaPhoto(media=img.BUY_TK, caption=text.buy_TOKENS)
        msg_shop = await clbck.message.edit_media(media=media)
        await clbck.message.edit_reply_markup(reply_markup=kb.tokens_kb)



# ПОКУПКА ПОДПИСКИ SILVER
@router.callback_query(F.data == "buy_prem_silver")
async def process_buy_command1(clbck: CallbackQuery, state: FSMContext):
    if config.PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await Bot_h.send_invoice(
            clbck.message.chat.id,
            title=text.premS_t,
            description=text.premS,
            provider_token=config.PAYMENTS_PROVIDER_TOKEN,
            currency='rub',
            is_flexible=False,
            prices=[prices.PRICE_SILVER_PREM_1],
            start_parameter='time-machine-example',
            payload='some-invoice-payload-for-our-internal-use'
        )

# ПОКУПКА ПОДПИСКИ GOLD
@router.callback_query(F.data == "buy_prem_gold")
async def process_buy_command2(clbck: CallbackQuery, state: FSMContext):
    if config.PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await Bot_h.send_invoice(
            clbck.message.chat.id,
            title=text.premG_t,
            description=text.premG,
            provider_token=config.PAYMENTS_PROVIDER_TOKEN,
            currency='rub',
            is_flexible=False,
            prices=[prices.PRICE_GOLD_PREM_1],
            start_parameter='time-machine-example',
            payload='some-invoice-payload-for-our-internal-use'
        )

# ОБНОВЛЕНИЕ ПОДПИСКИ ДО GOLD
@router.callback_query(F.data == "update_to_gold")
async def process_buy_command3(clbck: CallbackQuery, state: FSMContext):
    if config.PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await Bot_h.send_invoice(
            clbck.message.chat.id,
            title=text.premU_t,
            description=text.premU,
            provider_token=config.PAYMENTS_PROVIDER_TOKEN,
            currency='rub',
            is_flexible=False,
            prices=[prices.PRICE_UPDATE_TO_GOLD],
            start_parameter='time-machine-example',
            payload='some-invoice-payload-for-our-internal-use'
        )


# ПОКУПКА ТОКЕНОВ
@router.callback_query(F.data == "buy_tokens_100")
async def process_buy_command5(clbck: CallbackQuery, state: FSMContext):
    await Bot_h.send_invoice(
        clbck.message.chat.id,
        title=text.BuyT_t.format(tokens='100'),
        description=text.BuyT.format(tokens='100', col='1 - 2'),
        provider_token=config.PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        photo_url='',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[prices.TOKEN_100],
        start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use'
    )

@router.callback_query(F.data == "buy_tokens_300")
async def process_buy_command6(clbck: CallbackQuery, state: FSMContext):
    await Bot_h.send_invoice(
        clbck.message.chat.id,
        title=text.BuyT_t.format(tokens='300'),
        description=text.BuyT.format(tokens='300', col='3 - 6'),
        provider_token=config.PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        photo_url='',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[prices.TOKEN_300],
        start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use'
    )

@router.callback_query(F.data == "buy_tokens_500")
async def process_buy_command7(clbck: CallbackQuery, state: FSMContext):
    await Bot_h.send_invoice(
        clbck.message.chat.id,
        title=text.BuyT_t.format(tokens='500'),
        description=text.BuyT.format(tokens='500', col='5 - 10'),
        provider_token=config.PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        photo_url='',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[prices.TOKEN_500],
        start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use'
    )

@router.callback_query(F.data == "buy_tokens_750")
async def process_buy_command8(clbck: CallbackQuery, state: FSMContext):
    await Bot_h.send_invoice(
        clbck.message.chat.id,
        title=text.BuyT_t.format(tokens='750'),
        description=text.BuyT.format(tokens='750', col='7 - 15'),
        provider_token=config.PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        photo_url='',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[prices.TOKEN_750],
        start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use'
    )

@router.callback_query(F.data == "buy_tokens_1000")
async def process_buy_command9(clbck: CallbackQuery, state: FSMContext):
    await Bot_h.send_invoice(
        clbck.message.chat.id,
        title=text.BuyT_t.format(tokens='1000'),
        description=text.BuyT.format(tokens='1000', col='10 - 20'),
        provider_token=config.PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        photo_url='',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[prices.TOKEN_1000],
        start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use'
    )

@router.callback_query(F.data == "buy_tokens_1500")
async def process_buy_command10(clbck: CallbackQuery, state: FSMContext):
    await Bot_h.send_invoice(
        clbck.message.chat.id,
        title=text.BuyT_t.format(tokens='1500'),
        description=text.BuyT.format(tokens='1500', col='15 - 30'),
        provider_token=config.PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        photo_url='',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[prices.TOKEN_1500],
        start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use'
    )

@router.callback_query(F.data == "buy_tokens_2000")
async def process_buy_command11(clbck: CallbackQuery, state: FSMContext):
    await Bot_h.send_invoice(
        clbck.message.chat.id,
        title=text.BuyT_t.format(tokens='2000'),
        description=text.BuyT.format(tokens='2000', col='20 - 40'),
        provider_token=config.PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        photo_url='',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[prices.TOKEN_2000],
        start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use'
    )

@router.callback_query(F.data == "buy_tokens_3000")
async def process_buy_command12(clbck: CallbackQuery, state: FSMContext):
    await Bot_h.send_invoice(
        clbck.message.chat.id,
        title=text.BuyT_t.format(tokens='3000'),
        description=text.BuyT.format(tokens='3000', col='30 - 60'),
        provider_token=config.PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        photo_url='',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        prices=[prices.TOKEN_3000],
        start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use'
    )


# ОБРАБОТКА ЗАПРОСА НА ПОКУПКУ
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    global msg_shop
    await Bot_h.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    await msg_shop.delete()


# ФУНКЦИЯ ОБНОВЛЕНИЯ СТАТУСА ПОЛЬЗОВАТЕЛЯ
async def update_user_status(user_id: int, status: str):
    with db.connection.cursor() as cursor:
        cursor.execute("UPDATE users_settings SET stat = %s WHERE id = %s", (status, user_id))
        db.connection.commit()

# ФУНКЦИЯ ЗАПРОСА СТАТУСА ПОЛЬЗОВАТЕЛЯ
async def select_user_status(user_id: int):
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT stat FROM users_settings WHERE id = %s", user_id)
    return cursor.fetchone()['stat']

# ФУНКЦИЯ ПЕРЕВОДА ДНЕЙ В СЕКУНДЫ
def days_to_second(days):
    return days * 24 * 60 * 60

# ФУНКЦИЯ ДЛЯ ОБНОВЛЕНИЯ ТОКЕНОВ ПОЛЬЗВАТЕЛЯ
async def update_user_tokens(flag_timer):
    while flag_timer:
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        midnight = datetime.datetime.combine(tomorrow, datetime.time())
        res = (midnight - now).total_seconds()
        await asyncio.sleep(res)

        try:
            with db.connection.cursor() as conn:
                conn.execute('UPDATE users_settings SET prem_tok_day = 3 WHERE stat = "silver_user"')
                conn.execute('UPDATE users_settings SET prem_tok_day = 5 WHERE stat = "gold_user"')
                db.connection.commit()
        except Exception as e:
            print(f"Ошибка при обновлении токенов: {e}")


# УСТАНОВКА ТАЙМЕРА (АДМИН)
@router.message(Command("settimer"))
async def cmd_settime(message: types.Message):
    if admin.admins_db_id(message.from_user.id) == True:
        asyncio.create_task(update_user_tokens(flag_timer = True)) # Запускаем задачу в фоне
        await message.answer("Таймер установлен. Токены будут обновляться ежедневно в 00:00.")
    else:
        await message.answer("Вы не можете изменять настройки бота т.к. не являетесь админом")

# ОСТАНОВКА ТАЙМЕРА (АДМИН)
@router.message(Command("deltimer"))
async def cmd_deltime(message: types.Message):
    if admin.admins_db_id(message.from_user.id) == True:
        asyncio.create_task(update_user_tokens(flag_timer = False)) # Запускаем задачу в фоне
        await message.answer("Таймер отключен. Токены не будут обновляться")
    else:
        await message.answer("Вы не можете изменять настройки бота т.к. не являетесь админом")

# УСТАНОВКА ТАЙМЕРА 2
async def set_times(user_id, time_sub):
    with db.connection.cursor() as cursor:
        cursor.execute("UPDATE users_settings SET time_set = %s WHERE id = %s", (time_sub, user_id))
        db.connection.commit()

# РАССЧЁТ КОЛ-ВО ВРЕМЕНИ ДО ОКОНЧАНИЯ ПОДПИСКИ
def time_sub_day(user_id):
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT time_set FROM users_settings WHERE id = %s", user_id)
        get_time = int(cursor.fetchone()['time_set'])
    middle_times = get_time - int(time.time())
    if middle_times <= 0:
        return False
    else:
        dt = str(datetime.timedelta(seconds=middle_times))
        dt = dt.replace('days', "дней")
        dt = dt.replace('day', "день")
        return dt

# ПОЛУЧЕНИЕ БЕСПЛАТНЫХ ОБРАБОТОК
async def get_token(user_id, tokens):
    with db.connection.cursor() as cursor:
        cursor.execute("UPDATE users_settings SET tokens = %s + tokens WHERE id = %s", (tokens, user_id))
        db.connection.commit()

# УСПЕШНАЯ ОПЛАТА
@router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    user_id = message.from_user.id
    total_amount = message.successful_payment.total_amount // 100
    currency = message.successful_payment.currency

    if total_amount == 20:
        title = 100
        await message.answer_photo(photo=img.BUY_TK100, caption=text.buy_th.format(col=title), reply_markup=kb.iexit_kb)
        await get_token(user_id, int(title))

    elif total_amount == 55:
        title = 300
        await message.answer_photo(photo=img.BUY_TK300, caption=text.buy_th.format(col=title), reply_markup=kb.iexit_kb)
        await get_token(user_id, int(title))

    elif total_amount == 90:
        title = 500
        await message.answer_photo(photo=img.BUY_TK500, caption=text.buy_th.format(col=title), reply_markup=kb.iexit_kb)
        await get_token(user_id, int(title))

    elif total_amount == 140:
        title = 750
        await message.answer_photo(photo=img.BUY_TK750, caption=text.buy_th.format(col=title), reply_markup=kb.iexit_kb)
        await get_token(user_id, int(title))


    elif total_amount == 180:
        title = 1000
        await message.answer_photo(photo=img.BUY_TK1000, caption=text.buy_th.format(col=title), reply_markup=kb.iexit_kb)
        await get_token(user_id, int(title))


    elif total_amount == 270:
        title = 1500
        await message.answer_photo(photo=img.BUY_TK1500, caption=text.buy_th.format(col=title), reply_markup=kb.iexit_kb)
        await get_token(user_id, int(title))


    elif total_amount == 350:
        title = 2000
        await message.answer_photo(photo=img.BUY_TK2000, caption=text.buy_th.format(col=title), reply_markup=kb.iexit_kb)
        await get_token(user_id, int(title))


    elif total_amount == 530:
        title = 3000
        await message.answer_photo(photo=img.BUY_TK3000, caption=text.buy_th.format(col=title), reply_markup=kb.iexit_kb)
        await get_token(user_id, int(title))


    elif total_amount == 550:
        time_sub = int(time.time()) + days_to_second(30)
        await message.answer_photo(photo=img.SILVER, caption=text.prem_SILVER, reply_markup=kb.iexit_kb)
        await update_user_status(user_id, "silver_user")
        await get_token(user_id, 500)
        await set_times(user_id, time_sub)
        with db.connection.cursor() as cursor:
            cursor.execute('UPDATE users_settings SET prem_tok_day = 3 WHERE id = %s', user_id)
            db.connection.commit()

    elif total_amount == 200:
        await message.answer_photo(photo=img.GOLD, caption=text.prem_UPDATE, reply_markup=kb.iexit_kb)
        await update_user_status(user_id, "gold_user")
        await get_token(user_id, 500)
        with db.connection.cursor() as cursor:
            cursor.execute('UPDATE users_settings SET prem_tok_day = 5 WHERE id = %s', user_id)
            db.connection.commit()

    elif total_amount == 750:
        time_sub = int(time.time()) + days_to_second(30)
        await message.answer_photo(photo=img.GOLD, caption=text.prem_GOLD, reply_markup=kb.iexit_kb)
        await update_user_status(user_id, "gold_user")
        await get_token(user_id, 1000)
        await set_times(user_id, time_sub)
        with db.connection.cursor() as cursor:
            cursor.execute('UPDATE users_settings SET prem_tok_day = 5 WHERE id = %s', user_id)
            db.connection.commit()
