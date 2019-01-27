import http.client as hclient
import re
import xml.etree.ElementTree as ElementTree
import sqlite3


def get_weather_html(station, data_begin, data_end):
    con = hclient.HTTPConnection("pogoda-service.ru", port=80)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    con.request("POST", "/archive_gsod_res.php", "country=RU&station=" + station +"&datepicker_beg=" + data_begin + "&datepicker_end=" + data_end, headers)
    response = con.getresponse()
    #print(response.read())
    return response.read().decode("UTF-8")


def fix_xml(xml_string):
    """ Исправляет закрытие тегов

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
    xml_string = re.sub("(<tbody align =\"center\">)(.{0,20})(<tbody align =\"center\">)", "<tbody align=\"center\">", xml_string, flags=re.DOTALL)
    return xml_string

def create_db(station, statloc, table_body):
    database = sqlite3.connect("../data/weather.db")
    cursor = database.cursor()
    cursor.execute("""CREATE TABLE testweather (statName TEXT, 
                                                statLoc TEXT,
                                                date TEXT,
                                                tempMax INT,
                                                tempMin INT,
                                                press INT,
                                                wind INT,
                                                falls INT)""")
    for row in table_body:
        date = row[0].text
        temp_max = row[1].text
        if (temp_max == None):
            temp_max = 0
        temp_min = row[2].text
        if (temp_min == None):
            temp_min = 0
        press = row[4].text
        if (press == None):
            press = 0
        wind = row[5].text
        if (wind == None):
            wind = 0
        falls = row[6].text
        if (falls == None):
            falls = 0

        statement = "INSERT INTO testweather VALUES ('"+station+"', '"+statloc+"', '" \
                    +date+"', "+str(temp_max)+", " \
                    +str(temp_min)+", "+str(press)+", " \
                    +str(wind)+", "+str(falls)+")"
        print(statement)
        cursor.execute(statement)

    cursor.close()
    database.commit()
    database.close()

weatherHtml = get_weather_html("276120", "01.01.2000", "31.12.2000")
weatherHtml = fix_xml(weatherHtml)
#file_in = open("../data/test.html", "r")
#file_out = open("../data/test.html", "w", encoding="UTF-8-sig")

#file_out.write(weatherHtml)




html = ElementTree.fromstring(weatherHtml)

main_div = html[1][2]
table_body = main_div[5][1]
station = main_div[1].text

iter = main_div.itertext()
i = 0
while i < 100:
    statloc = re.search("Географические координаты: .{0,13}", next(iter))
    if (statloc != None):
        statloc = statloc.group(0)[27:]
        break
    i+=1

create_db(station, statloc, table_body)
