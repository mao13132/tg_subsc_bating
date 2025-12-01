from datetime import datetime
from sqlalchemy import select, insert, func

from src.sql.bd import Users


async def seed_test_users(BotDB, total: int = 200):
    try:
        async with BotDB.async_session_maker() as session:
            res = await session.execute(select(func.count(Users.id_pk)))
            existing = int(res.scalar() or 0)
            if existing >= total:
                return True

            need = total - existing
            now = datetime.utcnow()

            data = []
            for i in range(existing + 1, existing + need + 1):
                uid = f'dev_test_user_{i}'
                data.append({
                    'id_user': uid,
                    'login': f'user{i}',
                    'first_name': 'User',
                    'last_name': str(i),
                    'premium': '',
                    'join_date': now,
                    'last_time': now,
                    'need_paid': (i % 3 == 0),
                    'received_forecast': (i % 5 == 0),
                    'is_subs': (i % 2 == 0),
                    'send_payments': False,
                    'wants_forecast': (i % 7 == 0),
                    'get_offer': False,
                    'other': ''
                })

            await session.execute(insert(Users), data)
            await session.commit()
            return True
    except Exception:
        return False
        