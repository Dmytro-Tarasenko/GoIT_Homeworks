import datetime
from collections import UserDict
import re
from datetime import date


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        self.__value = None
        self.value = name

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, name):
        if isinstance(name, str):
            name = name.strip()
        _name_pattern = r'^[\w_\.\,\-]+$'
        if not re.match(_name_pattern, name):
            print('ValueError raised: Invalid name')
            return
        self.__value = name


class Phone(Field):
    def __init__(self, number):
        self.__value = None
        self.value = number

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, number):
        if number is None:
            print('ValueError raised: None is not a valid number')
            return
        if isinstance(number, str):
            number = (number.strip()
                      .replace('(', '')
                      .replace(')', '')
                      .replace('+', '')
                      .replace('-', '')
                      .replace(' ', ''))
            _number_pattern = r'^(\d{12}|\d{10}|\d{7}|\d{6})$'
            if not re.match(_number_pattern, number):
                print('ValueError raised: Invalid phone number')
                return
            self.__value = number
        elif isinstance(number, Phone):
            if number.value is not None:
                self.__value = number.value
            else:
                print('ValueError raised: None is not a valid number')


class Birthday(Field):
    def __init__(self, bday):
        self.__value = None
        self.value = bday

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, bday):
        if (isinstance(bday, datetime.date) or
                isinstance(bday, Birthday)):
            _bday = bday if isinstance(bday, datetime.date)\
                else bday.value
            if _bday <= date.today():
                self.__value = _bday
            else:
                print('ValueError raised: Future is not yet come')
                self.__value = None
        elif isinstance(bday, str):
            bday = (bday.strip()
                    .replace(' ', '-')
                    .replace('.', '-')
                    .replace(',', '-')
                    .replace('/', '-')
                    .replace('\\', '-'))
            # date yyyy-mm-dd | dd-mm-yyyy
            _bday_pattern = r'^(\d{2}-\d{2}-\d{4})|(\d{4}-\d{2}-\d{2})$'
            if not re.match(_bday_pattern, bday):
                raise ValueError('invalid_date')
            # what is 1st in bday year|day
            if len(bday.split('-')[0]) == 2:
                bday = '-'.join(bday.split('-')[::-1])
            try:
                res = date.fromisoformat(bday)
                if res > date.today():
                    self.__value = None
                    raise ValueError('future_date')
                else:
                    self.__value = res
            except ValueError as ve:
                err = '|'.join(ve.args)
                raise ValueError(err)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.__birthday = None
        self.birthday = None

    @property
    def birthday(self):
        return self.__birthday

    @birthday.setter
    def birthday(self, bday=None):
        if bday is None:
            return None
        self.__birthday = Birthday(bday)

    def __phone_values(self):
        for phone in self.phones:
            yield phone.value

    def prep_phone(self, phone):
        return (phone.strip()
                .replace('(', '')
                .replace(')', '')
                .replace('+', '')
                .replace('-', '')
                .replace(' ', ''))

    def is_valid_phone(self, phone):
        if isinstance(phone, Phone) and phone.value is not None:
            return True
        if isinstance(phone, str):
            phone = self.prep_phone(phone)
            _number_pattern = r'^(\d{12}|\d{10}|\d{7}|\d{6})$'
            if not re.match(_number_pattern, phone):
                return False
            return True

    def __str__(self):
        ret = (f'contact name - {self.name.value},'
               + f' phones: {", ".join(p.value for p in self.phones)};'
               + f' birthday: {self.birthday}')
        return ret

    def add_phone(self, phone):
        if not self.is_valid_phone(phone):
            raise ValueError('wrong_number')
        if (isinstance(phone, Phone) and
                self._get_phone_ind(phone.value) is None):
            self.phones.append(phone)
        elif self._get_phone_ind(self.prep_phone(phone)) is None:
            self.phones.append(Phone(phone))
        else:
            raise KeyError('phone_exists')

    def _get_phone_ind(self, phone_str):
        phone_lst = list(self.__phone_values())
        if phone_str in phone_lst:
            return phone_lst.index(phone_str)
        return None

    def _do_phone(self, phone, command: str, new_phone=None):
        if not self.is_valid_phone(phone):
            raise ValueError('wrong_number')
        if isinstance(phone, Phone):
            _search = phone.value
        else:
            _search = self.prep_phone(phone)
        ind = self._get_phone_ind(_search)
        if ind is not None:
            match command:
                case 'find':
                    return self.phones[ind]
                case 'remove':
                    self.phones.pop(ind)
                    return
                case 'edit':
                    if new_phone is None:
                        raise ValueError('new_phone_needed')
                    if not self.is_valid_phone(new_phone):
                        raise ValueError('wrong_number')
                    if isinstance(new_phone, Phone):
                        _sub = new_phone.value
                    else:
                        _sub = self.prep_phone(new_phone)
                    self.phones[ind].value = _sub
                    return
        raise ValueError('phone_not_found')

    def find_phone(self, phone):
        return self._do_phone(phone, 'find')

    def remove_phone(self, phone):
        self._do_phone(phone, 'remove')

    def edit_phone(self, old_phone, new_phone):
        self._do_phone(old_phone, 'edit', new_phone)

    def days_to_birthday(self):
        if self.birthday.value is None:
            raise ValueError(f'{self.name.value}'
                  + ' got no birthday set.')
        cur_bday = date(date.today().year,
                        self.birthday.value.month,
                        self.birthday.value.day)
        if (cur_bday - date.today()).days < 0:
            cur_bday = date(cur_bday.year+1,
                            cur_bday.month,
                            cur_bday.day)
        return (cur_bday - date.today()).days

class AddressBook(UserDict):
    def __init__(self):
        self.current_record_id = 0
        super().__init__()

    def get_record_id(self, name):
        if len(self.data) == 0:
            raise IndexError('mentor_detected')
        if name in self.data.keys():
            return list(self.data.keys()).index(name)

    def get_current_record(self):
        if len(self.data) == 0:
            raise IndexError('mentor_detected')
        record_key = list(self.data.keys())[self.current_record_id]
        return self.data[record_key]

    def get_record_byid(self, id_=0):
        record_key = list(self.data.keys())[id_]\
            if id_ < len(self.data)\
            else len(self.data) - 1
        return self.data[record_key]

    def add_record(self, record):
        self.data.update({record.name.value: record})
        name = record.name.value
        self.current_record_id = list(self.data.keys()).index(name)

    def find(self, name):
        if name in self.data.keys():
            self.current_record_id = list(self.data.keys()).index(name)
            return self.data.get(name)
        return None

    def delete(self, name):
        if name in self.data:
            id_ = list(self.data.keys()).index(name)
            self.current_record_id = id_ - 1\
                if id_ > 0 else 0
            self.data.pop(name)

    def iterator(self, pg_lim):
        for ind in range(0, len(self.data), pg_lim):
            self.current_record_id = ind + pg_lim\
                if (ind + pg_lim) < len(self.data)\
                else len(self.data) - 1
            yield list(self.data.values())[ind:ind+pg_lim]
