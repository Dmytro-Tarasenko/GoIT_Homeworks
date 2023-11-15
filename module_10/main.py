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
        self.value = number.strip()

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
        self.phones_repr = []
        self.value = {self.name.value: self.phones_repr}

    def add_phone(self, phone):
        phone_ = Phone(phone)
        self.phones.append(phone_)
        self.phones_repr.append(phone_.value)

    def remove_phone(self, phone):
        _phone = Phone(phone)
        idx = self.phones_repr.index(_phone.value)
        self.phones.pop(idx)
        self.phones_repr.pop(idx)

    def edit_phone(self, old_phone, new_phone):
        _old = Phone(old_phone)
        _new = Phone(new_phone)
        idx = self.phones_repr.index(_old.value)
        self.phones[idx].replace(_new.value)
        self.phones_repr[idx] = _new.value

    def find_phone(self, phone):
        phone_ = Phone(phone)
        if phone_.value in self.phones_repr:
            ind = self.phones_repr.index(phone_.value)
            return self.phones[ind]
        return None

    def __str__(self):
        ret = (f"Contact name: {self.name.value},"
               + " phones: {'; '.join(p.value for p in self.phones)}")
        return ret


class AddressBook(UserDict):

    def add_record(self, record):
        self.data.update({record.name.value: record})

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
