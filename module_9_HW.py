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

GREETING_MSG = 'How can I help you?'

ALIASES = {'exit': ['good bye', 'close', 'cya',
                    'see you', 'asta la vista'],
           'help': ['how to', 'idk', 'command'],
           'show': ['show all', 'exhibit', 'reveal'],
           'hello': ['hi', 'greetings', 'good morning',
                     'good afternoon', 'good evening', 'yo'],
           'add': ['plus', 'write']}

contacts = {}  # Contacts storage
loop = True  # Exit controller


def hello():
    """Prints greeting message"""
    status = None

    return status, GREETING_MSG


def input_error(handler):
    def inner(*args):
        error = ''
        try:
            return_values = handler(*args)
        except KeyError as ke:
            match handler.__name__:
                # Key error in add - contact allready exist
                case 'add':
                    error += ('Contact`ve been already recorded.',
                              + ' Try another name.')\
                        if 'contact_exists' in str(ke.args) \
                        else 'Unhandled KeyError raised while adding contact.'
                # KeyError in change | phone - contact does not exist
                case 'change' | 'phone':
                    error += 'Contact does not exist. Try another name.' \
                        if '!contact_exists' in str(ke.args) \
                        else ('Unhandled KeyError raised in'
                              + f' {handler.__name__}.')
                case _:
                    error += f'Unhandled KeyError in {handler.__name__}'
        except ValueError as ve:
            match handler.__name__:
                # no_contact|no_number|wrong_contact|wrong_number|contact_or_phone_mis
                case 'add' | 'change' | 'phone':
                    if 'no_contact_number' in str(ve.args):
                        error += ('Provide valid contact name\\'
                                  + 'phone number to proceed\n')
                    if 'no_contact' in str(ve.args):
                        error += ('Provide contact name to proceed\n')
                    if 'no_number' in str(ve.args):
                        error += ('Provide phone number to proceed\n')
                    if 'wrong_number' in str(ve.args):
                        error += 'Provided phone number is not valid\n'
                    if 'wrong_contact' in str(ve.args):
                        error += 'Provided contact name is not valid\n'
                    if 'contact_or_phone_mis' in str(ve.args):
                        error += ('Both contact name and phone number'
                                  + ' are needed to proceed\n')
                    error += (f'Type "help {handler.__name__}"'
                              + ' for detailed info')
                case _:
                    error = f'Unhandled KeyError in {handler.__name__}'
        except IndexError as ie:
            match handler.__name__:
                case 'show_all':
                    if 'empty_list' in str(ie.args):
                        error += ('Nothing to show -'
                                  + ' contacts base got no records.\n'
                                  + 'Try to fill it first.')
                case _:
                    error = f'Unhandled IndexError in {handler.__name__}'
        finally:
            return_values = return_values if not error \
                else ('Error', error)
        return return_values

    return inner


def _check_user_phone(user_phone=''):
    error = ''
    one_of_two_pattern = r'[\w\d]+ [\w\d]+'

    # validating contact and phone number
    if not user_phone:
        error += 'no_contact_number'
    elif not re.match(one_of_two_pattern, user_phone):
        error += 'contact_or_phone_mis'
    if error:
        raise ValueError(error)


def _check_user(user_=''):
    """Validates user name"""
    error = ''

    user_pattern = r'^[A-Za-z]+'
    user_match = re.match(user_pattern, user_)
    if not user_match or user_match.group() != user_:
        error += 'wrong_contact|'

    return error


def _is_user(user_=''):
    error = ''
    if user_ not in contacts:
        error += '!contact_exists'

    if '!contact_exists' in error:
        raise KeyError(error)
    elif error:
        raise ValueError(error)


def _check_number(phone_=''):
    """Validates phone number"""
    error = ''
    # phones with 6, 7, 10 or 12 digits are acceptable
    phone_pattern = r'\d{12}|\d{10}|\d{7}|\d{6}'
    phone_match = re.match(phone_pattern, phone_)
    if not phone_match or phone_match.group() != phone_:
        error += 'wrong_number|'

    return error


@input_error
def add(user_phone=''):
    """Adds new contact with phone number"""
    status = 'OK'
    message = ''
    error = ''

    _check_user_phone(user_phone)

    user_, phone_ = user_phone.rsplit(' ', maxsplit=1)

    error += _check_number(phone_)
    error += _check_user(user_)

    if user_ in contacts:
        error += 'contact_exists'

    if 'contact_exists' in error:
        raise KeyError(error)
    elif error:
        raise ValueError(error)

    # everything`s OK adding contact
    contacts[user_] = phone_
    message = f'{user_}`s added.'

    return status, message


@input_error
def change(user_phone=''):
    """Changes recorder phone number for given contact"""
    status = 'OK'
    message = ''
    error = ''

    _check_user_phone(user_phone)

    user_, phone_ = user_phone.rsplit(' ', maxsplit=1)

    error += _check_number(phone_)
    error += _check_user(user_)

    _is_user(user_)

    # everything`s OK adding contact
    contacts[user_] = phone_
    message = f'{user_}`s phone is changed.'

    return status, message


