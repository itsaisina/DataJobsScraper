import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import NoReturn


def create_directory(directory_path: str) -> NoReturn:
    """
    Создает директорию, если она еще не существует
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def load_and_prepare_data(file_path: str) -> pd.DataFrame:
    """
    Загружает и подготавливает данные для анализа
    """
    df = pd.read_excel(file_path)
    df['Местоположение'] = df['Местоположение'].fillna('Не указано')
    df = df.drop('Местоположение', axis=1).join(
        df['Местоположение'].str.split(', ', expand=True)
        .stack().reset_index(level=1, drop=True).rename('Город'))
    return df[df['Должность'].isin(['Аналитик по данным', 'Ученый по данным'])]


def plot_general_statistics(df: pd.DataFrame, save_path: str) -> NoReturn:
    """
    Визуализирует общую статистику вакансий
    """
    vacancies_count = df.groupby(['Должность', 'Уровень']).size().unstack(fill_value=0)
    vacancies_count_long = vacancies_count.reset_index().melt(id_vars='Должность', var_name='Уровень',
                                                              value_name='Количество')
    plt.figure(figsize=(10, 6))
    sns.barplot(data=vacancies_count_long, x='Должность', y='Количество', hue='Уровень')
    plt.title('Количество вакансий по направлениям и уровням')
    plt.xlabel('Направление')
    plt.ylabel('Количество вакансий')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{save_path}/общее_количество_вакансий.png")
    plt.close()


def plot_vacancies_by_city_for_position(df: pd.DataFrame, position: str, save_path: str) -> NoReturn:
    """
    Визуализирует количество вакансий по городам для определенной должности
    """
    df_position = df[df['Должность'] == position]
    vacancies_by_city = df_position.groupby(['Город', 'Уровень']).size().unstack(fill_value=0)
    plt.figure(figsize=(12, 8))
    vacancies_by_city.plot(kind='bar', stacked=True)
    plt.title(f'Количество вакансий для {position} по городам')
    plt.xlabel('Город')
    plt.ylabel('Количество вакансий')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{save_path}/{position.replace(' ', '_')}_по_городам_и_уровням.png")
    plt.close()


def main() -> NoReturn:
    """
    Главная функция для выполнения анализа вакансий
    """
    graphs_folder = "vacancy_graphs"
    create_directory(graphs_folder)
    df = load_and_prepare_data('vacancies.xlsx')
    plot_general_statistics(df, graphs_folder)
    for position in ['Аналитик по данным', 'Ученый по данным']:
        plot_vacancies_by_city_for_position(df, position, graphs_folder)


if __name__ == "__main__":
    main()
