from collections import UserDict
import re

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, phone):
        _valid_phone = r'^\d{10}$'
        if not re.match(_valid_phone, phone.strip()):
            raise ValueError('Phone number is invalid!')
        self.value = phone.strip()


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.value = {self.name.value: self.phones}

    def add_phone(self, phone):
        phone_ = Phone(phone)
        self.phones.append(phone_.value)

    def remove_phone(self, phone):
        phone_ = Phone(phone)
        self.phones.pop(self.phones.index(phone_.value))


    def edit_phone(self, old_phone, new_phone):
        old_phone_ = Phone(old_phone)
        new_phone_ = Phone(new_phone)
        ind = self.phones.index(old_phone_.value)
        self.phones[ind] = new_phone_.value

    def find_phone(self, phone):
        phone_ = Phone(phone)
        self.phones.index(phone_.value)
        return phone_.value

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):

    def add_record(self, record):
        self.data.update(record.value)

    def find(self, name):
        pass

    def delete(self, name):
        pass


book = AddressBook()

john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")

book.add_record(john_record)

jane_record = Record("Jane")
jane_record.add_phone("9876543210")
book.add_record(jane_record)


for name, record in book.data.items():
    print(record)

john = book.find("John")
john.edit_phone("1234567890", "1112223333")

print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

found_phone = john.find_phone("5555555555")
print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

# Видалення запису Jane
book.delete("Jane")