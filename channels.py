from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from config import REQUIRED_CHANNELS


async def check_subscription(bot: Bot, user_id: int) -> tuple[bool, list[dict]]:
    """
    Проверяет подписку пользователя на все каналы.
    Возвращает (все_подписан, список_непройденных_каналов)
    """
    not_subscribed = []

    for channel in REQUIRED_CHANNELS:
        subscribed = await is_subscribed(bot, user_id, channel)
        if not subscribed:
            not_subscribed.append(channel)

    return len(not_subscribed) == 0, not_subscribed


async def is_subscribed(bot: Bot, user_id: int, channel: dict) -> bool:
    """
    Проверяет подписку на конкретный канал.
    Для каналов типа 'request' — считаем подписанным если статус member/administrator/creator.
    """
    try:
        member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
        status = member.status.value  # 'member', 'administrator', 'creator', 'left', 'kicked', 'restricted'
        return status in ("member", "administrator", "creator")
    except (TelegramForbiddenError, TelegramBadRequest):
        # Бот не является участником канала или нет прав — пропускаем проверку
        return True


def build_subscribe_keyboard(not_subscribed: list[dict]):
    """Строит inline-клавиатуру со ссылками на каналы и кнопкой проверки."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    buttons = []
    for ch in not_subscribed:
        if ch["type"] == "public" and ch.get("username"):
            url = f"https://t.me/{ch['username']}"
        elif ch.get("invite_link"):
            url = ch["invite_link"]
        else:
            # Если нет ни username ни invite_link — пропускаем кнопку
            continue

        label = {
            "public": "📢",
            "private": "🔒",
            "request": "📋",
        }.get(ch["type"], "📌")

        buttons.append([InlineKeyboardButton(text=f"{label} {ch['title']}", url=url)])

    buttons.append([InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
