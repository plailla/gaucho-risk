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
      # for windows platform
      _ = os.system('cls')


def prompt_int(prompt_text, error_text=None):
    my_int = 0
    if not error_text:
        error_text = 'Error: Please provide an integer value.'
    have_int = False
    while not have_int:
        try:
            my_int = int(input(prompt_text))
            have_int = True
        except ValueError:
            print(error_text)
    return my_int


def prompt_int_range(prompt_text, error_text, min_int, max_int):
    my_int = 0
    have_int = False
    if not error_text:
        error_text = 'Error: Please provide an integer between {} and {}.'.format(min_int, max_int)
    while not have_int:
        try:
            my_int = int(input(prompt_text))
            #print(f'Read int {my_int}, max {max_int} and min {min_int}...')
            if max_int >= my_int >= min_int:
                have_int = True
            else:
                print(error_text)
        except ValueError:
            print(error_text)
    return my_int
