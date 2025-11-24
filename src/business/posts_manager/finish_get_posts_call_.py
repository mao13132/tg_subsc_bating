# # ---------------------------------------------
# # Program by @developer_telegrams
# #
# #
# # Version   Date        Info
# # 1.0       2023    Initial Version
# #
# # ---------------------------------------------
# # ---------------------------------------------
# # Program by @developer_telegrams
# #
# #
# # Version   Date        Info
# # 1.0       2023    Initial Version
# #
# # ---------------------------------------------
# from aiogram import types
# from aiogram.dispatcher import FSMContext
#
# from settings import LOGO
# from src.telegram.keyboard.keyboards import Admin_keyb
# from src.telegram.sendler.sendler import Sendler_msg
#
# from src.telegram.bot_core import BotDB
#
#
# async def finish_get_posts_call(call: types.CallbackQuery, state: FSMContext):
#     await Sendler_msg.log_client_call(call)
#
#     id_user = call.message.chat.id
#
#     data = await state.get_data()
#
#     batch_key = data.get('batch_key')
#
#     res_delete = await BotDB.user_messages.delete_not_batch_key(id_user, batch_key)
#
#     await BotDB.offers.delete_all()
#
#     await state.finish()
#
#     _msg = f'✅ Прогноз загружен'
#
#     keyboard = Admin_keyb().bet_keyboard()
#
#     res_send = await Sendler_msg.send_msg_call(call, _msg, keyboard)
#
#     return True
