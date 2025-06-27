# Сторонние библиотеки
import psycopg2
from config import DB_CONFIG

from src.api_utils import load_company, load_vacancies, loader_vacancies_top_10
from src.db_utils import insert_employers, insert_vacancies
from src.database import create_database, create_tables
from src.db_manager import DBManager


def user_interface(text):
    manager = DBManager()
    if text == 'да':
        employer_id_top = [
            '9013908',  # НЭВЗ ✅+
            '39305',    # Газпром нефть ✅+
            '4592004',  # билайн ✅+
            '749858',   # ВТБ ✅+
            '80',       # Альфа-Банк ✅+
            '3443',     # дом.рф ✅+
            '592442',   # Mail.ru Group ✅+
            '4996233',  # Роснефть ✅+
            '11454714', # Магнит ✅+
            '9777667',  # Росатом ✅+
            '1122462',  # SkyEng ✅+
            '4496',     #МТС Банк ✅+
            '31050'     #Рив Гош  ✅+
        ]
        print(" Загрузка данных из API...")
        vacancies_list = loader_vacancies_top_10(employer_id_top)

        if not vacancies_list:
            print("Не найдено ни одной вакансии.")
            return

        # Проверяем, какие компании были найдены
        found_employers = set()
        for vac in vacancies_list:
            emp = vac.get('employer')
            if emp:
                found_employers.add(emp['id'])

        print(f"Найденные компании: {found_employers}")

        seen = set()
        unique_employers = []
        for vac in vacancies_list:
            emp = vac.get('employer')
            if emp and emp['id'] not in seen:
                seen.add(emp['id'])
                unique_employers.append(emp)

        print(f"Сохранение {len(unique_employers)} работодателей...")
        insert_employers(unique_employers)

        print(f" Сохранение {len(vacancies_list)} вакансий...")
        insert_vacancies(vacancies_list)

    elif text == 'нет':
        user_input = input("Введите список от одной до 10 компаний через пробел: ").lower().strip()
        names = user_input.split()
        if len(names) > 10:
            print("Введите не более 10 компаний")
            return

        print(" Загрузка данных из API...")
        load = load_company(user_input)  # Вакансии по ключевому слову
        filter = load_vacancies(load)  # Все вакансии этих компаний

        if not load:
            print(" Не найдено ни одного работодателя.")
            return

        print(f" Найдено {len(load)} уникальных работодателей")
        insert_employers(filter)

        print(" Сохранение вакансий...")
        if not filter:
            print(" Нет вакансий для сохранения")
            return
        print(f" Найдено {len(filter)} вакансий")
        insert_vacancies(filter)

        print("\nВыберите действие:")
        print("1. Вывести компании и количество вакансий")
        print("2. Вывести все вакансии")
        print("3. Средняя зарплата")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")

        choice = input("Введите номер действия: ")

        if choice == "1":
            res = manager.get_companies_and_vacancies_count()
            print("\n Компании и количество вакансий:")
            for name, count in res:
                print(f"{name}: {count} вакансий")

        elif choice == "2":
            res = manager.get_all_vacancies()
            print("\n Все вакансии:")
            for item in res:
                print(item)

        elif choice == "3":
            avg = manager.get_avg_salary()
            print(f"\n Средняя зарплата: {avg:.2f}")

        elif choice == "4":
            avg = manager.get_avg_salary()
            res = manager.get_vacancies_with_higher_salary(avg)
            print(f"\n Вакансии с зарплатой выше средней ({avg:.2f}):")
            for item in res:
                print(item)

        elif choice == "5":
            word = input("Введите ключевое слово: ")
            res = manager.get_vacancies_with_keyword(word)
            print(f"\n Результаты поиска по '{word}':")
            for item in res:
                print(item)

        else:
            print(" Неверный выбор")
    else:
        print('Введите только "да" или "нет"!')

    manager.close()


if __name__ == "__main__":
    create_database()
    create_tables()

    while True:
        user_question = input("Вывести вакансии из топ 10 компаний: да/нет ").strip().lower()
        if user_question in ['да', 'нет']:
            break
        else:
            print(' Введите только "да" или "нет"!')

    user_interface(user_question)