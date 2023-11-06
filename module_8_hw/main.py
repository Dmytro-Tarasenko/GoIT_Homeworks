from datetime import date, datetime


def get_birthdays_per_week(users):

    if len(users) == 0:
        return {}

    users_bd = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': []
    }
    # Реалізуйте тут домашнє завдання
    for user in users:
        bd_to_be = datetime(date.today().year, user['birthday'].month, user['birthday'].day).date()
        cur_date = date.today()
        delta = bd_to_be - cur_date

        if 0 <= delta.days <= 6:
            day_of_week = datetime.strftime(bd_to_be, '%A')
            day_of_week = day_of_week if day_of_week in users_bd.keys() else 'Monday'
            users_bd[day_of_week].append(user['name'].split(' ')[0])

        if -365 <= delta.days < -358:
            bd_to_be = datetime(date.today().year+1, user['birthday'].month, user['birthday'].day).date()
            delta = bd_to_be - cur_date
            if 0 <= delta.days <= 6:
                day_of_week = datetime.strftime(bd_to_be, '%A')
                day_of_week = day_of_week if day_of_week in users_bd.keys() else 'Monday'
                users_bd[day_of_week].append(user['name'].split(' ')[0])

    users = {day: user_list for day, user_list in users_bd.items() if len(user_list) > 0}

    return users


if __name__ == "__main__":
    users = [
        {"name": "Jan Koum", "birthday": datetime(1976, 1, 1).date()},
    ]

    result = get_birthdays_per_week(users)
    print(result)
    # Виводимо результат
    for day_name, names in result.items():
        print(f"{day_name}: {', '.join(names)}")
