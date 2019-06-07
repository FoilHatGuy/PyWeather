import datetime as dt
import os
import re

import pandas as pd


class Data:
    """
    Класс базы данных. Хз.
    """
    def __init__(self):
        self.dictdf = {}
        self.cityindex = pd.DataFrame()
        self.load_data("../data/index.csv")
        self.mindate = dt.date(3000, 1, 1)
        self.maxdate = dt.date(1000, 1, 1)
        self.cityindex['minDate'] = pd.to_datetime(self.cityindex['minDate'], format='%Y-%m-%d')
        self.cityindex['maxDate'] = pd.to_datetime(self.cityindex['maxDate'], format='%Y-%m-%d')
        self.mindate = min(set(self.cityindex['minDate']))
        self.maxdate = max(set(self.cityindex['maxDate']))

        # print(self.dictdf)

    def my_get_data(self, filters):
        """
        Returns dict of dataframes with cities which match to filters

        :param filters: list of filters
        :return: dict of dataframes
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

    #
    # def getdata(self, filters):
    #     # print(filters)
    #     dictdf = {filters[0]: {'city': self.cityindex.loc[filters[0]]}} if filters[
    #                                                                           0] != 'Все' else self.cityindex.to_dict(
    #         'index')
    #     # df = pd.DataFrame(columns=['tempMax', 'tempMin', 'press', 'wind', 'falls'])
    #     #print('dictdf: ', dictdf)
    #     df = {}
    #     for x in dictdf.keys():
    #         # print(df)
    #         buf = pd.read_csv('../data/{0:03d}.csv'.format(self.cityindex.loc[x]['ID']), encoding="utf-8", sep=";",
    #                           index_col='date')
    #         # print(buf)
    #         buf.index = pd.to_datetime(buf.index)
    #         ioi = buf[(buf.index.day == int(filters[1]) if filters[1] != 'Все' else True) &
    #                   (buf.index.month == int(filters[2]) if filters[2] != 'Все' else True) &
    #                   (buf.index.year == int(filters[3]) if filters[3] != 'Все' else buf.index.year > 0)]
    #         # print(ioi)
    #         df.update({x: ioi})
    #     return df

    def getcities(self):
        return self.cityindex.index.to_list()

    def getdate(self):
        return [self.mindate, self.maxdate]

    def save(self, route):
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
        Loads 001.csv ... xxx.csv to dict of dataframes

        :return:
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

        # print(self.dictdf)

    def insert_row(self, iid, values):
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
        # print(values)
        # print(iid)
        # print(iid.split())
        ddf = pd.DataFrame.from_dict({0: [iid.split()[0]] + values[2:]}, orient='index',
                                     columns=["date", "tempMax", "tempMin", "press", "wind", "falls"]).set_index('date')
        # df = pd.read_csv('../data/{0:03d}.csv'.format(self.cityindex.loc[iid.split()[1]]['ID']),
        # encoding="utf-8", sep=";", index_col='date')
        self.dictdf[iid.split()[1]].update(ddf)
        # df.to_csv('../data/{0:03d}.csv'.format(self.cityindex.loc[iid.split()[1]]['ID']),
        # encoding="utf-8", sep=";", index=False)

    def delete_row(self, item):
        print(item)
        self.dictdf[item.split()[1]] = self.dictdf[item.split()[1]].drop(
            dt.datetime.strptime(item.split()[0], '%Y-%m-%d'), axis='index')
        if self.dictdf[item.split()[1]].size == 0:
            self.cityindex = self.cityindex.drop(item.split()[1])
            self.dictdf.pop(item.split()[1])
            # print(self.dictdf)
        pass
