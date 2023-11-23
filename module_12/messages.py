helpmsg = {
    'add': ('add <contact_name> [<phone_numbers>,'
            + '<birthday>]\n'
            + 'Adds  contact with name <contact_name>,'
            + 'phone number <phone_number>  to contact base.\n'
            + '<contact_name> contains only one word and'
            + ' <phone_number> - only digits,'
            + ' phones with 6, 7, 10 or 12 digits are acceptable;'
            + ' <birthday> should be in format yyyy-mm-dd or dd-mm-yyyy'
            + 'common separator are allowed [.,/\\].\n'
            + 'If no <contact_name> is provided'
            + ' all data goes to current record'),
    'exit': 'exit\n Prints farewell message, saves data and exits',
    'show': ('show [lim:N, <ind>, <ind_start>-<ind_end>]'
             + 'Shows recorded contacts in addressbook.\n'
             + 'lim:N - set the limitation of N records to display'
             + ' at once.\n Press "Enter" to proceed "C"  to abort.'
             + '<ind> - index of record in addressbook to display.\n'
             + '<ind_start>-<ind_end> - display records'
             + ' from <ind_start> to <ind_end>.'),
    'hello': 'hello\n Shows greeting message.',
    'change': ('change [<old_name>] <new_name> [<old_phone> <new_phone>]'
               + '[<new_birthday>]\n'
               + 'Changes data of record <old_name> to provided new ones.\n'
               + '<old_name> - is the name for record which data needs to'
               + ' be changed. If not specified current record is used.\n'
               + '<old_phone> <new_phone> - pairs of numbers to change.\n'
               + 'It`s possible to omit <old_phone> if there is only one'
               + ' number in record.\n'
               + '<new_birthday> - new date of birthday.'),
    'help': ('help [<command>]\n')
}

errormsg = {
    'no_contact_number': ('Provide valid contact name\\'
                          + 'phone number to proceed\n'),
    'future_date': ('Future is not come yet.'
                    + ' Try another date\n'),
    'no_contact': 'Provide contact name to proceed\n',
    'no_number': 'Provide phone number to proceed\n',
    'wrong_number': 'Provided phone number is not valid\n',
    'wrong_contact': 'Provided contact name is not valid\n',
    'contact_or_phone_mis': ('Both contact name and phone number'
                             + ' are needed to proceed\n'),
    'empty_list': ('Nothing to show -'
                   + ' contacts base got no records.\n'
                   + 'Try to fill it first.'),
    'mentor_detected': ('Really!? Doing stuff with no records!?\n'
                        + 'Ulyana, are you here?\n'
                        + 'If yes, THANKS ALOT!'),
    'contact_exists': ('Contact`ve been already recorded.'
                       + ' Try another name.'),
    'phone_exists': ('Phone`ve been already recorded.'
                     + ' Try another one.'),
    '!contact_exists': 'Contact does not exist. Try another name.',
    'params_absense': 'No needed parameter(s) was(were) provided.',
    'not_enough_phones': 'Unable to determine phone to change.',
    'bad_search_cond': 'Bad search condition were provided.'
}
