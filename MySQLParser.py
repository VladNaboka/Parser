import datetime
import dateparser
from bs4 import BeautifulSoup as BS
import requests
import pymysql

idF = 0
tags = ['div', 'h2', 'span', 'ul', 'h3', 'a', 'time']
article = ''

def TContent(article):
    for o in range(len(tags)):
        while True:
            objTag = el.find_all(f'{tags[o]}', {article})
            if objTag == []:
                print('Неверно - ', tags[o], article)
                break
            else:
                print('Верно - ', tags[o], article)
                return objTag
try:
    connection = pymysql.connect(host='127.0.0.1',port=3306, user='root', database='DataBaseParser', cursorclass=pymysql.cursors.DictCursor)
    print("Sucsessful")

    try:
        with connection.cursor() as cursor:
            tableRes = "CREATE TABLE `resource`(RESOURCE_ID bigint(20) AUTO_INCREMENT," \
                       "RESOURCE_NAME varchar(255), " \
                       "RESOURCE_URL varchar(255), " \
                       "top_tag varchar(255), " \
                       "bottom_tag varchar(255), " \
                       "title_cut varchar(255), " \
                       "date_cut varchar(255), " \
                       "PRIMARY KEY(RESOURCE_ID));"
            cursor.execute(tableRes)
            print("Создалась resource")

        with connection.cursor() as cursor:
            insertData = "INSERT INTO `resource` (RESOURCE_NAME, RESOURCE_URL, top_tag, bottom_tag, title_cut, date_cut) " \
                         "VALUES('nur.kz', 'https://www.nur.kz/latest/', 'body > div.page__container > div > main', " \
                         "'article-preview-category__subhead', 'article-preview-category__text', 'article-preview-category__date')"
            cursor.execute(insertData)
            insertData2 = "INSERT INTO `resource` (RESOURCE_NAME, RESOURCE_URL, top_tag, bottom_tag, title_cut, date_cut) " \
                         "VALUES('scientificrussia.ru', 'https://scientificrussia.ru/news', '#w0', " \
                         "'lead', 'title', 'prop time')"
            cursor.execute(insertData2)
            insertData3 = "INSERT INTO `resource` (RESOURCE_NAME, RESOURCE_URL, top_tag, bottom_tag, title_cut, date_cut) " \
                         "VALUES('tengrinews.kz', 'https://tengrinews.kz/find-out/', 'body > div.my-app > main > section', " \
                         "'tn-hidden', 'tn-article-title', 'tn-data-list')"
            cursor.execute(insertData3)
            insertData4 = "INSERT INTO `resource` (RESOURCE_NAME, RESOURCE_URL, top_tag, bottom_tag, title_cut, date_cut) " \
                         "VALUES('zakon.kz', 'https://www.zakon.kz/news/', 'div.zmainCard.z-row', " \
                         "'title', 'title', 'info')"
            cursor.execute(insertData4)
            connection.commit()

        with connection.cursor() as cursor:
            tableItem = "CREATE TABLE `items`(id int(11) AUTO_INCREMENT," \
                       "res_id int(11), " \
                       "link varchar(255), " \
                       "title text, " \
                       "content text, " \
                       "nd_date int(11), " \
                       "s_date int(11), " \
                       "not_date date, " \
                       "PRIMARY KEY(id));"
            cursor.execute(tableItem)

        with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM `resource`")
                rows = cursor.fetchall()
                for row in rows:
                    print(row.get('RESOURCE_NAME'))
                    url = requests.get(row.get('RESOURCE_URL'))
                    soup = BS(url.text, "html.parser")
                    for el in soup.select(row.get('top_tag')):
                        try:
                            dateContent = TContent(article=row.get('date_cut'))
                            textContent = TContent(article=row.get('bottom_tag'))
                            titleContent = TContent(article=row.get('title_cut'))
                            internalL = [
                                 a.get('href') for a in el.find_all('a')
                                 if a.get('href') and a.get('href')]
                            for i in range(len(dateContent)):
                                dateP = dateparser.parse(dateContent[i].text.strip(), date_formats=['%Y %B %d'], settings={'TIMEZONE': 'UTC'})
                                insert = "INSERT INTO `items`(res_id, link, title, content, nd_date, s_date, not_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                                values = (row.get('RESOURCE_ID'), internalL[i], titleContent[i].text.strip(), textContent[i].text.strip(), int(dateP.timestamp()), str(int(datetime.datetime.now().timestamp())), dateP)
                                cursor.execute(insert, values)
                                connection.commit()
                        except Exception as er:
                             pass
    finally:
        connection.close()
except Exception as e:
    print(e)