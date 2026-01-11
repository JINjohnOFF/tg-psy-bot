import asyncio, os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from storage import save_message, get_user, update_passport
from gemini import build_or_merge_passport, format_passport, compatibility

bot = Bot(os.getenv("TG_TOKEN"))
dp = Dispatcher()


@dp.message(F.text & ~F.command)
async def collect(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return

    save_message(message.chat.id, message.from_user.id, message.text)
    user = get_user(message.chat.id, message.from_user.id)

    if len(user["messages"]) == 500:
        result = build_or_merge_passport(
            user["passport"]["text"],
            user["messages"]
        )
        update_passport(message.chat.id, message.from_user.id, result)


@dp.message(Command("passport"))
async def passport_cmd(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("/passport @user short|deep")
        return

    mode = args[2] if len(args) > 2 else "deep"
    reply = message.reply_to_message
    if not reply:
        await message.reply("Ответь на сообщение пользователя")
        return

    user = get_user(message.chat.id, reply.from_user.id)
    if not user or not user["passport"]["text"]:
        await message.reply("Недостаточно данных")
        return

    text = format_passport(user["passport"]["text"], mode)

    msg = (
        f"🧠 Паспорт v{user['passport']['version']}\n"
        f"📊 Confidence: {user['passport']['confidence']:.2f}\n"
    )

    if user["shift"]["detected"]:
        msg += f"⚠️ Сдвиг: {user['shift']['reason']}\n"

    await message.reply(msg + "\n" + text[:4000])


@dp.message(Command("compatibility"))
async def compat_cmd(message: Message):
    if not message.reply_to_message:
        await message.reply("Ответь на сообщение первого человека")
        return

    u1 = get_user(message.chat.id, message.reply_to_message.from_user.id)
    u2 = get_user(message.chat.id, message.from_user.id)

    if not u1 or not u2:
        await message.reply("Недостаточно данных")
        return

    result = compatibility(
        u1["passport"]["text"],
        u2["passport"]["text"]
    )
    await message.reply(result[:4000])


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
