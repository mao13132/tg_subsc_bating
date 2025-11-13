# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
async def get_last_id(managers):
    managers = sorted(managers, key=lambda x: x['id'])

    try:
        last_id = managers[-1]['id']
    except:
        return 0

    return last_id + 1
