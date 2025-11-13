import json
import os

from settings import project_path


async def init_texts_from_json(BotDB):
    try:
        json_path = os.path.join(project_path, 'texts.json')

        if not os.path.exists(json_path):
            from src.utils.logger._logger import logger_msg
            logger_msg(f'Файл texts.json не найден по пути: {json_path}')
            return False

        with open(json_path, 'r', encoding='utf-8') as f:
            texts_data = json.load(f)

        bulk_texts = []

        for key, value in texts_data.get('buttons', {}).items():
            bulk_texts.append({'text_type': 'buttons', 'key': key, 'value': value})

        for key, value in texts_data.get('messages', {}).items():
            bulk_texts.append({'text_type': 'messages', 'key': key, 'value': value})

        if bulk_texts:
            created_count = await bulk_init_texts(BotDB, bulk_texts)

            from src.utils.logger._logger import logger_msg
            print(f'Инициализировано {created_count} текстов из {len(bulk_texts)} записей')

        return True

    except Exception as es:
        from src.utils.logger._logger import logger_msg
        error_ = f'Ошибка инициализации текстов: "{es}"'
        logger_msg(error_)
        return False


async def bulk_init_texts(BotDB, texts_data):
    created_count = 0

    try:
        existing_buttons = await BotDB.texts.get_button_texts()
        existing_messages = await BotDB.texts.get_message_texts()

        new_texts = []
        for text_data in texts_data:
            text_type = text_data['text_type']
            key = text_data['key']

            if text_type == 'buttons' and key not in existing_buttons:
                new_texts.append(text_data)
            elif text_type == 'messages' and key not in existing_messages:
                new_texts.append(text_data)

        if new_texts:
            created_count = await BotDB.texts.bulk_create_texts(new_texts)

        return created_count

    except Exception as es:
        from src.utils.logger._logger import logger_msg
        error_ = f'Ошибка массовой инициализации текстов: "{es}"'
        logger_msg(error_)
        return 0
        