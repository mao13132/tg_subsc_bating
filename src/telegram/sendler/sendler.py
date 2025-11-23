from aiogram import types
from aiogram.types import Message
from datetime import datetime

from settings import ADMIN, DEVELOPER, LOGGER, LOGO
from src.telegram.bot_core import BotDB


class Sendler_msg:
    @staticmethod
    async def _get_logo_file_id():
        try:
            return await BotDB.get_setting('logo_file_id')
        except:
            return False

    async def sender_to_user_by_id(bot, id_user, text, keyb):
        try:
            res_send = await bot.send_message(id_user, text, reply_markup=keyb, disable_web_page_preview=True,
                                              protect_content=True)
        except:
            return False

        return res_send

    async def sendler_to_admin_mute_bot(bot, text, keyb):
        res_send = False
        for admin in ADMIN:
            try:
                res_send = await bot.send_message(int(admin), text, reply_markup=keyb, disable_notification=True,
                                                  protect_content=True)
            except:
                continue

        return res_send

    async def sendler_to_admin_mute(message: Message, text, keyb):
        res_send = False
        for admin in ADMIN:
            try:
                res_send = await message.bot.send_message(int(admin), text, reply_markup=keyb,
                                                          disable_notification=True,
                                                          protect_content=True)
            except:
                try:
                    res_send = await message.bot.send_message(int(admin), text, protect_content=True)
                except Exception as es:
                    if str(es) == 'Chat not found':
                        print(f'Бот не имеет права писать админу, напишите /start боту')
                    else:
                        print(f'Ошибка при отправке сообщение админу текст: "{text}" {es}')
        return res_send

    async def sendler_to_admin(message: Message, text, keyb):
        res_send = False
        for admin in ADMIN:
            try:
                res_send = await message.bot.send_message(int(admin), text, reply_markup=keyb, protect_content=True)
            except:
                try:
                    res_send = await message.bot.send_message(int(admin), text, protect_content=True)
                except Exception as es:
                    if str(es) == 'Chat not found':
                        print(f'Бот не имеет права писать админу, напишите /start боту')
                    else:
                        print(f'Ошибка при отправке сообщение админу текст: "{text}" {es}')
        return res_send

    async def forward_to_admin(message: Message):
        for admin in ADMIN:
            try:
                res_send = await message.bot.forward_message(int(admin), message.chat.id, message.message_id,
                                                             protect_content=True)

                return res_send
            except Exception as es:
                if str(es) == 'Chat not found':
                    print(f'Бот не имеет права писать админу, напишите /start боту')
                else:
                    print(f'Ошибка при forward сообщение админу forward_to_admin {es}')

                return False

    async def reply_message_to_admin(message: Message, _msg, keyb, reply_msg):
        for admin in ADMIN:
            try:

                res_send = await reply_msg.reply(text=_msg, reply_markup=keyb, protect_content=True)

                return res_send

            except:
                try:
                    res_send = await message.bot.send_message(int(admin), _msg, reply_markup=keyb, protect_content=True)
                except Exception as es:
                    if str(es) == 'Chat not found':
                        print(f'Бот не имеет права писать админу, напишите /start боту')
                    else:
                        print(f'Ошибка при forward сообщение админу forward_to_admin {es}')

                    return False

    async def sendler_admin_call(call: types.CallbackQuery, text, keyb):
        res_send = False
        for admin in ADMIN:
            try:
                res_send = await call.bot.send_message(int(admin), text, reply_markup=keyb,
                                                       disable_web_page_preview=True,
                                                       protect_content=True)
            except:
                try:
                    res_send = await call.bot.send_message(int(admin), text, disable_web_page_preview=True,
                                                           protect_content=True)
                except Exception as es:
                    if str(es) == 'Chat not found':
                        print(f'Бот не имеет права писать админу {admin}, напишите /start боту')
                    else:
                        print(f'Ошибка при отправке сообщение админу текст {admin},: "{text}" {es}')
        return res_send

    async def send_msg_call(call: types.CallbackQuery, text_msg, keyb):
        if call.message.photo:
            try:
                # Отправляем новое текстовое сообщение
                res_send = await call.message.bot.send_message(call.message.chat.id, text_msg,
                                                               reply_markup=keyb, disable_web_page_preview=True,
                                                               protect_content=True)
                # Удаляем сообщение с медиа файлом
                try:
                    await call.message.delete()
                except:
                    pass

                return res_send
            except Exception as es:
                # print(f'Ошибка при удалении медиа и отправке нового сообщения: "{text_msg}" ошибка: "{es}"')
                return False

        try:
            # await call.message.edit_caption(caption=text_msg, reply_markup=keyb)
            res_send = await call.message.edit_text(text=text_msg, reply_markup=keyb, disable_web_page_preview=True)
        except Exception as es:
            try:
                res_send = await call.message.bot.send_message(call.message.chat.id, text_msg,
                                                               reply_markup=keyb, protect_content=True,
                                                               disable_web_page_preview=True)
            except Exception as es:
                print(f'Произошла ошибка при отправке поста текст: "{text_msg}" ошибка: "{es}"')
                return False

        return res_send

    async def send_msg_message(message: Message, text_msg, keyb):
        if message.photo:
            try:
                # Отправляем новое текстовое сообщение
                res_send = await message.bot.send_message(message.chat.id, text_msg,
                                                          reply_markup=keyb, disable_web_page_preview=True,
                                                          protect_content=True)
                # Удаляем сообщение с медиа файлом
                try:
                    await message.delete()
                except:
                    pass

                return res_send
            except Exception as es:
                # print(f'Ошибка при удалении медиа и отправке нового сообщения: "{text_msg}" ошибка: "{es}"')
                return False

        res_send = False
        if message.photo != []:

            try:
                res_send = await message.bot.send_message(message.chat.id, text_msg,
                                                          reply_markup=keyb, disable_web_page_preview=True,
                                                          protect_content=True)
            except Exception as es:
                print(f'Произошла ошибка при отправке поста текст: "{text_msg}" ошибка: "{es}"')
                return False
        else:
            try:
                res_send = await message.edit_text(text=text_msg, reply_markup=keyb, disable_web_page_preview=True)
            except:
                try:
                    res_send = await message.edit_caption(caption=text_msg, reply_markup=keyb)
                except:
                    try:
                        res_send = await message.bot.send_message(message.chat.id, text_msg,
                                                                  reply_markup=keyb, disable_web_page_preview=True,
                                                                  protect_content=True)
                    except Exception as es:
                        print(f'Произошла ошибка при отправке поста текст2: "{text_msg}" ошибка: {es}"')
                        return False

        return res_send

    async def send_call_message(call: types.CallbackQuery, text_msg, keyb):
        res_send = False
        if call.message.photo != []:

            try:
                res_send = await call.message.bot.send_message(call.message.chat.id, text_msg,
                                                               reply_markup=keyb, protect_content=True)
            except:
                print(f'Произошла ошибка при отправке поста текст: "{text_msg}" send_call_message"')
                return False
        else:
            try:
                res_send = await call.message.edit_text(text=text_msg, reply_markup=keyb)
            except:
                try:
                    res_send = await call.message.edit_caption(caption=text_msg, reply_markup=keyb)
                except Exception as es:
                    try:
                        res_send = await call.message.bot.send_message(call.message.chat.id, text_msg,
                                                                       reply_markup=keyb, protect_content=True)
                    except:
                        print(f'Произошла ошибка при отправке поста текст: "{text_msg}" send_call_message2 {es}"')
                        return False

        return res_send

    async def reply_user(message: Message, text_msg):
        try:
            res_send = await message.reply(text_msg, protect_content=True)
        except Exception as es:
            print(f'Произошла ошибка при reply_user текст: "{text_msg}" ошибка: "{es}"')
            return False

        return res_send

    async def log_client_call(call: types.CallbackQuery):

        _msg = (f'\n{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))} '
                f'"{call.message.chat.full_name}" @{call.message.chat.username} Кликает по кнопке "{call.data}"\n')

        print(_msg)

        try:
            await call.bot.answer_callback_query(call.id)
        except Exception as es:
            print(f'Уведомление: {es}')

        id_user = call.message.chat.id

        await BotDB.edit_user('last_time', datetime.now(), id_user)

        res_send = True
        if LOGGER and id_user != DEVELOPER:
            try:
                res_send = await call.message.bot.send_message(DEVELOPER, _msg, disable_notification=True,
                                                               protect_content=True)
            except:
                pass
        return res_send

    async def log_client_message(message: Message):

        _msg = (f'{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))} '
                f'"{message.chat.full_name}" @{message.chat.username} написал "{message.text}"\n')

        print(_msg)

        id_user = message.chat.id

        await BotDB.edit_user('last_time', datetime.now(), id_user)

        res_send = True
        if LOGGER and id_user != DEVELOPER:
            try:
                res_send = await message.bot.send_message(DEVELOPER, _msg, disable_notification=True,
                                                          protect_content=True)
            except:
                pass
        return res_send

    async def sendler_photo_call(self, call, photo, text, keyb):
        try:
            logo_file_id = await Sendler_msg._get_logo_file_id()
            if logo_file_id:
                try:
                    file_photo = types.InputMediaPhoto(logo_file_id)
                    res_send = await call.message.edit_media(media=file_photo)
                    res_send = await call.message.edit_caption(caption=text, reply_markup=keyb)
                    return res_send
                except:
                    try:
                        res_send = await call.message.bot.send_photo(call.message.chat.id, logo_file_id,
                                                                     caption=text, reply_markup=keyb,
                                                                     protect_content=True)
                        return res_send
                    except:
                        try:
                            with open(photo, 'rb') as file:
                                file_photo = types.InputMediaPhoto(file)
                                res_send = await call.message.edit_media(media=file_photo)
                                res_send = await call.message.edit_caption(caption=text, reply_markup=keyb)
                                return res_send
                        except:
                            try:
                                with open(photo, 'rb') as file:
                                    res_send = await call.message.bot.send_photo(call.message.chat.id, file,
                                                                                 caption=(text),
                                                                                 reply_markup=keyb,
                                                                                 protect_content=True)
                                    return res_send
                            except Exception as es:
                                print(f'Ошибка при отправке сообщения call с фото {es}')
                                return False
        except:
            pass
        try:
            with open(photo, 'rb') as file:
                file_photo = types.InputMediaPhoto(file)
                res_send = await call.message.edit_media(media=file_photo)
                res_send = await call.message.edit_caption(caption=text, reply_markup=keyb)
                return res_send
        except:
            try:
                with open(photo, 'rb') as file:
                    res_send = await call.message.bot.send_photo(call.message.chat.id, file, caption=(text),
                                                                 reply_markup=keyb, protect_content=True)
                    return res_send
            except Exception as es:
                print(f'Ошибка при отправке сообщения call с фото {es}')
                return False

    async def new_sendler_photo_call(self, call, photo, text, keyb):
        logo_file_id = await Sendler_msg._get_logo_file_id()

        try:
            if logo_file_id:
                res_send = await call.message.bot.send_photo(call.message.chat.id, logo_file_id, caption=(text),
                                                             reply_markup=keyb, protect_content=True)
                return res_send
        except:
            logo_file_id = False

        if not logo_file_id:
            try:
                with open(photo, 'rb') as file:
                    res_send = await call.message.bot.send_photo(call.message.chat.id, file, caption=(text),
                                                                 reply_markup=keyb, protect_content=True)
                    return res_send
            except Exception as es:
                print(f'Ошибка при отправке сообщения new_sendler_photo_call с фото {es}')
                return False

        return False

    async def new_sender_message_call(self, call, text, keyb):
        try:
            res_send = await call.message.bot.send_message(call.message.chat.id, text,
                                                           reply_markup=keyb, protect_content=True)
        except Exception as es:
            print(f'Ошибка при отправке сообщения new_sender_message_call {es}')
            return False

        return res_send

    async def sendler_photo_call_html(self, call, photo, text, keyb):
        try:
            logo_file_id = await Sendler_msg._get_logo_file_id()
            if logo_file_id:
                try:
                    file_photo = types.InputMediaPhoto(logo_file_id)
                    res_send = await call.message.edit_media(media=file_photo)
                    res_send = await call.message.edit_caption(caption=text, reply_markup=keyb)
                    return res_send
                except:
                    try:
                        res_send = await call.message.bot.send_photo(call.message.chat.id, logo_file_id, caption=text,
                                                                     reply_markup=keyb, protect_content=True)
                        return res_send
                    except:
                        try:
                            with open(photo, 'rb') as file:
                                file_photo = types.InputMediaPhoto(file)
                                res_send = await call.message.edit_media(media=file_photo)
                                res_send = await call.message.edit_caption(caption=text, reply_markup=keyb)
                                return res_send
                        except:
                            try:
                                with open(photo, 'rb') as file:
                                    res_send = await call.message.bot.send_photo(call.message.chat.id, file,
                                                                                 caption=text,
                                                                                 reply_markup=keyb,
                                                                                 protect_content=True)
                                    return res_send
                            except Exception as es:
                                print(f'Ошибка при отправке сообщения call с фото {es}')
                                return False
        except:
            pass
        try:
            with open(photo, 'rb') as file:
                file_photo = types.InputMediaPhoto(file)
                res_send = await call.message.edit_media(media=file_photo)
                res_send = await call.message.edit_caption(caption=text, reply_markup=keyb)
                return res_send
        except:
            try:
                with open(photo, 'rb') as file:
                    res_send = await call.message.bot.send_photo(call.message.chat.id, file, caption=text,
                                                                 reply_markup=keyb, protect_content=True)
                    return res_send
            except Exception as es:
                print(f'Ошибка при отправке сообщения call с фото {es}')
                return False

        return False

    async def sendler_photo_message(self, message, photo, text, keyb):
        try:
            logo_file_id = await Sendler_msg._get_logo_file_id()
            if logo_file_id:
                try:
                    file_photo = types.InputMediaPhoto(logo_file_id)
                    res_send = await message.edit_media(media=file_photo)
                    res_send = await message.edit_caption(caption=text, reply_markup=keyb)
                    return res_send
                except:
                    try:
                        res_send = await message.bot.send_photo(message.chat.id, logo_file_id, caption=(text),
                                                                reply_markup=keyb, protect_content=True)
                        return res_send
                    except:
                        try:
                            with open(photo, 'rb') as file:
                                file_photo = types.InputMediaPhoto(file)
                                res_send = await message.edit_media(media=file_photo)
                                res_send = await message.edit_caption(caption=text, reply_markup=keyb)
                                return res_send
                        except:
                            try:
                                with open(photo, 'rb') as file:
                                    res_send = await message.bot.send_photo(message.chat.id, file, caption=(text),
                                                                            reply_markup=keyb, protect_content=True)
                                    return res_send
                            except Exception as es:
                                print(f'Ошибка при отправке сообщение msg с фото {es}')
                                return False
        except:
            pass
        try:
            with open(photo, 'rb') as file:
                file_photo = types.InputMediaPhoto(file)
                res_send = await message.edit_media(media=file_photo)
                res_send = await message.edit_caption(caption=text, reply_markup=keyb)
                return res_send
        except:
            try:
                with open(photo, 'rb') as file:
                    res_send = await message.bot.send_photo(message.chat.id, file, caption=(text),
                                                            reply_markup=keyb, protect_content=True)
                    return res_send
            except Exception as es:
                print(f'Ошибка при отправке сообщение msg с фото {es}')
                return False

        return False

    async def sender_photo_bot(self, bot, id_user, photo, text, keyb):
        try:
            logo_file_id = await Sendler_msg._get_logo_file_id()
            if logo_file_id:
                res_send = await bot.send_photo(id_user, logo_file_id, caption=text, reply_markup=keyb,
                                                protect_content=True)
                return res_send
        except:
            try:
                with open(photo, 'rb') as file:
                    res_send = await bot.send_photo(id_user, file, caption=text, reply_markup=keyb,
                                                    protect_content=True)
                    return res_send
            except Exception as es:
                print(f'Ошибка при отправке сообщение sender_photo_bot с фото {es}')
                return False

        return False

    async def new_sendler_photo_message(self, message, photo, text, keyb):
        try:
            logo_file_id = await Sendler_msg._get_logo_file_id()
            if logo_file_id:
                res_send = await message.bot.send_photo(message.chat.id, logo_file_id, caption=(text),
                                                        reply_markup=keyb, protect_content=True)
                return res_send
        except:
            try:
                with open(photo, 'rb') as file:
                    res_send = await message.bot.send_photo(message.chat.id, file, caption=(text),
                                                            reply_markup=keyb, protect_content=True)
                    return res_send
            except Exception as es:
                print(f'Ошибка при отправке сообщение new_sendler_photo_message с фото {es}')
                return False

        return False
