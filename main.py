import asyncio
from pprint import pprint

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, ChatMemberAdministrator, ChatMemberOwner
import os
import django
from decouple import config


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from asgiref.sync import sync_to_async
from app.models import BotUser, OrderTaxi, GroupChatId, Driver

API_TOKEN = config('BOT_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@sync_to_async
def create_bot_user(chat_id, full_name, phone_number):
    return BotUser.objects.create(
        chat_id=chat_id,
        full_name=full_name,
        phone_number=phone_number
    )

@sync_to_async
def check_user(chat_id):
    return BotUser.objects.filter(chat_id=chat_id).exists()

@sync_to_async
def get_user(chat_id):
    try:
        return BotUser.objects.get(chat_id=chat_id)
    except Exception:
        return None

@sync_to_async
def get_user_from_order(order):
    try:
        return order.user
    except Exception:
        return None

@sync_to_async
def get_driver(chat_id):
    try:
        return Driver.objects.get(chat_id=chat_id)
    except Exception:
        return None

@sync_to_async
def get_group(chat_id):
    return GroupChatId.objects.all().exists()

@sync_to_async
def create_bot_group(chat_id, title):
    return GroupChatId.objects.create(
        chat_id=chat_id,
        group_name=title
    )

@sync_to_async
def get_groups():
    return GroupChatId.objects.all()

@sync_to_async
def create_order(direction, user):
    OrderTaxi.objects.create(user=user, direction=direction)

@sync_to_async
def update_order(option, user):
    order = OrderTaxi.objects.filter(user=user).order_by('-created_at').first()

    if order:
        order.person_count = option
        order.save()
    return order

@sync_to_async
def get_order(user):
    order = OrderTaxi.objects.filter(user=user).order_by('-created_at').first()
    return order

@sync_to_async
def get_order_user_id(order):
    return order.user.chat_id

@sync_to_async
def get_order_from_id(order_id):
    order = OrderTaxi.objects.filter(id=order_id).order_by('-created_at').first()
    return order

@sync_to_async
def update_order_time(user, time):
    order = OrderTaxi.objects.filter(user=user).order_by('-created_at').first()

    if order:
        order.leave_time = time
        order.save()
    return order

@sync_to_async
def update_order_description(user, description):
    order = OrderTaxi.objects.filter(user=user).order_by('-created_at').first()

    if order:
        order.description = description
        order.save()
    return order

@sync_to_async
def update_order_location(user, link):
    order = OrderTaxi.objects.filter(user=user).order_by('-created_at').first()

    if not order.from_location:
        order.from_location = link
        order.save()
    else:
        return None
    return order

@sync_to_async
def update_order_driver(order, driver):
    if not order.driver:
        order.driver = driver
        order.driver_status = True
        order.save()
    else:
        return order
    return order

phone_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


async def send_welcome(message: Message):
    button_order = KeyboardButton(text="🛍️ Buyurtma berish 🛒")

    menu = ReplyKeyboardMarkup(keyboard=[[button_order]], resize_keyboard=True)

    await message.answer("*Kerakli bo'limni tanlang:*", reply_markup=menu, parse_mode="Markdown")

@dp.message(Command("start"))
async def start_command(message: Message):
    chat_id = message.chat.id
    if message.chat.type == "private":
        if await check_user(chat_id):
            await send_welcome(message)
        else:
            await message.answer(
                "<b>Assalomu alaykum!</b>\n\n"
                "📱 <i>Iltimos, raqamingizni yuboring:</i>",
                reply_markup=phone_button,
                parse_mode="HTML"
            )


@dp.message(Command("activate"))
async def activate_group(message: Message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        chat_title = message.chat.title
        group = await get_group(chat_id)

        bot_member = await message.bot.get_chat_member(chat_id, message.bot.id)
        if not isinstance(bot_member, (ChatMemberAdministrator, ChatMemberOwner)):
            await message.answer(
                "⚠️ <b>Diqqat!</b>\n\n"
                "Bot ushbu guruhda <b>administrator</b> emas. "
                "🔑 <i>Guruhni aktivatsiya qilish uchun botni administrator qiling.</i>",
                parse_mode="HTML"
            )

            return

        if not group:
            await create_bot_group(chat_id, chat_title)
            await message.answer(
                f"✅ <b>Guruh muvaffaqiyatli activate qilindi!</b>\n\n"
                f"📌 <b>Guruh nomi:</b> <i>{chat_title}</i>\n"
                f"🆔 <b>Guruh ID:</b> <code>{chat_id}</code>",
                parse_mode="HTML"
            )

        else:
            await message.answer(
                f"⚠️ <b>Botga guruh allaqachon biriktirilgan!</b>\n\n"
                f"📌 <b>Guruh nomi:</b> <i>{chat_title}</i>\n"
                f"🆔 <b>Guruh ID:</b> <code>{chat_id}</code>",
                parse_mode="HTML"
            )


@dp.message(F.contact)
async def handle_contact(message: Message):
    if not await check_user(message.chat.id):
        if message.contact and message.contact.phone_number:
            phone_number = message.contact.phone_number
            name = f'{message.chat.first_name if message.chat.first_name else ""} {message.chat.last_name if message.chat.last_name else ""}'
            await create_bot_user(message.chat.id, name, phone_number)
            await message.answer(
                f"👤 *Ism familiyangiz:* `{name}`\n"
                f"📞 *Raqamingiz saqlandi:* `{phone_number}`",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="Markdown"
            )

            await send_welcome(message)
        else:
            await message.answer(
                "📱 <b>Iltimos, telefon raqamingizni yuboring:</b>",
                reply_markup=phone_button,
                parse_mode="HTML"
            )

    else:
        await send_welcome(message)

@dp.message(F.text == "🛍️ Buyurtma berish 🛒")
async def handle_order(message: Message):
    await message.answer(
        "🛒 <b>Buyurtma berish jarayonini boshlaymiz!</b>",
        parse_mode="HTML"
    )

    button1 = InlineKeyboardButton(
        text="🚕 Farg'ona → Yaypan",
        callback_data="fargona_yaypan"
    )
    button2 = InlineKeyboardButton(
        text="🚕 Yaypan → Farg'ona",
        callback_data="yaypan_fargona"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])
    await message.answer(
        "<b>Buyurtma ma'lumotlari:</b>\n\n"
        "📍 <b>Yo'nalishingiz:</b> <i>------------</i>\n"
        "👥 <b>Necha kishi:</b> <i>-------------</i>\n"
        "🕒 <b>Vaqti:</b> <i>-------------</i>\n"
        "📍 <b>Ketish joyi:</b> <i>-------------------</i>\n"
        "📝 <b>Izoh:</b> <i>-----------------</i>",
        parse_mode="HTML"
    )

    await message.answer(
        "🚖 <b>Yo'nalishni tanlang:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@dp.callback_query()
async def handle_button_click(callback_query: CallbackQuery):
    selected_option = callback_query.data
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    options = {"fargona_yaypan": "Farg'ona-Yaypan", "yaypan_fargona": "Yaypan-Farg'ona"}
    user = await get_user(chat_id)

    if selected_option in ['yaypan_fargona', 'fargona_yaypan']:
        await create_order(selected_option, user)

        await callback_query.message.answer(
            f"<b>Buyurtma ma'lumotlari:</b>\n\n"
            f"📍 <b>Yo'nalishingiz:</b> <i>{options[selected_option]}</i>\n"
            f"👥 <b>Necha kishi:</b> <i>-------------</i>\n"
            f"🕒 <b>Vaqti:</b> <i>-------------</i>\n"
            f"📍 <b>Ketish joyi:</b> <i>-------------------</i>\n"
            f"📝 <b>Izoh:</b> <i>-----------------</i>",
            parse_mode="HTML"
        )

        button1 = InlineKeyboardButton(text="1", callback_data="1")
        button2 = InlineKeyboardButton(text="2", callback_data="2")
        button3 = InlineKeyboardButton(text="3", callback_data="3")
        button4 = InlineKeyboardButton(text="4", callback_data="4")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2], [button3, button4]])

        await callback_query.message.answer(
            "👥 <b>Nechta joy kerak:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    elif selected_option in ['1', '2', '3', '4']:
        order = await update_order(selected_option, user)

        await callback_query.message.answer(
            f"<b>Buyurtma ma'lumotlari:</b>\n\n"
            f"📍 <b>Yo'nalishingiz:</b> <i>{options[order.direction]}</i>\n"
            f"👥 <b>Necha kishi:</b> <i>{order.person_count}</i>\n"
            f"🕒 <b>Vaqti:</b> <i>-------------</i>\n"
            f"📍 <b>Ketish joyi:</b> <i>-------------------</i>\n"
            f"📝 <b>Izoh:</b> <i>-----------------</i>",
            parse_mode="HTML"
        )

        await callback_query.message.answer(
            "🗓️ *Sana va Vaqtni kiriting:*\n```Na'muna: /vaqt 21-Noyabr, 12:30```",
            parse_mode="Markdown"
        )


    elif selected_option in ['ha', 'yoq']:
        if selected_option == 'yoq':
            await callback_query.message.answer(
                "❌ <b>Buyurtmangiz rad etildi.</b>\n"
                "🔄 <i>Bot qayta ishga tushiriladi...</i>",
                parse_mode="HTML"
            )

            await send_welcome(callback_query.message)
        elif selected_option=='ha':
            groups = await get_groups()
            order = await get_order(user)
            user = await get_user_from_order(order)
            text = f"{order.id}-<b>raqamli buyurtma:</b>\n\n" + \
                f"👤 <b>F.I.O:</b> {user.full_name}\n" + \
                f"📱 <b>Telefon raqami:</b> {user.phone_number}\n" + \
                f"📍 <b>Yo'nalish:</b> <i>{options[order.direction]}</i>\n" + \
                f"👥 <b>Yo'lovchilar soni:</b> <i>{order.person_count}</i>\n" + \
                f"🕒 <b>Vaqti:</b> <i>{order.leave_time}</i>\n" + \
                f"📍 <b>Ketish joyi:</b> <i><a href='{order.from_location}'>Google Maps'da ko'rish</a></i>\n" + \
                f"📝 <b>Izoh:</b> <i>{order.description}</i>"

            await callback_query.message.answer(text, parse_mode="HTML")
            await bot.delete_message(chat_id, message_id)
            async for gr in groups:
                await send_message_to_group(gr.chat_id, text)
            await callback_query.message.answer(
                "✅ <b>Buyurtmangiz qabul qilindi.</b>\n"
                "⏳ <i>Tez orada sizga xabar beramiz...</i>",
                parse_mode="HTML"
            )


    elif selected_option == "accept":
        chat_id = callback_query.message.chat.id
        user_chat_id = callback_query.from_user.id
        user = await get_driver(user_chat_id)


        if user is not None:
            original_text = callback_query.message.text
            original_markup = callback_query.message.reply_markup

            order_id = callback_query.message.text.split("-")[0]
            order = await get_order_from_id(order_id)
            driver = await get_driver(user_chat_id)
            order = await update_order_driver(order, driver)
            groups = await get_groups()
            text = ""

            new_markup = None

            if original_text != text or original_markup != new_markup:
                new_text = f"{order.id}-<b>buyurtmangiz qabul qilindi</b>\n\n" + \
                           f"<b>🚗 Haydovchi ma'lumotlari:</b>\n" + \
                           f"<b>👤 F.I.O:</b> {order.driver.full_name}\n" + \
                           f"<b>📞 Telefon raqami:</b> {order.driver.phone_number}\n" + \
                           f"<b>🚙 Mashina:</b> {order.driver.car_info}"

                text_for_group = f"{order.id}-<b>raqamli buyurtma qabul qilindi ✅ </b>\n\n" + \
                            f"<b>Haydovchi:</b> {order.driver.full_name}\n"

                user_chat_id = await get_order_user_id(order)
                if user_chat_id:
                    await bot.send_message(user_chat_id, new_text, parse_mode="HTML")
                else:
                    print("Foydalanuvchining chat_id topilmadi.")
                await bot.delete_message(
                    chat_id=chat_id,
                    message_id=callback_query.message.message_id
                )

                await callback_query.answer(
                    "✅ <b>Buyurtma qabul qilindi!</b>",
                    parse_mode="HTML"
                )
                async for gr in groups:
                    await bot.send_message(gr.chat_id, text_for_group, parse_mode="HTML")

        else:
            await callback_query.answer(
                "⚠️ <b>Sizning hisobingizda noaniqlik mavjud.</b>\n"
                "📞 <i>Iltimos, administrator bilan bog'laning.</i>",
                parse_mode="HTML"
            )


async def send_message_to_group(chat_id: int, message_text: str):
    try:
        button1 = InlineKeyboardButton(text="✅ Qabul qilish", callback_data="accept")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1]])

        await bot.send_message(chat_id, message_text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        print(f"Xatolik: {e}")


@dp.message(F.content_type == ContentType.LOCATION)
async def handle_location(message: Message):
    chat_id = message.chat.id
    options = {"fargona_yaypan": "Farg'ona-Yaypan", "yaypan_fargona": "Yaypan-Farg'ona"}
    user = await get_user(chat_id)
    latitude = message.location.latitude
    longitude = message.location.longitude

    maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

    if user is not None:
        order = await update_order_location(user, maps_link)
        if order is not None:
            await message.answer(
                f"<b>Buyurtma ma'lumotlari:</b>\n\n"
                f"📍 <b>Yo'nalishingiz:</b> {options[order.direction]}\n"
                f"👥 <b>Necha kishi:</b> {order.person_count}\n"
                f"🕒 <b>Vaqti:</b> {order.leave_time}\n"
                f"📍 <b>Ketish joyi:</b> <a href='{order.from_location}'>Google Maps'da ko'rish</a>\n"
                f"📝 <b>Izoh:</b> {order.description}",
                parse_mode='HTML'
            )

        await message.answer(
            "Haydovchi uchun qo'shimcha izoh yozing:\n\n"
            "```Na'muna: /izoh Yuklarim bor, Hozirgi telefon raqamim: +998-YY-XXX-XX-XX```",
            parse_mode='Markdown'
        )


@dp.message()
async def handle_message(message: Message):
    text = message.text
    chat_id = message.chat.id
    options = {"fargona_yaypan": "Farg'ona-Yaypan", "yaypan_fargona": "Yaypan-Farg'ona"}
    user = await get_user(chat_id)
    if text is not None and "/vaqt " in text and user is not None:
        order = await update_order_time(user, text[5:])

        await message.answer(
            f"<b>Buyurtma ma'lumotlari:</b>\n\n"
            f"📍 <b>Yo'nalishingiz:</b> {options[order.direction]}\n"
            f"👥 <b>Necha kishi:</b> {order.person_count}\n"
            f"🕒 <b>Vaqti:</b> {order.leave_time}\n"
            f"📍 <b>Ketish joyi:</b> -------------------\n"
            f"📝 <b>Izoh:</b> -----------------",
            parse_mode='HTML'
        )

        await message.answer(
            "📍 <b>Ketish joyini lokatsiyasini yuboring:</b>",
            parse_mode='HTML'
        )

    elif text is not None and "/izoh " in text and user is not None:
        order = await update_order_description(user, text[5:])

        await message.answer(
            f"<b>Buyurtma ma'lumotlari:</b>\n\n"
            f"📍 <b>Yo'nalishingiz:</b> {options[order.direction]}\n"
            f"👥 <b>Necha kishi:</b> {order.person_count}\n"
            f"🕒 <b>Vaqti:</b> {order.leave_time}\n"
            f"📍 <b>Ketish joyi:</b> <a href='{order.from_location}'>Google Maps'da ko'rish</a>\n"
            f"📝 <b>Izoh:</b> {order.description}",
            parse_mode='HTML'
        )

        button1 = InlineKeyboardButton(text="✅ Ha", callback_data="ha")
        button2 = InlineKeyboardButton(text="❌ Yo'q", callback_data="yoq")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])

        await message.answer(
            "✅ <b>Ma'lumotlarni tasdiqlaysizmi?</b>",
            reply_markup=keyboard,
            parse_mode='HTML'
        )


async def main():
    print("Bot ishga tushdi...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())