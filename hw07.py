from collections import UserDict
from datetime import datetime, timedelta

# Базовий клас для полів запису
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для зберігання імені контакту. Обов'язкове поле.
class Name(Field):
    pass

# Клас для зберігання номера телефону.
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

# Клас для зберігання дати народження.
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Клас для зберігання інформації про контакт включаючи ім'я та список телефонів.
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Додавання телефону до запису
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    # Видалення телефону з запису
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    # Редагування телефону в запису
    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    # Додавання дати народження до запису
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    # Обчислення днів до наступного дня народження
    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = self.birthday.value.replace(year=today.year + 1)
        return (next_birthday - today).days

    # Перетворення запису на рядок для зручного виведення
    def __str__(self):
        phones = ', '.join(phone.value for phone in self.phones)
        birthday = self.birthday.value.strftime('%d.%m.%Y') if self.birthday else "Not set"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"

# Клас для зберігання та управління записами
class AddressBook(UserDict):
    # Додавання запису до адресної книги
    def add_record(self, record):
        self.data[record.name.value] = record

    # Пошук запису за ім'ям
    def find(self, name):
        return self.data.get(name)

    # Видалення запису за ім'ям
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    # Повертає список контактів, яких потрібно привітати по днях на наступному тижні
    def get_upcoming_birthdays(self):
        today = datetime.now()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                days_to_birthday = record.days_to_birthday()
                if days_to_birthday is not None and 0 <= days_to_birthday <= 7:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

# Декоратор для обробки помилок вводу
def input_error(func):
    def wrapper(args, book):
        try:
            return func(args, book)
        except (IndexError, ValueError) as e:
            return str(e)
    return wrapper

# Функція для додавання контакту
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

# Функція для зміни телефону контакту
@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated."
    return "Contact not found."

# Функція для виведення телефону контакту
@input_error
def phone_contact(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return f"{name}'s phone numbers: {', '.join(phone.value for phone in record.phones)}"
    return "Contact not found."

# Функція для виведення всіх контактів
def show_all_contacts(args, book: AddressBook):
    return '\n'.join(str(record) for record in book.data.values())

# Функція для додавання дати народження до контакту
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    return "Contact not found."

# Функція для показу дати народження контакту
@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.value.strftime('%d.%m.%Y')}"
    return "Contact not found or birthday not set."

# Функція для виведення днів народження на наступному тижні
def show_upcoming_birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return '\n'.join(f"{record.name.value} has birthday on {record.birthday.value.strftime('%d.%m.%Y')}" for record in upcoming)
    return "No upcoming birthdays in the next 7 days."

# Функція для розбору вводу користувача
def parse_input(user_input):
    return user_input.strip().split()

# Головна функція програми
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(phone_contact(args, book))

        elif command == "all":
            print(show_all_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(show_upcoming_birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
