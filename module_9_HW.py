
import re

HEADER = r"""
 <*********************************************************************>
||   ____                          ____        _                        ||
||  / ___| _   _ _ __   ___ _ __  | __ )  ___ | |_                      ||
||  \___ \| | | | '_ \ / _ \ '__| |  _ \ / _ \| __|                     ||
||   ___) | |_| | |_) |  __/ |    | |_) | (_) | |_                      ||
||  |____/ \__,_| .__/ \___|_|    |____/ \___/ \__|                     ||
||    ____      |_|   _             _         _____  ___   ___   ___    ||
||   / ___|___  _ __ | |_ __ _  ___| |_ ___  |___ / / _ \ / _ \ / _ \   ||
||  | |   / _ \| '_ \| __/ _` |/ __| __/ __|   |_ \| | | | | | | | | |  ||
||  | |__| (_) | | | | || (_| | (__| |_\__ \  ___) | |_| | |_| | |_| |  ||
||   \____\___/|_| |_|\__\__,_|\___|\__|___/ |____/ \___/ \___/ \___/   ||
||                                                                      ||
||                      by DmytroT, 2023                                ||
 <**********************************************************************>
"""

BYE = r"""

   _____                 _   ____             _ 
  / ____|               | | |  _ \           | |
 | |  __  ___   ___   __| | | |_) |_   _  ___| |
 | | |_ |/ _ \ / _ \ / _` | |  _ <| | | |/ _ \ |
 | |__| | (_) | (_) | (_| | | |_) | |_| |  __/_|
  \_____|\___/ \___/ \__,_| |____/ \__, |\___(_)
                                    __/ |       
                                   |___/        

"""


def hello():
    pass


def add():
    pass


def change():
    pass


def phone():
    pass


def show_all():
    pass


def exit():
    pass


def help(command=''):
    pass

def parse_input_():

    aliases = {'exit': ['good bye', 'close', 'cya',
                        'see you', 'asta la vista'],
               'help': ['how to', 'idk'],
               'show': ['show all', 'exhibit', 'reveal'],
               'hello': ['hi', 'greetings', 'good morning',
                         'good afternoon', 'good evening', 'yo']}

    quick_access_aliases = {}
    for command, alias_lst in aliases.items():
        quick_access_aliases.update({alias: command for alias in alias_lst})

    appendix = [aliases[i][j] for i in aliases
                for j in range(len(aliases[i]))]
    appendix = '|'.join(appendix)

    command_pattern = (r'^(hello|add|change|phone|show|exit|help|'
                       + rf'{appendix})')
    def inner(sequence=''):
        command = ''
        args = ''
        status = 'Ok'
        match_res = re.match(command_pattern, sequence, re.I)
        if match_res:
            command = match_res.group()
            command = command if command not in quick_access_aliases \
                else quick_access_aliases[command]
            args = sequence[match_res.span()[1]:].lstrip()
        else:
            status = 'Error'
            command = 'help'
            args = f'{sequence.split()[0]} is not a command'
        return command, args, status

    return inner

# commands: hello/add/change/phone/show all/exit/help
#    add/change <contact_name> <phone>
#       contact_name: contains letters only
#       phone: contains phone number(international, internal)
#    phone <phone>
#       phone: contains phone number(international, internal)
#    show all
#        with no args
#    exit
#        with no args
#    help [<command>]
#        with no args - displays list of commands,
#        command [hello|add|change|phone|show all|exit|good bye|close]
# $command $contact_name $phone
def main():
    print(HEADER)

    parse_input = parse_input_()
    contacts = {}

    while True:
        sequence = input(">>> ")

        command, args, status = parse_input(sequence)

        print(command, args, status)


if __name__ == "__main__":
    main()
