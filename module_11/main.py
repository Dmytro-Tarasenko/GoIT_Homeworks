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
        _valid_name = r'^\w(2,)$'
        name = name.strip()
        if not re.match(_valid_name, name):
            raise ValueError('Invalid name')
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
        number = (number.strip()
                  .replace('+', '')
                  .replace('(', '')
                  .replace(')', '')
                  .replace('-', '')
                  .replace(' ', ''))
        _valid_phone = r'^\d{10}$'
        if not re.match(_valid_phone, number):
            raise ValueError('Invalid number')
        self.__value = number

    def replace(self, number):
        self.value = number


class Birthday(Field):
    def __init__(self, bdate):
        self.__value = None
        self.value = bdate

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, bdate):
        bdate = (bdate.strip()
                 .replace(' ', '')
                 .replace('-', '')
                 .replace('.', ''))
        _valid_date = r'^\d{8}$'
        match = re.match(_valid_date, bdate)
        bdate = date.fromisoformat(bdate)
        if not match or bdate >= date.today():
            raise ValueError('Invalid date')
        self.__value = bdate


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if birthday else None
        self.phones = []

    def __index_of(self, number):
        numbers = [self.phones[i].value for i in range(len(self.phones))]
        if number in numbers:
            return numbers.index(number)

    def add_phone(self, phone):
        phone_ = Phone(phone)
        self.phones.append(phone_)

    def remove_phone(self, phone):
        _phone = Phone(phone)
        idx = self.__index_of(_phone.value)
        if idx is None:
            raise IndexError('Number not found')
        self.phones.pop(idx)

    def edit_phone(self, old_phone, new_phone):
        idx = self.__index_of(old_phone)
        if idx is None:
            raise ValueError('Number not found')
        self.phones[idx].replace(new_phone)

    def find_phone(self, phone):
        _phone = Phone(phone)
        idx = self.__index_of(_phone.value)
        if idx is not None:
            return self.phones[idx]

    def days_to_birthday(self):
        bday_ = self.birthday.value
        if bday_ is None:
            return None
        today_ = date.today()
        this_bday = date(today_.year,
                         bday_.month,
                         bday_.day)
        if (this_bday - today_).days < 0:
            this_bday = date(today_.year + 1,
                             bday_.month,
                             bday_.day)
        return (this_bday - today_).days

    def __str__(self):
        ret = (f'Contact name: {self.name.value},'
               + f' phones: {"; ".join(p.value for p in self.phones)}'
               + f' birthday: {self.birthday}')
        return ret


class AddressBook(UserDict):

    def add_record(self, record):
        self.data.update({record.name.value: record})

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)


if __name__ == '__main__':
    bday = Birthday('20221116')
    print(bday)
