import asyncio

from src.business.start_sql_data.start_sql_data import start_sql_data
from src.telegram.bot_core import *
from src.telegram.handlers.users import *
from src.telegram.state.states import *
from src.telegram.callbacks.call_user import *
from src.business.schedule.payment_scheduler import start_payment_scheduler, stop_payment_scheduler


def registration_all_handlers(dp):
    register_user(dp)


def registration_state(dp):
    register_state(dp)


def registration_calls(dp):
    register_callbacks(dp)


async def main():
    bot_start = Core()

    res_sql = await bot_start.BotDB.init_bases()

    if not res_sql:
        return False

    start_data = await start_sql_data(bot_start.BotDB)

    registration_all_handlers(bot_start.dp)
    registration_state(bot_start.dp)
    registration_calls(bot_start.dp)

    await start_payment_scheduler()

    try:
        await bot_start.dp.start_polling()
    finally:
        await stop_payment_scheduler()
        await bot_start.dp.storage.close()
        await bot_start.dp.storage.wait_closed()
        await bot_start.bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print(f'Бот остановлен!')
