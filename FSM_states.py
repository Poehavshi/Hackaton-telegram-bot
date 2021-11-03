from aiogram.utils.helper import Helper, HelperMode, ListItem

class CommandStates(Helper):
    mode = HelperMode.snake_case
    
    FIND_CABINET_STATE = ListItem()
    FIND_TEACHER_STATE = ListItem()

if __name__ == '__main__':
    print(CommandStates.all())
