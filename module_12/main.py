import pickle
import re
from pathlib import Path
from AddressBook import AddressBook, Record, Birthday, Name, Phone

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

BDAY_PATTERN = (r'\b(?:(\d{4}[\-,\.\\/]\d{2}[\-,\.\\/]\d{2})|'
                + r'(\d{2}[\-,\.\\/]\d{2}[\-,\.\\/]\d{4}))\b')
PHONE_PATTERN = r'\b\d{12}|\d{10}|\d{7}|\d{6}|\b'
NAME_PATTERN = r'\b[a-zA-Z]+[\w\.\,]+\b'

address_book = None
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
                # Key error in add - contact already exist
                case 'add':
                    if 'contact_exists' in str(ke.args):
                        error += ('Contact`ve been already recorded.'
                                  + ' Try another name.')
                    if 'phone_exists' in str(ke.args):
                        error += ('Phone`ve been already recorded.'
                                  + ' Try another one.')
                    else:
                        'Unhandled KeyError raised while adding contact.'
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
                    if 'future_date' in str(ve.args):
                        error += ('Future is not come yet.'
                                  + ' Try another date\n')
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
    pass


def _check_number(phone_=''):
    """Validates phone number"""
    error = ''
    # phones with 6, 7, 10 or 12 digits are acceptable
    phone_pattern = r'\d{12}|\d{10}|\d{7}|\d{6}'
    phone_match = re.match(phone_pattern, phone_)
    if not phone_match or phone_match.group() != phone_:
        error += 'wrong_number|'

    return error

def tokenize_args(sequence=''):
    names = []
    phones = []
    bdays = []

    tokens = sequence.split(' ')

    for token in tokens:
        if re.match(NAME_PATTERN, token):
            names.append(token)
        elif re.match(BDAY_PATTERN, token):
            bdays.append(token)
        elif re.match(PHONE_PATTERN, token):
            phones.append(token)

    return names, phones, bdays


@input_error
def add(sequence=''):
    """Adds new contact with phone number"""
    status = 'OK'
    message = ''

    names, phones, bdays = tokenize_args(sequence)

    if len(names) == 0:
        record = address_book.get_current_record()
    else:
        record = address_book.find(names[0])
        if not record:
            address_book.add_record(Record(names[0]))
            record = address_book.find(names[0])
        if len(names) > 1:
            message += ('Warning: Only 1 name can be in add command.'
                        + ' To edit name use <change> command instead.\n')
    if len(bdays) > 0:
        if record.birthday is None:
            record.birthday = bdays[0]
        else:
            message += (f'Warning: Record {record.name} has birthday set.'
                        + ' Use <change> command instead.\n')
        if len(bdays) > 1:
            message += 'Warning: Human can have only 1 birthday.\n'

    if len(phones) > 0:
        for phone in phones:
            record.add_phone(phone)

    return status, message


@input_error
def change(args=None):
    """Changes recorder phone number for given contact"""
    status = 'OK'
    message = ''
    error = ''

    return status, message


@input_error
def phone(args=None):
    """Displays phone number for given contact"""
    status = 'OK'
    message = ''
    error = ''

    return status, message


@input_error  # IndexError - empty
def show_all(record='all'):
    """Displays all recorded contacts"""
    status = 'OK'
    message = ''
    error = ''

    return status, message


@input_error
def find(search=''):
    pass


def exit_():
    """Job is done let`s go home"""
    global loop
    loop = False
    status = None
    message = BYE

    with open('data.bin', 'wb') as f_out:
        try:
            pickle.dump(address_book, f_out)
        except Exception as er:
            print(f'Error raised while saving addressbook: {str(er.args)}')
            status = 'Error'

    return status, message


def help(command=''):
    """Prints help"""
    cmd_ = command

    status = None

    message = 'Usage: '
    match command:
        case 'add':
            message += (f'{cmd_} <contact_name> [<phone_number>,'
                        + f'<birthday>]\n')
            message += ('Adds  contact with name <contact_name>,'
                        + 'phone number <phone_number> to contact base.\n'
                        + '<contact_name> contains only one word and'
                        + ' <phone_number> - only digits,'
                        + ' phones with 6, 7, 10 or 12 digits are acceptable')
        case 'exit':
            message += f'{cmd_}\n'
            message += 'Prints farewell message and exits'
        case 'show':
            message += f'{cmd_}\n'
            message += 'Shows all recorded contacts'
        case 'hello':
            message += f'{cmd_}\n'
            message += 'Shows greeting message'
        case 'change':
            message += f'{cmd_} <contact_name> <phone_number>\n'
            message += ('Changes recorded phone number of <contact_name>'
                        + ' to  <phone_number>.\n'
                        + '<contact_name> contains only one word and'
                        + ' <phone_number> - only digits,'
                        + ' phones with 6, 7, 10 or 12 digits are acceptable')
        case 'phone':
            message += f'{cmd_} <contact_name>\n'
            message += ('Shows recorded phone number for <contact_name>\n'
                        + '<contact_name> contains only one word')
        case 'help':
            message += f'{cmd_} <command>\n'
            message += ('Displays help info for <command>\n'
                        + 'List of available commands: hello, add,'
                        + ' change, phone, show, exit, help, find.\n')
        case _:
            message += '<command> [<parameters>]\n'
            message += ('Bot provides a storage for contacts.'
                        + ' Common operations such as adding, changing,\n'
                        + ' showing contact`s info etc are supported.\n'
                        + 'List of available commands: hello, add,'
                        + ' change, phone, show, exit, good bye,'
                        + ' close, help.\n'
                        + 'Type "help <command> for details')

    return status, message


def parse_input(sequence=''):
    """Main part of input parser"""
    command_pattern = r'^(hello|add|change|phone|show|exit|help|find)'
    command = ''
    args = ''
    if not sequence:
        return 'help', ''

    match_res = re.match(command_pattern, sequence, re.I)
    if match_res:
        command = match_res.group()
        args = sequence[match_res.span()[1]:].lstrip()
    else:
        command = 'help'
        args = ''

    return command, args


def read_from_file(path: Path):
    with path.open('rb') as fin:
        try:
            data = pickle.load(fin)
        except Exception as er:
            data = None
    return data

def main():
    global address_book
    print(HEADER)

    commands = {
        'hello': {'func': hello, 'args': False},
        'add': {'func': add, 'args': True},
        'change': {'func': change, 'args': True},
        'phone': {'func': phone, 'args': True},
        'show': {'func': show_all, 'args': True},
        'exit': {'func': exit_, 'args': False},
        'help': {'func': help, 'args': True},
        'find': {'func': find, 'args': True}
    }

    data_bin = Path('data.bin')
    if data_bin.exists():
        address_book = read_from_file(data_bin)
    if address_book is None:
        address_book = AddressBook()

    info_message = ('Addressbook is loaded '
                    + f'({len(address_book.data)} records)')\
        if len(address_book.data) > 0 \
        else 'Addressbook is created (0 records)'
    current_record = (f'Current record [{address_book.current_record_id}'
                      + f']: {str(address_book.get_current_record())}')\
        if len(address_book.data) > 0 \
        else 'There is no records yet in addressbook.'
    commands_line = 'Commands: ' + ' | '.join(commands.keys())

    while loop:
        print(info_message)
        print(current_record)
        print(commands_line)
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
        info_message = f'Address book got {len(address_book.data)} record(s).'
        current_record = (f'Current record [{address_book.current_record_id}'
                          + f']: {str(address_book.get_current_record())}') \
            if len(address_book.data) > 0 \
            else 'There is no records yet in addressbook.'


if __name__ == "__main__":
    main()
