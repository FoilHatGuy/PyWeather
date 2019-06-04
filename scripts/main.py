import datetime as dt
import re
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as msg
import tkinter.ttk as ttk
import os
import pandas as pd

from scripts.editdialog import EditDialog


class Data:
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

    def load_data(self, route):
        """
        Loads 001.csv ... xxx.csv to dict of dataframes

        :return:
        """
        self.cityindex = pd.read_csv(route, encoding="utf-8", sep=";", index_col=u'city')
        direct = '/'.join(route.split('/')[:-1]) + '/'
        for row in self.cityindex.iterrows():
            id_str = str(row[1]['ID']).zfill(3)
            self.dictdf.update(
                {row[0]: pd.read_csv(direct + id_str + ".csv", encoding="utf-8", sep=";").set_index('date')})
            self.dictdf[row[0]].index = pd.to_datetime(self.dictdf[row[0]].index)

        # print(self.dictdf['Петропавловск-Камчатский'])

    def my_get_data(self, filters):
        """
        Returns dict of dataframes with cities which match to filters

        :param filters: list of filters
        :return: dict of dataframes
        """

        dictdf = {}
        if filters[0] == 'Все':
            for city in self.dictdf.keys():
                dictdf[city] = self.dictdf[city][
                    (self.dictdf[city].index.day == int(filters[1]) if filters[1] != 'Все' else True) &
                    (self.dictdf[city].index.month == int(filters[2]) if filters[2] != 'Все' else True) &
                    (self.dictdf[city].index.year == int(filters[3]) if filters[3] != 'Все' else self.dictdf[
                                                                                                     city].index.year > 0)]

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
    #                                                                            0] != 'Все' else self.cityindex.to_dict(
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
            self.dictdf[item[0]]\
                .to_csv(direct + '{0:03}'.format(idx) + '.csv',
                                        sep=";",
                                        index=False,
                                        encoding='utf-8')
            indx = indx.append(pd.DataFrame([[idx, item[0],
                                              min(set(self.dictdf[item[0]].index)),
                                              max(set(self.dictdf[item[0]].index))]],
                                            columns=['ID', 'city', 'minDate', 'maxDate']))
        indx.to_csv(route, sep=";", encoding='utf-8', index=False)

    def open(self, route):  # TODO remove askopenfile
        direct = '/'.join(route.split('/')[:-1]) + '/'
        route = fd.askopenfilename(initialdir="../data/", title="Select file to open", defaultextension='.csv',
                                   filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if route is not None and not re.match(r'\d\d\d\.csv', route):
            self.cityindex = pd.read_csv(route, encoding="utf-8", sep=";")

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
        self.dictdf[item.split()[1]] = self.dictdf[item.split()[1]].drop(dt.datetime.strptime(item.split()[0], '%Y-%m-%d'), axis='index')
        if self.dictdf[item.split()[1]].size == 0:
            self.cityindex = self.cityindex.drop(item.split()[1])
            self.dictdf.pop(item.split()[1])
            # print(self.dictdf)
        pass


class Gui:
    def __init__(self, data):
        self.view = 'flat'
        self.pointer = data
        self.root = tk.Tk()
        self.root.title("PyWeather")
        self.root.resizable(False, False)

        def daysupdatecounter(days, month, year):
            nonlocal day
            # print(days.get(), month.get(), year.get())
            if month.get() == 'Все':
                dayscount = 31
            elif year.get() == 'Все':
                if month.get() != 12:
                    dayscount = (dt.date(4, int(month.get()) + 1, 1) - dt.timedelta(days=1)).day
                else:
                    dayscount = (dt.date(4 + 1, 1, 1) - dt.timedelta(days=1)).day
            else:
                if month.get() != 12:
                    dayscount = (dt.date(int(year.get()), int(month.get()) + 1, 1) - dt.timedelta(days=1)).day
                else:
                    dayscount = (dt.date(int(year.get()) + 1, 1, 1) - dt.timedelta(days=1)).day

            day.config(values=['Все'] + list(range(1, dayscount + 1)))
            if days.get() != 'Все' and int(days.get()) > dayscount:
                days.set(dayscount)

        top = ttk.Frame(self.root, relief=self.view, borderwidth=5)
        top.pack(anchor='n')

        top_left = ttk.Frame(top, relief=self.view, borderwidth=5)
        top_left.grid(column=0, row=0)

        # upper toolbar with filters
        toolbar = ttk.Frame(top_left, relief=self.view, borderwidth=5)
        toolbar.grid(row=0, column=0, columnspan=3)

        citylabel = ttk.Label(toolbar, text='Город:', width=10, anchor="e")
        citylabel.grid(row=0, column=0)

        cityfilter = tk.StringVar(value='Все')
        citychoice = ttk.Combobox(toolbar, textvariable=cityfilter, values=['Все'] + self.pointer.getcities(),
                                  state='readonly', width=30)
        citychoice.grid(row=0, column=1)

        datelabel = ttk.Label(toolbar, text='Дата:', width=10, anchor="e")
        datelabel.grid(row=0, column=2, padx=5)

        dayfilter = tk.StringVar(value='Все')
        day = ttk.Combobox(toolbar, textvariable=dayfilter, state='readonly', width=3,
                           values=['Все'] + list(["%.2d" % i for i in range(1, 32)]))
        day.grid(row=0, column=3)

        monthfilter = tk.StringVar(value='Все')
        yearfilter = tk.StringVar(value='Все')
        month = ttk.Combobox(toolbar, textvariable=monthfilter,
                             values=['Все'] + list(["%.2d" % i for i in range(1, 13)]),
                             state='readonly', width=3)
        month.grid(row=0, column=4)
        month.bind('<<ComboboxSelected>>', lambda x: daysupdatecounter(dayfilter, monthfilter, yearfilter))

        year = ttk.Combobox(toolbar, textvariable=yearfilter, state='readonly', width=5, values=['Все'] + list(
            range(self.pointer.getdate()[0].year, self.pointer.getdate()[1].year + 1)))
        year.grid(row=0, column=5)

        refresh = ttk.Button(toolbar, text='Обновить', command=lambda: self.askdata(list(
            map(lambda x: x.get(), [cityfilter, dayfilter, monthfilter, yearfilter]))))
        refresh.grid(row=0, column=6, padx=30)

        def updatestartfilter():
            pass
            # if isinstance(yearfilter.get(), int) and isinstance(monthfilter.get(), int) and isinstance(dayfilter.get(), int):
            #     datefilter = dt.date(int(yearfilter.get()), int(monthfilter.get()), int(dayfilter.get()))
            # print(startdatefilter)

        day.bind('<<ComboboxSelected>>', lambda x: updatestartfilter())
        month.bind('<<ComboboxSelected>>', lambda x: daysupdatecounter(dayfilter, monthfilter, yearfilter),
                   updatestartfilter())
        year.bind('<<ComboboxSelected>>', lambda x: daysupdatecounter(dayfilter, monthfilter, yearfilter),
                  updatestartfilter())

        # test = tk.Label(toolbar, textvariable=self.cityfilter, width=25)
        # test.grid(row=0, column=1)

        # toolbar ends

        # table starts
        tableframe = ttk.Frame(top_left, relief='groove', borderwidth=2)
        tableframe.grid(row=1, column=0, columnspan=3)

        self.table = ttk.Treeview(tableframe,
                                  columns=["statName", "date", "tempMax", "tempMin", "press", "wind", "falls"])

        scroll = ttk.Scrollbar(tableframe, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table['show'] = "headings"
        scroll.pack(side='right', fill='y')
        self.table.pack(side='left', fill='y')

        self.table.column('#0', width=50)
        self.table.heading('#0', text='ID')

        self.table.column('statName', width=180)
        self.table.heading('statName', text='Город')

        self.table.column('date', width=70)
        self.table.heading('date', text='Дата')

        self.table.column('tempMax', width=80)
        self.table.heading('tempMax', text='Maкс температура')

        self.table.column('tempMin', width=80)
        self.table.heading('tempMin', text='Mин темпратура')

        self.table.column('press', width=80)
        self.table.heading('press', text='Атм давление')

        self.table.column('wind', width=50)
        self.table.heading('wind', text='Скорость ветра')

        self.table.column('falls', width=50)
        self.table.heading('falls', text='Осадки')
        # table ends

        # right editor panel
        editor = ttk.Frame(top, relief=self.view, borderwidth=5)
        editor.grid(column=1, row=0, columnspan=3)
        # <<<<<<< HEAD
        #         button1 = tttk.Button(editor, text="Insert row", command=lambda: self.insert(self.df))
        #         button1.grid(row=0, column=0, pady=8)
        #         button2 = tttk.Button(editor, text="open file", command=lambda: self.pointer.open())
        #         button2.grid(row=1, column=0, pady=8)
        #
        #         button2 = tttk.Button(editor, text="Save to disk", command=lambda: self.pointer.save())
        #         button2.grid(row=2, column=0, pady=8)
        # =======

        self.insert_but = ttk.Button(editor, text="Insert row", command=self.insert)
        self.insert_but.grid(row=0, column=0, pady=8)

        self.edit_button = ttk.Button(editor, text="Edit row", command=self.editrow)
        self.edit_button.grid(row=1, column=0, pady=8)

        self.delete_but = ttk.Button(editor, text="Delete row", command=self.delete)
        self.delete_but.grid(row=2, column=0, pady=8)

        save_butt = ttk.Button(editor, text="Save to disk", command=lambda: self.save())
        save_butt.grid(row=3, column=0, pady=8)

        delete_but = ttk.Button(editor, text="Load database", command=self.load)
        delete_but.grid(row=4, column=0, pady=8)

        # >>>>>>> a945df43bd1acf5d7e229d8915c95378b3e0bcf2
        # editor panel ends
        self.askdata(['Все', 'Все', 'Все', 'Все'])

        # canvas with graphs
        bottom = ttk.Frame(self.root, relief=self.view, borderwidth=5, height=100, width=100)
        bottom.pack(anchor='s', fill='y')

        but1 = ttk.Button(bottom, text="This is not a button")
        but1.grid(row=0, column=0, pady=8)
        but2 = ttk.Button(bottom, text="This one too")
        but2.grid(row=1, column=0, pady=8)
        but3 = ttk.Button(bottom, text="Don't press me")
        but3.grid(row=2, column=0, pady=8)
        # /canvas

        self.root.update()
        self.root.mainloop()

    def insert(self, data):
        pass

    def load(self):
        route = fd.askopenfilename()
        print(route)
        if not re.match(r'.*\d{3}\.csv', route):
            if route:
                self.pointer.load_data(route)
        else:
            msg.showerror('Недопустимое имя', "Имя файла имеет недопустимы формат. Пожалуйста, введите другое имя.")

    def editrow(self):
        if self.table.focus() != '':
            self.edit_button.config(state=tk.DISABLED)
            curr_item = self.table.focus()
            # print(curr_item)
            curr_item_info = self.table.item(self.table.focus())
            edialog = EditDialog(self.root, [curr_item] + curr_item_info['values'])
            if 'normal' == self.root.state():
                self.edit_button.config(state=tk.NORMAL)
            if edialog.exit_code == 1:
                new_values = edialog.get_values()
                self.table.item(curr_item, text=curr_item, values=new_values)
                new_values[1] = dt.datetime.strptime(new_values[1], "%d.%m.%Y")
                self.pointer.update_row(curr_item, new_values)

    def save(self):
        route = fd.asksaveasfilename(title="Select file to save",
                                        filetypes=(("csv files", ".csv"),
                                                   ("all files", ".*")),
                                        defaultextension='.csv',
                                        initialdir="../data/")
        if not re.match(r'\d{3}\.csv', route):
            self.pointer.save(route)
        else:
            msg.showerror('Недопустимое имя', "Имя файла имеет недопустимы формат. Пожалуйста, введите другое имя.")

    def delete(self):
        if self.table.focus() != '':
            curr_item = self.table.focus()
            self.table.delete(curr_item)
            self.pointer.delete_row(curr_item)

    def askdata(self, filt):
        df = self.pointer.my_get_data(filt)
        # print(df)
        self.table.delete(*self.table.get_children())
        for city in df.keys():
            for row in df[city].to_dict('index').items():
                row = list(row)
                row[0] = dt.date(row[0].year, row[0].month, row[0].day)
                # print(row)
                self.table.insert("", "end", iid=str(row[0]) + ' ' + city, text=row[0].strftime("%d.%m.%Y"),
                                  values=[city, row[0].strftime("%d.%m.%Y")] + list(row[1].values()))
        # example of element:
        # print(list(df.iterrows())[0])


if __name__ == "__main__":
    Gui(Data())
