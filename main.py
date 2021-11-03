from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types.input_media import InputMediaPhoto
from aiogram.utils import executor
from aiogram.types.input_file import InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from kampus import KAMPUS
from teachers import TEACHERS
from FSM_states import CommandStates
from token import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())

@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message):
    await bot.send_message(msg.from_user.id, "Введите команду /help")

@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    await msg.reply("Напиши /find_teacher для поиска преподавателя или /find_cabinet для поиска нужной тебе аудитории!")

@dp.message_handler(commands=['find_teacher'])
async def process_find_teacher_command(msg: types.Message):
    state = dp.current_state(user=msg.from_user.id)
    await state.set_state('find_teacher_state')
    await msg.reply("Введите фамилию преподавателя:")

@dp.message_handler(state = CommandStates.FIND_TEACHER_STATE)
async def find_teacher_message(msg: types.Message):
    second_name = msg.text
    try:
        if not second_name.isalpha():
            raise TypeError
        if second_name in TEACHERS:
            teacher = TEACHERS[second_name]
            message = f"Фамилия: {second_name}; Имя: {teacher['first_name']}"
            await bot.send_message(msg.from_user.id, message)
            media = []
            for photo_id in teacher['photo']:
                media.append(InputMediaPhoto(InputFile(photo_id)))
            await bot.send_media_group(msg.from_user.id, media)
            message = f"Корпус: {teacher['building_number']}; Аудитория: {teacher['cabinet_number']}"
            await bot.send_message(msg.from_user.id, message)
        else:
            await bot.send_message(msg.from_user.id, "Такого преподавателя нет в базе!")
        
    except TypeError:
        await bot.send_message(msg.from_user.id, "Такой фамилии быть не может!")
    state = dp.current_state(user=msg.from_user.id)
    await state.reset_state()

@dp.message_handler(commands=['find_cabinet'])
async def process_find_cabinet_command(msg: types.Message):
    state = dp.current_state(user=msg.from_user.id)

    await state.set_state('find_cabinet_state')
    await msg.reply("Введите номер корпуса и кабинета:\n(Пример: <номер корпуса> <номер кабинета>")


@dp.message_handler(state = CommandStates.FIND_CABINET_STATE)
async def find_cabinet_message(msg: types.Message):
    message = msg.text
    building_number, cabinet_number = message.split()

    try:
        # Validate format of input
        if cabinet_number.isalnum():
            building_number = building_number.lower()
        else:
            raise TypeError

        if cabinet_number.isalnum():
            cabinet_number = cabinet_number.lower()
            floor_number = cabinet_number[0]
        else: 
            raise TypeError

        message = "Корпус: {0}; Кабинет: {1}".format(building_number, cabinet_number)
        await bot.send_message(msg.from_user.id, message)
        
        # Try to find building and send photo of building
        if building_number in KAMPUS:

            building = KAMPUS[building_number]
            await bot.send_location(msg.from_user.id, building['lat'], building['lot'])

            media = []
            for photo_id in building['building']: 
                media.append(InputMediaPhoto(InputFile(photo_id)))
            await bot.send_media_group(msg.from_user.id, media)

            if floor_number in building:

                floor = building[floor_number]

                media = []
                for photo_id in floor['floor']:
                    media.append(InputMediaPhoto(InputFile(photo_id)))

                await bot.send_media_group(msg.from_user.id, media)

                # with open(floor['floor'], 'rb') as photo:
                #     await bot.send_photo(msg.from_user.id, photo, caption="Этаж")

                if cabinet_number in floor:
                    media = []
                    for photo_id in floor[cabinet_number]:
                        media.append(InputMediaPhoto(InputFile(photo_id)))
                    await bot.send_media_group(msg.from_user.id, media)

                #     with open(floor[cabinet_number], 'rb') as photo:
                #         await bot.send_photo(msg.from_user.id, photo, caption="Кабинет")

                else:
                    await bot.send_message(msg.from_user.id, "Такого кабинета не существует!")
            else:
                await bot.send_message(msg.from_user.id, "Такого этажа не существует!")
        else:
            await bot.send_message(msg.from_user.id, "Такого корпуса не существует!")
        state = dp.current_state(user=msg.from_user.id)
        await state.reset_state()

    except TypeError:
        await bot.send_message(msg.from_user.id, "Кабине или корпус введен неверно!")


if __name__ == '__main__':
    executor.start_polling(dp)