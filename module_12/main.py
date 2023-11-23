import pickle
import re
from pathlib import Path
from AddressBook import AddressBook, Record, Birthday, Name, Phone
from messages import helpmsg, errormsg

HEADER = r"""
  <*********************************************************>
||  _   _       _      _____            _   ____        _    ||
|| | \ | |     | |    / ____|          | | |  _ \      | |   ||
|| |  \| | ___ | |_  | |     ___   ___ | | | |_) | ___ | |_  ||
|| | . ` |/ _ \| __| | |    / _ \ / _ \| | |  _ < / _ \| __| ||
|| | |\  | (_) | |_  | |___| (_) | (_) | | | |_) | (_) | |_  ||
|| |_| \_|\___/ \__|  \_____\___/ \___/|_| |____/ \___/ \__| ||
||                                                           ||
||                  by DmytroT, 2023                         ||
  <*********************************************************>
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
        except Exception as exception:
            handled = False
            for err, msg in errormsg.items():
                if err in str(exception.args):
                    error += msg
                    handled = True
            if not handled:
                error += (f'Unhandled {exception.__repr__()} raised in'
                          + f' {handler.__name__}.\n'
                          + f' arguments: {args}\n')

            error += (f'Type "help {handler.__name__}"'
                      + ' for detailed info')
        finally:
            return_values = return_values if not error \
                else ('Error', error)
        return return_values

    return inner

#
# CUTTED
#

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
        record = address_book.find(names[0].capitalize())
        if not record:
            address_book.add_record(Record(names[0].capitalize()))
            record = address_book.find(names[0].capitalize())
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
def change(sequence=''):
    """Changes recorded info current or given record"""
    status = 'OK'
    message = ''

    names, phones, bdays = tokenize_args(sequence)

    if len(names) <= 1:
        record = address_book.get_current_record()
        if len(names) == 1:
            record.name = Name(names[0].capitalize())
    elif len(names) >= 2:
        record = address_book.find(names[0].capitalize())
        if record is None:
            raise KeyError('!contact_exists')
        record.name = Name(names[1].capitalize())
        if len(names) > 2:
            message += ('Warning:\n\tOnly 2 names are'
                        + ' taken into account.\n')

    if len(phones) > 0:
        if len(phones) == 1:
            if len(record.phones) == 1:
                record.edit_phone(record.phones[0], Phone(phones[0]))
            else:
                raise ValueError('not_enough_phones')
        else:
            pairs = []
            for ind in range(0, len(phones), 2):
                pairs.append(phones[ind: ind+2])
            for pair in pairs:
                if len(pair) == 2:
                    record.edit_phone(pair[0], pair[1])
                else:
                    raise ValueError('not_enough_phones')

    if len(bdays) > 0:
        if len(bdays) >= 1:
            if record.birthday is None:
                message += (f'Warning: Record {record.name} has'
                            + ' no birthday set.'
                            + ' Use <add> command instead.\n')
            else:
                record.birthday = Birthday(bdays[0])
            if len(bdays) > 1:
                message += 'Warning:\n\tOnly 1 birthday is used.'

    return status, message


@input_error  # IndexError - empty
def show(sequence=''):
    """Displays recorded contacts"""
    status = 'OK'
    message = ''

    if not sequence:
        return status, 'Nothing to show.'

    # lim:N
    lim_ptrn = r'\blim:\d+\b'
    lim = re.findall(lim_ptrn, sequence)
    if len(lim) > 1: # no more than 1 limit per "page"
        raise ValueError('uncertain_show')
    # <ind>
    ind_ptrn = r'\b\d+\b'
    inds = re.findall(ind_ptrn, sequence)
    if len(inds) > 0 and len(lim) > 0: # limit and <ind> is nonsense
        raise ValueError('uncertain_show')
    #<start>-<end>
    range_ptrn = r'\b\d+-\d+\b'
    range_ = re.findall(range_ptrn, sequence)
    if len(lim) > 0 and len(range_) > 1: # only 1 range per limit
        raise ValueError('uncertain_show')
    # easiest way to filter invalid input
    if (len(lim) + len(inds) + len(range_)) == 0:
        raise ValueError('uncertain_show')
    header = (f'+{"=":=^5}+{"=":=^15}+{"=":=^15}+{"=":=^15}+\n'
              + f'|{"ID":^5}|{"NAME":^15}|{"PHONES":^15}'
              + '|{"BIRTHDAY":^15}|\n'
              + f'+{"-":-^5}+{"-":-^15}+{"-":-^15}+{"-":-^15}+\n')
    footer = f'+{"-":-^5}+{"-":-^15}+{"-":-^15}+{"-":-^15}+\n'
    # Show by ind
    rows = []
    for ind in inds:
        if int(ind) >= len(address_book.data):
            raise IndexError('index_out')
        rcrd = address_book.get_record_byid(int(ind))
        rows.append()



    if sequence != 'all':

    else:

    return status, message


@input_error
def find(sequence=''):
    """Finds record by given patterns"""
    status = 'OK'
    message = ''
    res_lst = []

    name_part = r'\b[a-z]{2,}\b'
    phone_part = r'\b\d{2,}\b'
    srch_name = [i for i in sequence.split()
                        if re.search(name_part, i)]
    srch_phon = [i for i in sequence.split()
                        if re.search(phone_part, i)]
    if len(sequence.split()) != len(srch_phon) + len(srch_name):
        message += 'Warning: Some invalid search pattern were removed.\n'
    if len(srch_name) == 0 and len(srch_phon) == 0:
        raise ValueError('bad_search_cond')

    for rcrd in address_book.data.values():

        row = {'name': '', 'id': None, 'phones': []}

        for token in srch_name:
            res = re.search(token, rcrd.name.value, re.I)
            if res:
                row['id'] = address_book.get_record_id(rcrd.name.value)
                # name - Waldemar
                # token - dem
                # name - Wal[dem]ar
                name = (f'{rcrd.name.value[:res.start()]}'
                        + f'[{token}]{rcrd.name.value[res.end():]}')
                row['name'] = name
                break

        for token in srch_phon:
            for phone in rcrd.phones:
                res = re.search(token, phone.value)
                if res:
                    if row['id'] is None:
                        row['name'] = rcrd.name.value
                        row['id'] = (address_book
                                     .get_record_id(rcrd.name.value))
                    else:
                        # phone - 123456
                        # token - 45
                        # phone - 123[45]6
                        phone_num = (f'{phone.value[:res.start()]}'
                                     + f'[{token}]{phone.value[res.end():]}')
                        row['phones'].append(phone_num)
                else:
                    # just for representation
                    row['phones'].append(phone.value)

        res_string = (f'Record ({row['id']}): {row['name']}, phones: '
                      + f'{', '.join(row['phones'])}')
        # got no [ == got no matches
        if '[' in res_string:
            res_lst.append(res_string)

    conditions = ', '.join(srch_name) + ' '
    conditions += ', '.join(srch_phon)
    if len(res_lst):
        message += f'{len(res_lst)} result(s) for {conditions}.\n'
        message += '\n'.join(res_lst)
    else:
        message += f'No results for {conditions}.\n'

    return status, message


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
    status = None

    message = 'Usage: '
    for cmd, msg in helpmsg.items():
        if cmd == command:
            message += msg

    if message == 'Usage: ':
        message += '<command> [<parameters>]\n'
        message += ('Bot provides a storage for contacts.'
                    + ' Common operations such as adding, changing,\n'
                    + 'showing contact`s info etc are supported.\n'
                    + 'List of available commands: hello, add,'
                    + ' change, show, exit, find, help.\n'
                    + 'Type "help <command> for details\n====')

    return status, message


def parse_input(sequence=''):
    """Main part of input parser"""
    command_pattern = r'^(hello|add|change|show|exit|help|find)'
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
        'show': {'func': show, 'args': True},
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
        sequence = input(">>> ").lstrip()
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
        info_message = (f'Address book`s got {len(address_book.data)}'
                        + ' record(s).')
        current_record = ('Current record ['
                          + f'{address_book.current_record_id}]: '
                          + f'{str(address_book.get_current_record())}')\
            if len(address_book.data) > 0 \
            else 'There is no records yet in addressbook.'


if __name__ == "__main__":
    main()
