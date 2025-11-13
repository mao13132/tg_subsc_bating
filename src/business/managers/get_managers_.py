# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from src.telegram.bot_core import BotDB

import json


async def get_managers():
    managers = await BotDB.get_setting('managers')

    if managers:
        try:
            managers = json.loads(managers)
        except:
            managers = []

    else:
        managers = []

    return managers
