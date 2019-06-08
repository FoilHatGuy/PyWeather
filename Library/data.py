import datetime as dt
import os
import re

import pandas as pd


class Data:
    """
    Класс базы данных. Выполняет функции и действия по отношению к данным.
    """
    def __init__(self):
        self.dictdf = {}
        self.cityindex = pd.DataFrame()
        self.load_data("../Data/index.csv")
        self.mindate = dt.date(3000, 1, 1)
        self.maxdate = dt.date(1000, 1, 1)
        self.cityindex['minDate'] = pd.to_datetime(self.cityindex['minDate'], format='%Y-%m-%d')
        self.cityindex['maxDate'] = pd.to_datetime(self.cityindex['maxDate'], format='%Y-%m-%d')
        self.mindate = min(set(self.cityindex['minDate']))
        self.maxdate = max(set(self.cityindex['maxDate']))

        # print(self.dictdf)

    def get_data(self, filters):
        """
        Возвращает словарь из датафреймов, которые соответствуют фильтрам

        :param filters: список из фильтров
        :return: словарь датафреймов вида {город: датафрейм}
        """
        dictdf = {}
        if filters[0] == 'Все':
            for city in self.dictdf.keys():
                # print(self.dictdf[city].index.year>0)
                dictdf[city] = self.dictdf[city][
                    (self.dictdf[city].index.day == int(filters[1]) if filters[1] != 'Все' else True) &
                    (self.dictdf[city].index.month == int(filters[2]) if filters[2] != 'Все' else True) &
                    (self.dictdf[city].index.year == int(filters[3]) if filters[3] != 'Все' else
                     self.dictdf[city].index.year > 0)]

        else:
            dictdf[filters[0]] = self.dictdf[filters[0]][
                (self.dictdf[filters[0]].index.day == int(filters[1]) if filters[1] != 'Все' else True) &
                (self.dictdf[filters[0]].index.month == int(filters[2]) if filters[2] != 'Все' else True) &
                (self.dictdf[filters[0]].index.year == int(filters[3]) if filters[3] != 'Все' else self.dictdf[filters[
                    0]].index.year > 0)]
        return dictdf

    def getcities(self):
        """
        Возвращает список имеющихся в базе данных городов

        :return: список городов
        """
        return self.cityindex.index.to_list()

    def get_date_list(self):
        return [self.cityindex['minDate'], self.cityindex['maxDate']]

    def getdate(self):
        """
        Возвращает список из минимальной и максимальной дат во всей базе данных

        :return: [самая ранняя дата, самая поздняя дата]
        """
        return [self.mindate, self.maxdate]

    def save(self, route):
        """
        сохраняет базу данных по указанному маршруту

        :param route: Путь, где лежит основной файл базы данных
        """
        direct = '/'.join(route.split('/')[:-1]) + '/'
        files = [f for f in os.listdir(direct) if
                 os.path.isfile(direct + f) and not re.match(r'\d\d\d\.csv', f) and re.match(r'.*\.csv', f)]
        indx = pd.DataFrame(columns=['ID', 'city', 'minDate', 'maxDate'])

        if files:
            for file in files:
                indx = indx.append(pd.read_csv(direct + file, encoding="utf-8", sep=";"), sort=False)
            # print(indx)
            idx = max(indx['ID'].to_list())
        else:
            idx = 0
        indx = pd.DataFrame(columns=['ID', 'city', 'minDate', 'maxDate'])
        for item in self.cityindex.iterrows():
            # print(item[0])
            idx += 1
            self.dictdf[item[0]] \
                .to_csv(direct + '{0:03}'.format(idx) + '.csv',
                        sep=";",
                        index=True,
                        encoding='utf-8')
            indx = indx.append(pd.DataFrame([[idx, item[0],
                                              min(set(self.dictdf[item[0]].index)),
                                              max(set(self.dictdf[item[0]].index))]],
                                            columns=['ID', 'city', 'minDate', 'maxDate']))
        indx.to_csv(route, sep=";", encoding='utf-8', index=False)

    def load_data(self, route):
        """
        Загружает основной файл и сопутствующие ему файлы

        :param route: Путь основного файла
        """
        del self.dictdf
        self.dictdf = {}
        self.cityindex = pd.read_csv(route, encoding="utf-8", sep=";", index_col=u'city')
        direct = '/'.join(route.split('/')[:-1]) + '/'
        for row in self.cityindex.iterrows():
            id_str = str(row[1]['ID']).zfill(3)
            self.dictdf.update(
                {row[0]: pd.read_csv(direct + id_str + ".csv", encoding="utf-8", sep=";").set_index('date')})
            self.dictdf[row[0]].index = pd.to_datetime(self.dictdf[row[0]].index)


    def insert_row(self, iid, values):
        """
        Вставляет новый ряд данных и, если необходимо, дополняет список городов

        :param iid: координаты новой ячейки данных
        :param values: значения ячейки
        """
        print(dt.datetime.strptime(str(iid.split()[0]), '%Y-%m-%d'))

        ddf = pd.DataFrame.from_dict({0: [iid.split()[0]] + values[2:]}, orient='index',
                                     columns=["date", "tempMax", "tempMin", "press", "wind", "falls"]).set_index('date')
        ddf.index = pd.to_datetime(ddf.index)
        if values[0] not in self.cityindex.keys():
            self.cityindex = \
                self.cityindex.append(pd.DataFrame([[max(self.cityindex['ID']) + 1, values[0],
                                                     dt.datetime.strptime(iid.split()[0], '%Y-%m-%d'),
                                                     dt.datetime.strptime(iid.split()[0], '%Y-%m-%d')]],
                                                   columns=['ID', 'city', 'minDate', 'maxDate']).set_index('city'),
                                      sort=False)
            self.dictdf.update({values[0]: ddf})
        else:
            self.cityindex.at[iid.split()[1], 'minDate'] = min(self.cityindex.loc[iid.split()[1]]['minDate'],
                                                               dt.datetime.strptime(iid.split()[0], '%Y-%m-%d'))
            self.cityindex.at[iid.split()[1], 'maxDate'] = max(self.cityindex.loc[iid.split()[1]]['maxDate'],
                                                               dt.datetime.strptime(iid.split()[0], '%Y-%m-%d'))

            self.dictdf[iid.split()[1]].update(ddf)

    def update_row(self, iid, values):
        """
        Изменяет ячейку в базе данных

        :param iid: координаты ячейки данных
        :param values: новые значения ячейки
        """

        ddf = pd.DataFrame.from_dict({0: [iid.split()[0]] + values[2:]}, orient='index',
                                     columns=["date", "tempMax", "tempMin", "press", "wind", "falls"]).set_index('date')
        self.dictdf[iid.split()[1]].update(ddf)

    def delete_row(self, item):
        """
        Удаляет ряд из базы данных

        :param item: координаты ряда
        """
        print(item)
        self.dictdf[item.split()[1]] = self.dictdf[item.split()[1]].drop(
            dt.datetime.strptime(item.split()[0], '%Y-%m-%d'), axis='index')
        if self.dictdf[item.split()[1]].size == 0:
            self.cityindex = self.cityindex.drop(item.split()[1])
            self.dictdf.pop(item.split()[1])
            # print(self.dictdf)
        pass
