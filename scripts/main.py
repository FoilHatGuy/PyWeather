import datetime as dt
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk

import pandas as pd


class Data:
    def __init__(self):
        self.dataframe = pd.read_csv("../data/weather.csv", encoding="utf-8", sep=";")
        self.dataframe['date'] = pd.to_datetime(self.dataframe['date'])
        # print(self.dataframe.dtypes)
        # self.getdata(self.dataframe)
        self.cities = sorted(list(set(self.dataframe['statName'])))
        self.mindate = min(set(self.dataframe['date']))
        self.maxdate = max(set(self.dataframe['date']))
        # print(self.mindate, self.maxdate)

    def open(self):
        route = fd.askopenfile(initialdir="../data/", title="Select file to open", defaultextension='.csv',
                               filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if route is not None:
            self.dataframe = pd.read_csv(route, encoding="utf-8", sep=";")

    def getdata(self, filters):
        print(filters)
        # city = '.*' if filters[0] == 'all' else filters[0]
        # print(self.dataframe[self.dataframe['statName'].str.contains(city, regex=True)])
        # print(self.dataframe['statName'].str.contains(str(city)))
        # date = '\-'.join(map(lambda x: '.*' if x == 'all' else x, filters[:0:-1]))
        # print(
        #     (self.dataframe['statName'].str.contains(filters[0], regex=True) if filters[0] != 'all' else True) &
        #     (self.dataframe['date'].dt.day == int(filters[1]) if filters[1] != 'all' else True) &
        #     (self.dataframe['date'].dt.month == int(filters[2]) if filters[2] != 'all' else True) &
        #     (self.dataframe['date'].dt.year == int(filters[3]) if filters[3] != 'all' else self.dataframe['date'].dt.year > 0))
        return self.dataframe[
            (self.dataframe['statName'].str.contains(filters[0], regex=True) if filters[0] != 'all' else True) &
            (self.dataframe['date'].dt.day == int(filters[1]) if filters[1] != 'all' else True) &
            (self.dataframe['date'].dt.month == int(filters[2]) if filters[2] != 'all' else True) &
            (self.dataframe['date'].dt.year == int(filters[3]) if filters[3] != 'all' else self.dataframe[
                                                                                               'date'].dt.year > 0)]
        # return self.dataframe

    def getcities(self):
        return self.cities

    def getdate(self):
        return [self.mindate, self.maxdate]

    @staticmethod
    def save(data):
        route = fd.asksaveasfile(initialdir="../data/", title="Select file to save", defaultextension='.csv',
                                 filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if route is not None:
            data.to_csv(route, encoding="utf-8", sep=";")


class Gui:
    def __init__(self, data):
        self.pointer = data
        self.df = pd.DataFrame()
        root = tk.Tk()

        root.resizable(False, False)

        def daysupdatecounter(days, month, year):
            nonlocal day
            # print(days.get(), month.get(), year.get())
            if month.get() == 'all':
                dayscount = 31
            elif year.get() == 'all':
                if month.get() != 12:
                    dayscount = (dt.date(4, int(month.get()) + 1, 1) - dt.timedelta(days=1)).day
                else:
                    dayscount = (dt.date(4 + 1, 1, 1) - dt.timedelta(days=1)).day
            else:
                if month.get() != 12:
                    dayscount = (dt.date(int(year.get()), int(month.get()) + 1, 1) - dt.timedelta(days=1)).day
                else:
                    dayscount = (dt.date(int(year.get()) + 1, 1, 1) - dt.timedelta(days=1)).day

            day.config(values=['all'] + list(range(1, dayscount + 1)))
            if days.get() != 'all' and int(days.get()) > dayscount:
                days.set(dayscount)

        top = ttk.Frame(root, relief='groove', borderwidth=5)
        top.pack(anchor='n')

        top_left = ttk.Frame(top, relief='groove', borderwidth=5)
        top_left.grid(column=0, row=0)

        # upper toolbar with filters
        toolbar = ttk.Frame(top_left, relief='flat', borderwidth=5)
        toolbar.grid(row=0, column=0, columnspan=3)

        citylabel = ttk.Label(toolbar, text='city:', width=10, anchor="e")
        citylabel.grid(row=0, column=0)

        cityfilter = tk.StringVar(value='all')
        citychoice = ttk.Combobox(toolbar, textvariable=cityfilter, values=['all'] + self.pointer.getcities(),
                                  state='readonly', width=30)
        citychoice.grid(row=0, column=1)

        datelabel = ttk.Label(toolbar, text='date:', width=10, anchor="e")
        datelabel.grid(row=0, column=2, padx=5)

        dayfilter = tk.StringVar(value='all')
        day = ttk.Combobox(toolbar, textvariable=dayfilter, state='readonly', width=3,
                           values=['all'] + list(["%.2d" % i for i in range(1, 32)]))
        day.grid(row=0, column=3)

        monthfilter = tk.StringVar(value='all')
        yearfilter = tk.StringVar(value='all')
        month = ttk.Combobox(toolbar, textvariable=monthfilter,
                             values=['all'] + list(["%.2d" % i for i in range(1, 13)]),
                             state='readonly', width=3)
        month.grid(row=0, column=4)
        month.bind('<<ComboboxSelected>>', lambda x: daysupdatecounter(dayfilter, monthfilter, yearfilter))

        year = ttk.Combobox(toolbar, textvariable=yearfilter, state='readonly', width=5, values=['all'] + list(
            range(self.pointer.getdate()[0].year, self.pointer.getdate()[1].year + 1)))
        year.grid(row=0, column=5)

        refresh = ttk.Button(toolbar, text='refresh', command=lambda: self.askdata(list(
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
        tableframe = ttk.Frame(top_left, relief='groove', borderwidth=5)
        tableframe.grid(row=1, column=0, columnspan=3)

        self.table = ttk.Treeview(tableframe,
                                  columns=["ID", "statName", "date", "tempMax", "tempMin", "press", "wind", "falls"],
                                  show='headings')

        scroll = ttk.Scrollbar(tableframe, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)

        scroll.pack(side='right', fill='y')
        self.table.pack(side='left', fill='y')

        self.table.column('ID', width=50)
        self.table.heading('ID', text='ID')

        self.table.column('statName', width=180)
        self.table.heading('statName', text='city')

        self.table.column('date', width=70)
        self.table.heading('date', text='date')

        self.table.column('tempMax', width=80)
        self.table.heading('tempMax', text='Max temp')

        self.table.column('tempMin', width=80)
        self.table.heading('tempMin', text='Min temp')

        self.table.column('press', width=80)
        self.table.heading('press', text='pressure')

        self.table.column('wind', width=50)
        self.table.heading('wind', text='wind')

        self.table.column('falls', width=50)
        self.table.heading('falls', text='falls')
        # table ends

        # right editor panel
        editor = ttk.Frame(top, relief='groove', borderwidth=5)
        editor.grid(column=1, row=0, columnspan=3)
        button1 = ttk.Button(editor, text="Insert row", command=lambda: self.insert(self.df))
        button1.grid(row=0, column=0, pady=8)
        button2 = ttk.Button(editor, text="Delete row", command=lambda: self.delete(self.df))
        button2.grid(row=1, column=0, pady=8)

        button2 = ttk.Button(editor, text="Save to disk", command=lambda: self.save(self.df))
        button2.grid(row=2, column=0, pady=8)
        # editor panel ends
        self.askdata(['all', 'all', 'all', 'all'])

        # canvas with graphs
        bottom = ttk.Frame(root, relief='groove', borderwidth=5, height=100, width=100)
        bottom.pack(anchor='s', fill='y')

        button1 = ttk.Button(bottom, text="In1sert row", command=lambda: self.insert(self.df))
        button1.grid(row=0, column=0, pady=8)
        button2 = ttk.Button(bottom, text="De1lete row", command=lambda: self.delete(self.df))
        button2.grid(row=1, column=0, pady=8)

        button2 = ttk.Button(bottom, text="Sa1ve to disk", command=lambda: self.pointer.save(self.df))
        button2.grid(row=2, column=0, pady=8)
        # /canvas

        root.update()
        root.mainloop()

    def insert(self, data):
        pass

    def delete(self, data):
        pass

    def askdata(self, filt):
        self.df = self.pointer.getdata(filt)
        self.table.delete(*self.table.get_children())
        for row in self.df.iterrows():
            # print(row)
            rowdata = row[1].tolist()
            # print(rowdata)
            self.table.insert("", "end", values=rowdata[0:2] + [rowdata[2].strftime("%d.%m.%Y")] + rowdata[3:])
        # example of element:
        # print(list(data.iterrows())[0])


if __name__ == "__main__":
    Gui(Data())
