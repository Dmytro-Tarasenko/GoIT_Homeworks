from collections import UserDict
import re


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, number):
        if not self.is_valid(number):
            raise ValueError('Invalid number')
        super().__init__(number.strip())

    def is_valid(self, number):
        _valid_phone = r'^\d{10}$'
        if not re.match(_valid_phone, number.strip()):
            return False
        return True

    def replace(self, number):
        if not self.is_valid(number):
            raise ValueError('Invalid number')
        self.value = number.strip()


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
#       self.value = {self.name.value: self.phones_repr}

    # number буде передаватись через Phone.value вже після валідації
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
        _old = Phone(old_phone)
        _new = Phone(new_phone)
        idx = self.__index_of(_old.value)
        if idx is None:
            raise ValueError('Number not found')
        self.phones[idx].replace(_new.value)

    def find_phone(self, phone):
        _phone = Phone(phone)
        idx = self.__index_of(_phone.value)
        if idx is not None:
            return self.phones[idx]

    def __str__(self):
        ret = (f"Contact name: {self.name.value},"
               + f" phones: {'; '.join(p.value for p in self.phones)}")
        return ret


class AddressBook(UserDict):

    def add_record(self, record):
        self.data.update({record.name.value: record})

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
