# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from datetime import datetime
from src.start_sql_data.texts_init import init_texts_from_json


async def start_sql_data(BotDB):
    res_ = await BotDB.start_settings(key='managers', value='[]')

    await init_texts_from_json(BotDB)

    # await __import__('src.sql.test_users_seed', fromlist=['seed_test_users']).seed_test_users(BotDB)

    return True
