from aiogram import types
from aiogram.types import Message
from datetime import datetime

from settings import ADMIN, DEVELOPER, LOGGER
from src.telegram.bot_core import BotDB


class Sendler_msg:

    async def sender_to_user_by_id(bot, id_user, text, keyb):
        try:
            res_send = await bot.send_message(id_user, text, reply_markup=keyb, disable_web_page_preview=True)
        except:
            return False

        return res_send

    async def sendler_to_admin_mute_bot(bot, text, keyb):
        for admin in ADMIN:
            try:
                await bot.send_message(int(admin), text, reply_markup=keyb, disable_notification=True)
            except:
                continue

        return True

    async def sendler_to_admin_mute(message: Message, text, keyb):
        for admin in ADMIN:
            try:
                await message.bot.send_message(int(admin), text, reply_markup=keyb, disable_notification=True)
            except:
                try:
                    await message.bot.send_message(int(admin), text)
                except Exception as es:
                    if str(es) == 'Chat not found':
                        print(f'Бот не имеет права писать админу, напишите /start боту')
                    else:
                        print(f'Ошибка при отправке сообщение админу текст: "{text}" {es}')

    async def sendler_to_admin(message: Message, text, keyb):
        for admin in ADMIN:
            try:
                await message.bot.send_message(int(admin), text, reply_markup=keyb)
            except:
                try:
                    await message.bot.send_message(int(admin), text)
                except Exception as es:
                    if str(es) == 'Chat not found':
                        print(f'Бот не имеет права писать админу, напишите /start боту')
                    else:
                        print(f'Ошибка при отправке сообщение админу текст: "{text}" {es}')

    async def forward_to_admin(message: Message):
        for admin in ADMIN:
            try:
                msg = await message.bot.forward_message(int(admin), message.chat.id, message.message_id)

                return msg
            except Exception as es:
                if str(es) == 'Chat not found':
                    print(f'Бот не имеет права писать админу, напишите /start боту')
                else:
                    print(f'Ошибка при forward сообщение админу forward_to_admin {es}')

                return False

    async def reply_message_to_admin(message: Message, _msg, keyb, reply_msg):
        for admin in ADMIN:
            try:

                msg = await reply_msg.reply(text=_msg, reply_markup=keyb)

                return msg

            except:
                try:
                    await message.bot.send_message(int(admin), _msg, reply_markup=keyb)
                except Exception as es:
                    if str(es) == 'Chat not found':
                        print(f'Бот не имеет права писать админу, напишите /start боту')
                    else:
                        print(f'Ошибка при forward сообщение админу forward_to_admin {es}')

                    return False

    async def sendler_admin_call(call: types.CallbackQuery, text, keyb):
        for admin in ADMIN:
            try:
                await call.bot.send_message(int(admin), text, reply_markup=keyb, disable_web_page_preview=True)
            except:
                try:
                    await call.bot.send_message(int(admin), text, disable_web_page_preview=True)
                except Exception as es:
                    if str(es) == 'Chat not found':
                        print(f'Бот не имеет права писать админу {admin}, напишите /start боту')
                    else:
                        print(f'Ошибка при отправке сообщение админу текст {admin},: "{text}" {es}')

    async def send_msg_call(call: types.CallbackQuery, text_msg, keyb):
        try:
            await call.message.edit_caption(caption=text_msg, reply_markup=keyb)
        except Exception as es:
            # print(f'Ошибка редактирования поста: {es}')
            try:
                with open(LOGO, 'rb') as file:
                    await call.message.bot.send_photo(call.message.chat.id, file, caption=(text_msg),
                                                      reply_markup=keyb)
            except:
                try:
                    await call.message.bot.send_message(call.message.chat.id, text_msg,
                                                        reply_markup=keyb)

                except Exception as es:
                    print(f'Произошла ошибка при отправке поста текст: "{text_msg}" ошибка: "{es}"')
                    return False

        return True

    async def send_msg_message(message: Message, text_msg, keyb):
        if message.photo != []:

            try:
                await message.bot.send_message(message.chat.id, text_msg,
                                               reply_markup=keyb, disable_web_page_preview=True)
            except Exception as es:
                print(f'Произошла ошибка при отправке поста текст: "{text_msg}" ошибка: "{es}"')
                return False
        else:
            try:
                await message.edit_text(text=text_msg, reply_markup=keyb, disable_web_page_preview=True)
            except:
                try:
                    await message.edit_caption(caption=text_msg, reply_markup=keyb)
                except:
                    try:
                        await message.bot.send_message(message.chat.id, text_msg,
                                                       reply_markup=keyb, disable_web_page_preview=True)
                    except Exception as es:
                        print(f'Произошла ошибка при отправке поста текст2: "{text_msg}" ошибка: {es}"')
                        return False

        return True

    async def send_call_message(call: types.CallbackQuery, text_msg, keyb):
        if call.message.photo != []:

            try:
                await call.message.bot.send_message(call.message.chat.id, text_msg,
                                                    reply_markup=keyb)
            except:
                print(f'Произошла ошибка при отправке поста текст: "{text_msg}" send_call_message"')
                return False
        else:
            try:
                await call.message.edit_text(text=text_msg, reply_markup=keyb)
            except:
                try:
                    await call.message.edit_caption(caption=text_msg, reply_markup=keyb)
                except Exception as es:
                    try:
                        await call.message.bot.send_message(call.message.chat.id, text_msg,
                                                            reply_markup=keyb)
                    except:
                        print(f'Произошла ошибка при отправке поста текст: "{text_msg}" send_call_message2 {es}"')
                        return False

        return True

    async def reply_user(message: Message, text_msg):

        try:
            await message.reply(text_msg)

        except Exception as es:
            print(f'Произошла ошибка при reply_user текст: "{text_msg}" ошибка: "{es}"')
            return False

        return True

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

        if LOGGER and id_user != DEVELOPER:
            try:
                await call.message.bot.send_message(DEVELOPER, _msg, disable_notification=True)
            except:
                pass

    async def log_client_message(message: Message):

        _msg = (f'{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))} '
                f'"{message.chat.full_name}" @{message.chat.username} написал "{message.text}"\n')

        print(_msg)

        id_user = message.chat.id

        await BotDB.edit_user('last_time', datetime.now(), id_user)

        if LOGGER and id_user != DEVELOPER:
            try:
                await message.bot.send_message(DEVELOPER, _msg, disable_notification=True)
            except:
                pass

    async def sendler_photo_call(self, call, photo, text, keyb):
        try:
            with open(photo, 'rb') as file:
                file_photo = types.InputMediaPhoto(file)

                res_send = await call.message.edit_media(media=file_photo)
                res_send = await call.message.edit_caption(caption=text, reply_markup=keyb)
        except:
            try:
                with open(photo, 'rb') as file:
                    res_send = await call.message.bot.send_photo(call.message.chat.id, file, caption=(text),
                                                                 reply_markup=keyb)
            except Exception as es:
                print(f'Ошибка при отправке сообщения call с фото {es}')
                return False

        return res_send

    async def new_sendler_photo_call(self, call, photo, text, keyb):

        try:
            with open(photo, 'rb') as file:
                await call.message.bot.send_photo(call.message.chat.id, file, caption=(text),
                                                  reply_markup=keyb)
        except Exception as es:
            print(f'Ошибка при отправке сообщения new_sendler_photo_call с фото {es}')
            return False

        return True

    async def new_sender_message_call(self, call, text, keyb):

        try:
            await call.message.bot.send_message(call.message.chat.id, text,
                                                reply_markup=keyb)
        except Exception as es:
            print(f'Ошибка при отправке сообщения new_sender_message_call {es}')
            return str(es)

        return True

    async def sendler_photo_call_html(self, call, photo, text, keyb):
        try:
            with open(photo, 'rb') as file:
                file_photo = types.InputMediaPhoto(file)

                await call.message.edit_media(media=file_photo)
                await call.message.edit_caption(caption=text, reply_markup=keyb, )
        except:
            try:
                with open(photo, 'rb') as file:
                    await call.message.bot.send_photo(call.message.chat.id, file, caption=text,
                                                      reply_markup=keyb)
            except Exception as es:
                print(f'Ошибка при отправке сообщения call с фото {es}')
                return False

        return True

    async def sendler_photo_message(self, message, photo, text, keyb):
        try:
            with open(photo, 'rb') as file:
                file_photo = types.InputMediaPhoto(file)

                await message.edit_media(media=file_photo)
                await message.edit_caption(caption=text, reply_markup=keyb)
        except:
            try:
                with open(photo, 'rb') as file:
                    await message.bot.send_photo(message.chat.id, file, caption=(text),
                                                 reply_markup=keyb)
            except Exception as es:
                print(f'Ошибка при отправке сообщение msg с фото {es}')
                return False

        return True

    async def sender_photo_bot(self, bot, id_user, photo, text, keyb):
        try:
            with open(photo, 'rb') as file:
                await bot.send_photo(id_user, file, caption=text, reply_markup=keyb)
        except Exception as es:
            print(f'Ошибка при отправке сообщение sender_photo_bot с фото {es}')
            return False

        return True

    async def new_sendler_photo_message(self, message, photo, text, keyb):

        try:
            with open(photo, 'rb') as file:
                await message.bot.send_photo(message.chat.id, file, caption=(text),
                                             reply_markup=keyb)
        except Exception as es:
            print(f'Ошибка при отправке сообщение new_sendler_photo_message с фото {es}')
            return False

        return True
