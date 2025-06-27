import requests
from config import USER_AGENT
import os

# Получаем путь к текущему скрипту
script_dir = os.path.dirname(os.path.abspath(__file__))
path_to_json = os.path.join(script_dir, "../data/vacancy_hh.json")
os.makedirs(os.path.dirname(path_to_json), exist_ok=True)


def load_company(companies_list_input: str):
    """Ищет работодателя ТОЛЬКО по названию компании и возвращает его ID."""
    company_names = [name.strip() for name in companies_list_input.split(',')]
    employer_ids = []

    for company_name in company_names:
        url = "https://api.hh.ru/employers"
        headers = {'User-Agent': USER_AGENT}
        params = {"text": company_name}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            employers = response.json().get("items", [])

            if employers:
                employer_id = employers[0]['id']# При соблюдении условия берем первый id из employer
                employer_ids.append(employer_id)
                print(f"Найден ID '{employer_id}' для компании '{company_name}'")
            else:
                employer_ids.append(None)
                print(f"Компания '{company_name}' не найдена.")

        except requests.RequestException as e:
            print(f"Ошибка при поиске компании '{company_name}': {e}")
            employer_ids.append(None)

    return employer_id


def loader_vacancies(id_company):
    '''Нахождение вакансий от работодателей из списка вакансий по ID работодателя'''
    url = "https://api.hh.ru/vacancies"
    headers = {'User-Agent': USER_AGENT}
    all_vacancies = []

    for employer_id in id_company:
        if employer_id is None:
            print(f"Пропущен недопустимый ID компании: {employer_id}")
            continue
        params = {"employer_id": employer_id, "per_page": 10}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            vacancies = data.get("items", [])
            if vacancies:
                all_vacancies.extend(vacancies)
                print(f"Найдено {len(vacancies)} вакансий для работодателя {employer_id}")
            else:
                print(f"Нет вакансий для работодателя {employer_id}")

        except requests.RequestException as e:
            print(f"Ошибка при загрузке вакансий для {employer_id}: {e}")

    return all_vacancies


if __name__ == '__main__':
    user_input = input("Введите список компании(например: Яндекс, Сбер...): ").lower()
    company_id =load_company(user_input)
    all_vacancies = loader_vacancies(company_id)
