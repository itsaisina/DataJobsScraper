import json
from typing import NoReturn

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import openpyxl
from webdriver_manager.chrome import ChromeDriverManager


def load_config(config_path: str) -> dict:
    """
    Загружает конфигурационный файл
    """
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config


def init_driver(headless_mode: bool) -> webdriver.Chrome:
    """
    Инициализирует драйвер браузера с необходимыми опциями
    """
    options = Options()
    if headless_mode:
        options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def get_html_selenium(url: str, timeout: int) -> str:
    """
    Получает HTML страницы через Selenium
    """
    with init_driver(config['headless_mode']) as driver:
        driver.get(url)
        time.sleep(timeout)
        return driver.page_source


def get_page_count(html: str) -> int:
    """
    Определяет количество страниц с вакансиями
    """
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('div', class_='with-pagination__pages')
    return int(pagination.find_all('a')[-1].text) if pagination else 1


def get_vacancy_details(vacancy_url: str, timeout: int) -> list:
    """
    Извлекает детали вакансии по URL
    """
    html = get_html_selenium(vacancy_url, timeout)
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.select_one('.page-title__title').text.strip()
    date = soup.select_one('.vacancy-header__date time').text.strip()

    sections = soup.find_all(class_='content-section')

    index_section = 0

    salary_section = soup.select_one('.basic-salary')
    salary = salary_section.text.strip() if salary_section else ""

    if len(sections) == 4:
        index_section += 1

    requirements_section = sections[index_section].find_all(class_='inline-list')[0]

    if requirements_section:
        requirements_items = requirements_section.text.split(' • ')
        position, level = requirements_items[0].split(', ') if ', ' in requirements_items[0] else (
            requirements_items[0], "")
        additional_requirements = ', '.join(requirements_items[1:]) if len(requirements_items) > 1 else ""
    else:
        position, level, additional_requirements = "", "", ""

    index_section += 1

    loc_and_type_section = sections[index_section].find_all(class_='inline-list')[0]
    if loc_and_type_section:
        loc_and_type_items = loc_and_type_section.text.split(' • ')
        location = loc_and_type_items[0] if (any(char.isdigit() for char in loc_and_type_items[0]) or
                                             "," in loc_and_type_items[0]) else ""
        full_time = "Полный рабочий день" in loc_and_type_section.text
        remote = "Можно удалённо" in loc_and_type_section.text
    else:
        location, full_time, remote = "", False, False

    company_section = soup.select_one('.vacancy-company__title .link-comp')
    company = company_section.text.strip() if company_section else ""

    return [title, date, salary, position, level, additional_requirements, location, full_time, remote, company,
            vacancy_url]


def get_vacancy_links(page_url: str, timeout: int) -> list:
    """
    Собирает ссылки на вакансии с заданной страницы поиска
    """
    vacancy_links = []
    current_page = 0
    last_page_reached = False

    while not last_page_reached:
        current_page += 1
        html = get_html_selenium(f"{page_url}&page={current_page}", timeout)
        soup = BeautifulSoup(html, 'html.parser')

        next_page_button = soup.select_one('.with-pagination__side-button [rel="next"]')
        last_page_reached = not bool(next_page_button)

        for link in soup.find_all('a', href=True, class_='vacancy-card__title-link'):
            vacancy_links.append('https://career.habr.com' + link['href'])

    return vacancy_links


def scrape_vacancies(config: dict) -> NoReturn:
    """
    Основная функция для сбора информации о вакансиях и сохранения её в файл Excel
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Название вакансии', 'Дата публикации', 'Зарплата', 'Должность', 'Уровень', 'Дополнительные требования',
               'Местоположение', 'Полный рабочий день', 'Можно удаленно', 'Компания', 'Ссылка на вакансию'])

    seed_url = config['seed_url']
    for level in config['levels']:
        for category in config['categories']:
            link = f"{seed_url}{level}{category}"
            vacancy_links = get_vacancy_links(link, config['timeout'])
            for vacancy_link in vacancy_links:
                try:
                    details = get_vacancy_details(vacancy_link, config['timeout'])
                    ws.append(details)
                    print(f"Обработана вакансия: {details[0]}")
                except Exception as e:
                    print(f"Ошибка при обработке вакансии {vacancy_link}: {e}")

    wb.save('vacancies.xlsx')


if __name__ == "__main__":
    config = load_config('scrapper_config.json')
    scrape_vacancies(config)
