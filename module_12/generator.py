"""Generates test AddressBook
There will be pag_lim * pgs + random.randrange(0, pag_lim)
records in AddressBook
"""
import random
import pickle
from AddressBook import *

names = ['Alex', 'Bob', 'Andre', 'Ann', 'Isabelle', 'Louis', 'Vasyl',
         'Nadiya', 'Petro', 'Pedro', 'Ann-Marie', 'Alexandra', 'Kasandra',
         'Mark', 'Olaf']
pag_lim = 4
pgs = 4
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

with open('data.bin', 'wb') as fout:
    pickle.dump(test_book, fout)