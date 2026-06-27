import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN
from channels import check_subscription, build_subscribe_keyboard

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def require_subscription(user_id: int, respond_func):
    """
    Универсальная проверка подписки.
    respond_func — async callable для отправки ответа пользователю.
    Возвращает True если все подписки пройдены.
    """
    all_ok, not_subscribed = await check_subscription(bot, user_id)

    if not all_ok:
        text = (
            "👋 Чтобы пользоваться ботом, подпишись на все каналы ниже.\n\n"
            "После подписки нажми кнопку <b>✅ Я подписался</b>."
        )
        keyboard = build_subscribe_keyboard(not_subscribed)
        await respond_func(text, reply_markup=keyboard, parse_mode="HTML")
        return False

    return True


@dp.message(CommandStart())
async def cmd_start(message: Message):
    ok = await require_subscription(
        message.from_user.id,
        lambda text, **kwargs: message.answer(text, **kwargs),
    )
    if ok:
        await message.answer(
            "✅ Отлично! Все подписки подтверждены.\n\nДобро пожаловать! Бот готов к работе."
        )


@dp.callback_query(F.data == "check_subscription")
async def callback_check(call: CallbackQuery):
    all_ok, not_subscribed = await check_subscription(bot, call.from_user.id)

    if not all_ok:
        text = (
            "❌ Ты ещё не подписан на все каналы.\n\n"
            "Подпишись и снова нажми кнопку."
        )
        keyboard = build_subscribe_keyboard(not_subscribed)
        await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await call.answer("Подпишись на все каналы!", show_alert=True)
    else:
        await call.message.edit_text(
            "✅ Отлично! Все подписки подтверждены.\n\nДобро пожаловать! Бот готов к работе."
        )
        await call.answer("Доступ открыт!", show_alert=False)


# --- Пример защиты любого другого хендлера ---
@dp.message()
async def any_message(message: Message):
    ok = await require_subscription(
        message.from_user.id,
        lambda text, **kwargs: message.answer(text, **kwargs),
    )
    if not ok:
        return

    # Сюда попадает только подписанный пользователь
    await message.answer("Ты написал: " + message.text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
