import csv  # для работы с csv файлами (таблицы)
import json  # для работы с json файлами (словари)
from bs4 import BeautifulSoup  # поиск по html странице
from selenium import webdriver  # необходимо для предотвращения блокировок
import requests  # используется в получении json словаря
import random  # случайная задержка для запросов
import time  # случайная задержка для запросов
from os.path import isfile  # для проверки на существование файла html страницы

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/103.0.0.0 "
                  "Safari/537.36",
}


def get_data(url, region):
    # # Получаем json со страницы с информацией о анализах
    # # (самое главное - uri, для перехода на другие страницы)
    #
    # req = requests.get(url + region, headers=headers)
    # src = req.text
    # # print(src)
    #
    # with open(f'{region}.html', 'w') as f:
    #     f.write(src)
    #
    # with open("f{region}.html") as f:
    #     src = f.read()
    #
    # soup = BeautifulSoup(src, 'lxml')
    # json_dict = soup.find("div", style="display: none").get("data-services-list")
    #
    # with open("msk.json", 'w') as f:
    #     json.dump(json.loads(json_dict), f, indent=4, ensure_ascii=False)

    with open("msk.json") as f:  # загружаем список комплексов из полученного json файла
        compleces_list = json.load(f)

    with open("all_information.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow((
            'Название',
            'Цена (руб)',
            'Срок (дней)',
            'Биоматериал',
            'Исследования'
        ))

    list_of_information_dict = []
    iterations = len(compleces_list)
    cnt_iterations = 1
    for item in compleces_list:  # итерируемся по комплексам анализов, заходя на каждую страницу отдельно
        print(f"Итерация {cnt_iterations}: {item['uri']}.\nОсталось итераций: {iterations - cnt_iterations} ...")

        if not isfile(f"data/{item['uri']}.html"):  # если страницы нет, то запрашиваем ее с сайта и сохраняем
            time.sleep(random.uniform(1, 4))  # задержка для предотвращения блокировок

            category_href = url + item['uri']
            driver = webdriver.Chrome()
            try:  # получаем страницу через Selenium
                driver.get(category_href)

                src = driver.page_source
                with open(f"data/{item['uri']}.html", 'w') as file:
                    file.write(src)

            except Exception as ex:  # при ошибке пытаемся еще раз запросить страницу
                print(ex)

                time.sleep(random.uniform(10, 13))
                driver.get(category_href)

                src = driver.page_source
                with open(f"data/{item['uri']}.html", 'w') as file:
                    file.write(src)
            finally:
                driver.close()
                driver.quit()

        with open(f"data/{item['uri']}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')
        try:  # получаем список необходимых анализов
            composition_block = soup.find('div', class_='js-tests')
            h_cards = composition_block.find_all('div', class_='js-card-item')
            analyses = []
            for card in h_cards:
                analys_name = card.find(class_='h-card__inner').find(class_='_name'). \
                    find(class_='h-card__content').text
                analyses.append(analys_name)
        except Exception:
            analyses = ["Нет данных"]

        try:  # получаем биоматериал
            biomaterial = soup.find(class_='a-head__bio').find(class_='a-head__td').text
        except Exception:
            biomaterial = 'Нет данных'

        try:  # получаем имя комплекса
            name = item['name'].strip()
        except Exception:
            name = 'Нет данных'

        try:  # получаем цену комплекса
            price = item['price'].strip()
            if ' ' in price:  # цена может быть в формате "4 050", преобразуем ее в "4050"
                price = price.replace(' ', '')
        except Exception:
            price = 'Нет данных'

        try:  # получем срок прохождения комплекса в днях
            time_in_days = item['time']
        except Exception:
            time_in_days = 'Нет данных'

        # формируем словарь для последующей записи в json
        information_dict = {
            'Название': name,
            'Цена (руб)': price,
            'Срок (дней)': time_in_days,
            'Биоматериал': biomaterial.capitalize(),
            'Исследования': analyses
        }
        list_of_information_dict.append(information_dict)

        # записываем строку в csv файл
        with open("all_information.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow((
                name,
                price,
                time_in_days,
                biomaterial.capitalize(),
                '\n'.join(analyses)  # каждый анализ с новой строки
            ))

        cnt_iterations += 1

    with open("all_information.json", 'w') as f:
        json.dump(list_of_information_dict, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    get_data("http://kdl.ru/analizy-i-tseny/", 'msk')
