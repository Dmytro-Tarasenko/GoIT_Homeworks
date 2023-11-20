from AddressBook import AddressBook, Name, Phone, Birthday, Record
from datetime import date
import random

print('Name tests.')
print('Name consists of [\\w \\.,]. Whitespaces are stripped:\n')

print('1. For "  Vasyl 3,jr. " - Vasyl 3,jr.')
name = Name("  Vasyl 3,jr. ")
print(name)
print('____________\n')

print('2. For "Vasyl" - Vasyl')
name = Name("Vasyl")
print(name)
print('____________\n')

print('3. For "Vas-yl" - ValueError raised: Invalid name: None')
name2 = Name("Vas-yl")
print(name2)
print('"Vasyl!" - ValueError raised: Invalid name: None')
name2 = Name("Vasyl!")
print(name2)
print('=============\n')

print('Phone tests.')
print('Phone consists of 6, 7, 10 or 12 numbers. "+- ()" are stripped:\n')

print('1. For 12345678 - 1234567')
phone = Phone("1234567")
print(phone)
print('____________\n')

print('2. For 123 45 6-7 - 1234567')
phone = Phone("123 45 6-7")
print(phone)
print('____________\n')

print('3. For +38 (067) 123-34 67 - 380671234567')
phone = Phone("+38 (067) 123-34 67")
print(phone)
print('____________\n')

print('4. For 123 45 6-789 - ValueError raised: Invalid phone number: None')
phone = Phone("123 45 6-789")
print(phone)
print('____________\n')

print('5. For phone = Phone(None) - ValueError raised: None is not a valid number: None')
phone = Phone(None)
print(phone)
print('==============\n')

print('Birthday tests.')
print('Date can be yyyy-mm-dd or dd-mm-yyyy, sep is one of [,.- \\/]:\n')

print('1. For 1234.01/23 - 1234-01-23')
bday = Birthday("1234.01/23")
print(bday)
print('____________\n')

print('2. For 12\\11 2010 - 2010-11-12')
bday = Birthday("12\\11 2010")
print(bday)
print('____________\n')

print('3. For 2042-01-12 - ValueError raised: Future is not yet come: None')
bday = Birthday("2042-01-12")
print(bday)
print('____________\n')

print('4. For 2010-13-25 - ValueError raised: (month must be in 1..12,): None')
bday = Birthday('2010-13-25')
print(bday)
print('==============\n')

print('Record tests.')

print("Record('John') - ok")
john_rec = Record('John')
print("add_phone('1234567890') - ok")
john_rec.add_phone('1234567890')
print("add_phone('+38(067)321-54-76') - ok")
john_rec.add_phone('+38(067)321-54-76')
print("add_phone('+38 (067) 321 54 76') - KeyError is raised: Phone is already recorded")
john_rec.add_phone('+38 (067) 321 54 76')
print("find_phone('+38(067)321-54-76') - 380673215476")
print(john_rec.find_phone('+38(067)321-54-76'))
print("find_phone('+38(067)321-54-77') - ValueError raised: number not found: None")
print(john_rec.find_phone('+38(067)321-54-77'))
print(john_rec)
print('==============\n')

print('AddressBook Tests')
book = AddressBook()
# Створення запису для John
print('Record("John") - ok')
john_record = Record("John")
print("birthday = '199810-25' - ValueError raised: Invalid date")
john_record.birthday = '199810-25'
print('add_phone("(1)2-34567890") - ok')
john_record.add_phone("(1)2-34567890")
print('add_phone("5555555555") - ok')
john_record.add_phone("5555555555")
print("john_record.days_to_birthday() - ValueError: Record John got no birthday set.")
print(john_record.days_to_birthday())

# Додавання запису John до адресної книги
print('add_record(john_record) -ok')
book.add_record(john_record)

# Створення та додавання нового запису для Jane
print('Jane record block in book + days_to_birthday - OK')
jane_record = Record("Jane")
jane_record.birthday = Birthday('1980-01-23')
jane_record.add_phone("9876543210")
print(jane_record.days_to_birthday())
book.add_record(jane_record)
print('Jane record in book:')
print(book.data['Jane'])

# Виведення всіх записів у книзі
print('\nAll records in book:')
for name, record in book.data.items():
    print(record)

print('\nFind record John in book:')
# Знаходження та редагування телефону для John
john = book.find("John")
print(john)
print('\njohn.edit_phone("1234567890", "1112223333")')
john.edit_phone("1234567890", "1112223333")
print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

# Пошук конкретного телефону у записі John
print('john.find_phone("5555555555")')
found_phone = john.find_phone("5555555555")
print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

# Видалення запису Jane
print('\nbook.delete("Jane")')
book.delete("Jane")
print(book)


names = ['Alex', 'Bob', 'Andre', 'Ann', 'Isabelle']
pag_lim = 3
pgs = 2
num_records = pag_lim * pgs + random.randrange(0, pag_lim)

print(f'Generate random {num_records} records for test_book:')
test_book = AddressBook()
for i in range(num_records):
    cnt_name = f'{names[random.randrange(0, len(names))]}{(i // pag_lim) + 1}{(i % pag_lim) + 1}'
    rec_ = Record(cnt_name)
    for _ in range(1, 5):
        if random.randrange(33) % 2:
            rec_.add_phone(str(random.randrange(1111111111, 9999999999)))
    rec_.birthday = str(date(random.randrange(1970, 2010),
                             random.randrange(1, 12),
                             random.randrange(1, 28)))
    test_book.add_record(rec_)
print(f'test_book got {len(test_book)} records\n')

import pickle

with open('data.bin', 'wb') as fout:
    data  = pickle.dump(test_book)

pgs = pgs+1 if num_records % pag_lim else pgs
print(f'With {pag_lim} records per page there will be {pgs} page(s)')
page_num = 1
for page in test_book.iterator(pag_lim):
    print(f'\nPage #{page_num}')
    for _ in page:
        print(_, end=' days_to_bd: ')
        print(_.days_to_birthday())
    page_num += 1
