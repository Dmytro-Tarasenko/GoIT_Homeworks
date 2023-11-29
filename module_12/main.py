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

address_book = AddressBook()
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
            if len(phones) == 0 and len(bdays) == 0:
                return status, message
        if len(names) > 1:
            message += ('Warning: Only 1 name can be in add command.'
                        + ' To edit name use <change> command instead.\n')
        if len(names) == 1 and len(phones) == 0 and len(bdays) == 0:
            message += ('There is nothing to add to existing'
                        + f' {record.name.value} contact.\n'
                        + 'Try another name or add some information.')
            return 'Warning', message
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
        old_name = record.name.value
        if len(names) == 1:
            new_name = names[0].capitalize()
            record.name = Name(new_name)
            address_book.data[new_name] = address_book.data.pop(old_name)
            address_book.current_record_id = len(address_book.data) - 1
    elif len(names) >= 2:
        record = address_book.find(names[0].capitalize())
        old_name = record.name.value
        if record is None:
            raise KeyError('!contact_exists')
        new_name = names[1].capitalize()
        record.name = Name(new_name)
        address_book.data[new_name] = address_book.data.pop(old_name)
        address_book.current_record_id = len(address_book.data) - 1
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
    start_len = len(sequence)

    # lim:N
    lim_ptrn = r'\blim:\d+\b'
    lim = re.findall(lim_ptrn, sequence)
    sequence = re.sub(lim_ptrn, '', sequence)
    if len(lim) > 1:  # no more than 1 limit
        raise ValueError('uncertain_show')

    # <start>-<end>
    range_ptrn = r'\b\d+-\d+\b'
    range_ = re.findall(range_ptrn, sequence)
    if len(lim) > 0 and len(range_) > 1:  # only 1 range per limit
        raise ValueError('uncertain_show')
    # ranges need to be poped to avoid index conflict
    sequence = re.sub(range_ptrn, '', sequence)

    # <ind>
    ind_ptrn = r'\b\d+\b'
    inds = re.findall(ind_ptrn, sequence)
    if len(inds) > 0 and len(lim) > 0:  # limit and <ind> is nonsense
        raise ValueError('uncertain_show')

    # easiest way to filter invalid input
    if (len(lim) + len(inds) + len(range_)) == 0\
            and len(sequence) > 0:
        raise ValueError('uncertain_show')

    # no params = show from 0 to len()
    # only lim is set: lim + range_ 0 to len()
    if start_len == 0 or (len(lim) == 1 and len(range_) == 0):
        range_ = [f'0-{len(address_book.data)}']

    header = (f'+{"=":=^5}+{"=":=^15}+{"=":=^15}+'
              + f'{"=":=^15}+{"=":=^12}+\n'
              + f'|{"ID":^5}|{"NAME":^15}|{"PHONES":^15}'
              + f'|{"BIRTHDAY":^15}|{"DAYS TO BD":^12}|\n'
              + f'+{"=":=^5}+{"=":=^15}+{"=":=^15}+'
              + f'{"=":=^15}+{"=":=^12}+\n')
    footer = (f'+{"-":-^5}+{"-":-^15}+{"-":-^15}'
              + f'+{"-":-^15}+{"-":-^12}+\n')

    # Returns row from record:
    # id 23 Name Vasyl, phones 1234567, 2345678, 3456789,
    # bday 2000-01-01, days to BD 45
    #    5        15          15          15            12
    # | 23  |   Vasyl   |  1234567  |  2000-01-01   |   45    |
    # |     |           |  2345678  |               |         |
    # |     |           |  3456789  |               |         |
    # +-----+-----------+-----------+---------------+---------+
    def make_row(record: Record, ind=None):
        name = record.name.value

        if ind is None:
            ind = address_book.get_record_id(name)

        if record.birthday is None:
            bday = days2bd = '-'
        else:
            bday = record.birthday.value
            days2bd = record.days_to_birthday()
        if len(record.phones) == 0:
            phone_0 = '-'
        elif len(record.phones) >= 1:
            phone_0 = record.phones[0].value
        #    5        15          15          15            12
        row = (f'|{ind:^5}|{name:<15}|{phone_0:^15}|'
               + f'{str(bday):^15}|{days2bd:^12}|\n')
        for i in range(1, len(record.phones)):
            row += (f'|{" ":^5}|{"":^15}|{record.phones[i].value:^15}'
                    + f'|{" ":^15}|{" ":12}|\n')
        row += footer
        return row

    buffer = [int(i) for i in inds]
    for chunk in range_:
        start = int(chunk.split('-')[0])
        end = int(chunk.split('-')[1])
        end = end if end <= len(address_book.data) \
            else len(address_book.data)
        buffer.extend(range(start, end))
    inds = [None for _ in range(len(address_book.data))]
    for ind_ in buffer:
        inds[ind_] = ind_

    # Show by ind
    rows = []

    # lim[0] = 'lim:3' -> lim = 3
    lim = int(lim[0].split(':')[1]) if len(lim) == 1 else 0

    # show by range
    # decorator???
    if lim == 0:
        for ind in inds:
            if ind is not None:
                rcrd = address_book.get_record_byid(ind)
                rows.append(make_row(rcrd, ind))
    else:
        start = int(range_[0].split('-')[0])
        end = int(range_[0].split('-')[1])
        for chunk in address_book.iterator(start, end, lim):
            out = header
            for rcrd in chunk:
                out += make_row(rcrd)
            print(out)
            _ = input('Enter to proceed, "c" for cancel:')
            if _.lower() == 'c':
                message = 'Canceled by user.'
                break
        return status, message

    if len(rows) > 0:
        message += header
        for row in rows:
            message += row

    return status, message


