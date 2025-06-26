import requests
from config import USER_AGENT
from pprint import pprint

def loader_vacancy(text: str):
    '''Получение списка вакансий по запросу с ввода ключевого слова через API'''
#Шаг 1: получение вакансий по введеному слову
    vacancy_list = []
    url = "https://api.hh.ru/vacancies"
    headers = {'User-Agent': USER_AGENT}
    text_split = text.replace(',', '').split()
    for name_co in text_split:
        params = {"text": name_co, "per_page": 100}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()  # Если код будет 200

            vacancies = response.json().get("items", [])

# Шаг 2: Фильтрация вакансий, где введенное слово есть ТОЛЬКО в названиях компании
            filtered_vacancies = []
            for vacancy in vacancies:
                employer_name = vacancy.get("employer", {}).get("name", "").lower()
                if name_co in employer_name:
                    filtered_vacancies.append(vacancy)

            vacancy_list.extend(filtered_vacancies)

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'API недоступно. Невозможно получить вакансии "{text_split}":{e}')
    return vacancy_list


#Шаг 3: Определяем ID компании из списка вакансий и производим поиск вакансий от ПОЛУЧЕННЫХ РАБОТОДАТЕЛЕЙ
def loader_company(loader_vacancy):
    '''Нахождение вакансий от работодателей из списка вакансий по ID'''
    url = "https://api.hh.ru/vacancies"
    headers = {'User-Agent': USER_AGENT}
    all_vacancies = []

    # Сбор всех ID работодателей
    employer_ids = {
        vacancy['employer']['id']
        for vacancy in loader_vacancy
        if vacancy.get('employer') and vacancy['employer'].get('id')
    }
    #Поиск вакансий по id работодателя
    for employer_id in employer_ids:
        params = {"employer_id": employer_id, "per_page": 100}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            all_vacancies.extend(data.get("items", []))

        except requests.RequestException as e:
            print(f"Ошибка при загрузке вакансий для {employer_id}: {e}")
    return all_vacancies


def process_vacancy(vacancy):
    '''Представление вакансий по конкретным полям'''
    salary = vacancy.get('salary')

    return {
        'id': vacancy['id'],
        'employer_id': vacancy['employer']['id'],
        'name': vacancy['name'],
        'salary_from': salary['from'] if salary and 'from' in salary else None,
        'salary_to': salary['to'] if salary and 'to' in salary else None,
        'currency': salary['currency'] if salary and 'currency' in salary else None,
        'area': vacancy['area']['name'],
        'url': vacancy['alternate_url']
    }


if __name__ == '__main__':
    user_input = input("Введите список компании через запятую или одну: ").lower()
    step1=loader_vacancy(user_input)
    step2 = loader_company(step1)
    step3 = [process_vacancy(v) for v in step2]
    pprint(step3)
    # for company in step2:
    #     name = get_company_name(company)
    #     print(f"{company}: {name}")

#Яндекс, Мегафон, Teboil, Сбер, Газпром, Магнит, СДЭК, Озон, Мария-ра, Северсталь

# def get_company_name(loader_company):
#     '''Вывод названий компаний по ID'''
#     url = f"https://api.hh.ru/employers/{loader_company}"
#     headers = {"User-Agent": USER_AGENT}
#
#     try:
#         response = requests.get(url, headers=headers, timeout=5)
#         response.raise_for_status()
#         data = response.json()
#         return data["name"]
#     except (requests.RequestException, KeyError):
#         return "Неизвестная компания"
