import os


def press_any_key():
    input('\nPress any key to continue...\n')


def lang_enumeration(and_expression='and', *kwarg):
    text = ''
    for item in kwarg:
        text += ''

    return text


def screen_clear():
   # for mac and linux(here, os.name is 'posix')
   if os.name == 'posix':
      _ = os.system('clear')
   else:
      # for windows platfrom
      _ = os.system('cls')


