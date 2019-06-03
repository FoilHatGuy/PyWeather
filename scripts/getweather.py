import datetime
import http.client as hclient
import os
import re
import xml.etree.ElementTree as ElementTree

import pandas as pd
from pandas import DataFrame


def get_weather_html(station, data_begin, data_end):
    con = hclient.HTTPConnection("pogoda-service.ru", port=80)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    con.request("POST", "/archive_gsod_res.php",
                "country=RU&station=" + station + "&datepicker_beg=" + data_begin.strftime('%d.%m.%Y') +
                "&datepicker_end=" + data_end.strftime('%d.%m.%Y'), headers)
    response = con.getresponse()
    # print(response.read())
    return response.read().decode("UTF-8")


def fix_xml(xml_string):
    """
    Исправляет закрытие тегов

    Согласно стандарту XML любой тег либо должен быть закрыт
    либо должен быть самозакрывающимся. В HTML это не
    обязательно, поэтому теги <meta>, <link> и др. не имеют
    закрывающих пар. Это вызывает проблему парсинга HTML
    файла с помощью ElementTree. Эта функция заменяет > на
    /> делая теги самозакрывающимися

    :param xml_string: XML строка для обработки
    :return: Исправленная строка
    """

    xml_string = re.sub("(<meta.{0,200}[^/])(>)", r"\1/\2", xml_string)
    xml_string = re.sub("(<link.{0,200})(>)", r"\1/\2", xml_string)
    xml_string = re.sub("(<br)(>)", r"\1/\2", xml_string)
    xml_string = re.sub("(<tbody align =\"center\">)(.{0,20})(<tbody align =\"center\">)", "<tbody align=\"center\">",
                        xml_string, flags=re.DOTALL)
    return xml_string


def create_db(table_body):
    columns = ["date", "tempMax", "tempMin", "press", "wind", "falls"]
    df = DataFrame(columns=columns)
    # print(str(table_body))
    # # for row in table_body:
    # #     date = row[0].text
    #     temp_max = row[1].text
    #     if temp_max is None:
    #         temp_max = -200
    #     temp_min = row[2].text
    #     if temp_min is None:
    #         temp_min = -200
    #     press = row[4].text
    #     if press is None:
    #         press = -200
    #     wind = row[5].text
    #     if wind is None:
    #         wind = -200
    #     falls = row[6].text
    #     if falls is None:
    #         falls = -200
    #     l_row = {"date": date, "tempMax": str(temp_max), "tempMin": str(temp_min),
    #              "press": str(press), "wind": str(wind), "falls": str(falls)}
    #
    #     df = df.append(l_row, ignore_index=True)
    # print(list(table_body))
    # print(list(map(lambda x: dict(zip(columns, list(map(lambda y: -200 if y.text is None else y.text, list(x))))), table_body)))
    df = df.append(list(
        map(lambda x: dict(zip(columns, list(map(lambda y: -200 if y.text is None else y.text, list(x))))),
            table_body)), ignore_index=True)
    # l_row = {"date": row[0].text, "tempMax": str(row[1].text), "tempMin": str(row[2].text),
    #          "press": str(row[4].text), "wind": str(row[5].text), "falls": str(row[6].text)}

    # print(l_row)
    return df


stations = [['325830', 'Петропавловск-Камчатский'], ['319600', 'Владивосток'], ['249590', 'Якутск'],
            ['307100', 'Иркутск'], ['295700', 'Красноярск'], ['286980', 'Омск'], ['287220', 'Уфа'],
            ['349290', 'Краснодар'], ['276120', 'Москва'], ['260630', 'Санкт-Петербург'], ['225500', 'Архангельск'],
            ['221130', 'Мурманск'], ['267020', 'Калининград']]

files = [f for f in os.listdir('../data') if
         os.path.isfile('../data/' + f) and not re.match(r'\d\d\d\.csv', f) and re.match(r'.*\.csv', f)]
indx = DataFrame(columns=['ID', 'city'])

if files:
    for file in files:
        indx = indx.append(pd.read_csv("../data/" + file, encoding="utf-8", sep=";"), sort=False)
    print(indx)
    idx = max(indx['ID'].to_list())
else:
    idx = 0
startdate = datetime.date(2000, 1, 1)
enddate = datetime.date(2000, 1, 5)
delta = datetime.timedelta(days=1000)
indx = DataFrame(columns=['ID', 'city', 'minDate', 'maxDate'])
for item in stations:
    idx += 1
    df = DataFrame(columns=["date", "tempMax", "tempMin", "press", "wind", "falls"])
    print(item[1])
    date = startdate - delta
    while enddate - date > delta:
        date += delta
        print('from:', date, 'to end:', enddate - date)
        html = ElementTree.fromstring(fix_xml(get_weather_html(item[0], date, enddate)))
        df = pd.concat([df, create_db(html[1][2][5][1])], ignore_index=True, sort=False)
    # print(df['date'])
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
    print(df)
    df.to_csv('../data/' + '{0:03}'.format(idx) + '.csv', sep=";", index=False, encoding='utf-8')

    indx = indx.append(pd.DataFrame([[idx, item[1], min(set(df['date'])), max(set(df['date']))]], columns=['ID', 'city', 'minDate', 'maxDate']))

# indx = indx.set_index('ID')
print(indx)
indx.to_csv('../data/index.csv', sep=";", encoding='utf-8', index=False)





