@input_error
def find(sequence=''):
    """Finds record by given patterns"""
    status = 'OK'
    message = ''
    res_lst = []

    sequence = sequence.lower()
    token_pattern = r'\b[a-z]{2,}\b|\b\d{2,}\b'

    # перелік усіх валідних умов пошуку
    token_list = re.findall(token_pattern, sequence)
    # єдиний пошуковий паттерн
    search_pattern = rf'{"|".join(token_list)}'

    for ind, name in enumerate(address_book.data):
        # search_sting = 'Name::phone1#phone2#phone3::Birthday
        search_string = (address_book
                         .find(name)
                         .as_search_string().lower())
        res_string = re.sub(search_pattern,
                            lambda x: f'[{x.group()}]',
                            search_string)
        # res_string Id::N[ame]::phone1#phon[e2]#phone3::Birthday
        res_string = f'{ind}::' + res_string
        if '[' in res_string:
            res_lst.append(res_string)

    if len(res_lst) == 0:
        message += ('There were no results for'
                    + f' {search_pattern.replace("|", " | ")}.')
        return status, message

    header = (f'+{"=":=^5}+{"=":=^17}+{"=":=^17}+{"=":=^12}+\n'
              + f'|{"ID":^5}|{"NAME":^17}|'
              + f'{"PHONES":^17}|{"BIRTHDAY":^12}|\n')
    footer = f'+{"-":-^5}+{"-":-^17}+{"-":-^17}+{"-":-^12}+\n'

    rows = ''
    # row Id::N[ame]::phone1#phon[e2]#phone3::Birthday
    # | 23  |  V[asy]l  |  1234567  |  2000-01-01   |
    # |     |           | 23[4567]8 |               |
    # |     |           |  3456789  |               |
    # +-----+-----------+-----------+---------------+
    for row in res_lst:
        id_, name_, phones_, bday_ = row.split('::')
        phones_ = phones_.split('#')
        phone0 = '-' if len(phones_) == 0 else phones_[0]
        # bday_ = bday_ if bday_ != 'none' else '-'
        rows += (f'|{id_:^5}|{name_.capitalize():^17}|'
                 + f'{phone0:^17}|{bday_:^12}|\n')
        for phone in phones_[1:]:
            rows += f'|{"":<5}|{"":<17}|{phone:^17}|{"":^12}|\n'
        rows += footer

    message += (f'There are {len(res_lst)} results'
                + f' for {search_pattern.replace("|", " | ")}:\n')
    message += header + footer + rows

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
    elif address_book.find(sequence.split()[0].capitalize()):
        command = 'show'
        rcrd = address_book.find(sequence.split()[0].capitalize())
        ind = address_book.get_record_id(rcrd.name.value)
        args = str(ind)
    else:
        command = 'help'
        args = ''

    return command, args


def read_from_file(path: Path):
    with path.open('rb') as fin:
        try:
            data = pickle.load(fin)
        except Exception:
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
        if len(address_book.data) > 0\
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
