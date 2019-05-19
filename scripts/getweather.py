import http.client as hclient
import re
import xml.etree.ElementTree as ElementTree
import datetime
import pandas as pd
from pandas import DataFrame


def get_weather_html(station, data_begin, data_end):
    con = hclient.HTTPConnection("pogoda-service.ru", port=80)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    con.request("POST", "/archive_gsod_res.php", "country=RU&station=" + station + "&datepicker_beg=" + data_begin.strftime('%d.%m.%Y') +
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


def create_db(station, table_body):
    columns = ["statName", "date", "tempMax", "tempMin", "press", "wind", "falls"]
    df = DataFrame(columns=["statName", "date", "tempMax", "tempMin", "press", "wind", "falls"])
    for row in table_body:
        date = row[0].text
        temp_max = row[1].text
        if temp_max is None:
            temp_max = -200
        temp_min = row[2].text
        if temp_min is None:
            temp_min = -200
        press = row[4].text
        if press is None:
            press = -200
        wind = row[5].text
        if wind is None:
            wind = -200
        falls = row[6].text
        if falls is None:
            falls = -200

        l_row = {"statName": station, "date": date, "tempMax": str(temp_max), "tempMin": str(temp_min),
                 "press": str(press), "wind": str(wind), "falls": str(falls)}
        # print(l_row)
        df = df.append(l_row, ignore_index=True)
    return df


stations = [['325830', 'Петропавловск - Камчатский'], ['319600', 'Владивосток'], ['249590', 'Якутск'],
            ['307100', 'Иркутск'], ['295700', 'Красноярск'], ['286980', 'Омск'], ['287220', 'Уфа'],
            ['349290', 'Краснодар'], ['276120', 'Москва'], ['260630', 'Санкт - Петербург'], ['225500', 'Архангельск'],
            ['221130', 'Мурманск'], ['267020', 'Калининград ']]

df = DataFrame(columns=["statName", "date", "tempMax", "tempMin", "press", "wind", "falls"])
startdate = datetime.date(2000, 1, 1)
enddate = datetime.date(2011, 12, 31)
delta = datetime.timedelta(days=1000)
for item in stations:
    print(item[1])
    date = startdate - delta
    while enddate - date > delta:
        date += delta
        print('from:', date, 'to end:', enddate - date)
        html = ElementTree.fromstring(fix_xml(get_weather_html(item[0], date, enddate)))
        df = pd.concat([df, create_db(item[1], html[1][2][5][1])], ignore_index=True)

df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
print(df)
df.to_csv("../data/weather.csv", sep=";", index=False)