@input_error
def phone(user_=''):
    """Displays phone number for given contact"""
    status = 'OK'
    message = ''
    error = ''

    if not user_:
        error += 'no_contact'
        raise ValueError(error)

    error += _check_user(user_)
    if error:
        raise ValueError(error)

    _is_user(user_)

    message = f'{user_}`s phone is: {contacts[user_]}'

    return status, message


@input_error  # IndexError - empty
def show_all():
    """Displays all recorded contacts"""
    status = 'OK'
    message = ''
    error = ''

    if len(contacts) == 0:
        error += 'empty_list'
        raise IndexError(error)

    header = (f'+{"=":=^15}+{"=":=^15}+\n'
              + f'|{"CONTACT NAME":^15}|{"PHONE NUMBER":^15}|\n'
              + f'+{"-":-^15}+{"-":-^15}+\n')
    footer = f'+{"-":-^15}+{"-":-^15}+\n'
    message += header

    for name, number in contacts.items():
        name = name if len(name) < 12 else name[:12]+'...'
        message += (f'|{name.capitalize():^15}|{number:^15}|\n'
                    + footer)

    return status, message


def exit():
    """Job is done let`s go home"""
    global loop
    loop = False
    status = None
    message = BYE

    return status, message


def help(command=''):
    """Prints help"""
    cmd_ = command

    status = None

    alias_str = ', '.join(ALIASES[command]) if command in ALIASES else ''
    alias_str = f'alias(es) for {command} is(are): {alias_str}' \
        if alias_str else ''

    for com, aliases in ALIASES.items():
        if cmd_ in aliases:
            command = com
            alias_str = f'Is alias for {command}'
            break

    message = 'Usage: '
    match command:
        case 'add':
            message += f'{cmd_} <contact_name> <phone_number>\n{alias_str}\n'
            message += ('Adds  contact with name <contact_name>'
                        + ' and phone number <phone_number> to contact base.\n'
                        + '<conact_name> contains only one word and'
                        + ' <phone_number> - only digits,'
                        + ' phones with 6, 7, 10 or 12 digits are acceptable')
        case 'exit':
            message += f'{cmd_}\n{alias_str}\n'
            message += 'Prints farewell message and exits'
        case 'show':
            message += f'{cmd_}\n{alias_str}\n'
            message += 'Shows all recorded contacts'
        case 'hello':
            message += f'{cmd_}\n{alias_str}\n'
            message += 'Shows greeting message'
        case 'change':
            message += f'{cmd_} <contact_name> <phone_number>\n{alias_str}\n'
            message += ('Changes recorded phone number of <contact_name>'
                        + ' to  <phone_number>.\n'
                        + '<conact_name> contains only one word and'
                        + ' <phone_number> - only digits,'
                        + ' phones with 6, 7, 10 or 12 digits are acceptable')
        case 'phone':
            message += f'{cmd_} <contact_name>\n{alias_str}\n'
            message += ('Shows recorded phone number for <contact_name>\n'
                        + '<conact_name> contains only one word')
        case 'help':
            message += f'{cmd_} <command>\n{alias_str}\n'
            message += ('Displays help info for <command>'
                        + ' and its aliases.\n'
                        + 'List of available commands: hello, add,'
                        + ' change, phone, show, exit, help.\n')
        case _:
            message += '<command> [<parameters>]\n'
            message += ('Bot provides a storage for contacts.'
                        + ' Common operations such as adding, changing,\n'
                        + ' showing contact`s info etc are supported.\n'
                        + 'List of available commands: hello, add,'
                        + ' change, phone, show, exit, help.\n'
                        + 'Type "help <command> for details')

    return status, message


def parse_input_():
    """Preparative part of parse_input - saving state
    for quick_access_aliases
    """
    quick_access_aliases = {}
    for command, alias_lst in ALIASES.items():
        quick_access_aliases.update({alias: command for alias in alias_lst})

    appendix = [ALIASES[i][j] for i in ALIASES
                for j in range(len(ALIASES[i]))]
    appendix = '|'.join(appendix)
    command_pattern = (r'^(hello|add|change|phone|show|exit|help|'
                       + rf'{appendix})')

    def inner(sequence=''):
        """Main part of input parser"""
        command = ''
        args = ''
        if not sequence:
            return 'help', ''

        match_res = re.match(command_pattern, sequence, re.I)
        if match_res:
            command = match_res.group()
            command = command if command not in quick_access_aliases \
                else quick_access_aliases[command]
            args = sequence[match_res.span()[1]:].lstrip()
        else:
            command = 'help'
            args = ''

        return command, args

    return inner


def main():
    print(HEADER)

    commands = {
        'hello': {'func': hello, 'args': False},
        'add': {'func': add, 'args': True},
        'change': {'func': change, 'args': True},
        'phone': {'func': phone, 'args': True},
        'show': {'func': show_all, 'args': False},
        'exit': {'func': exit, 'args': False},
        'help': {'func': help, 'args': True}
    }

    parse_input = parse_input_()

    while loop:
        sequence = input(">>> ").lstrip().lower()

        command, args = parse_input(sequence)

        if not command:
            command = 'help'
        if args and commands[command]['args']:
            status, message = commands[command]['func'](args)
        else:
            status, message = commands[command]['func']()
        if status:
            print(f'{command}: {status}')
            print(message)
        else:
            print(message)


if __name__ == "__main__":
    main()
