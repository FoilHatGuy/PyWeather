import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk

import pandas as pd


class Data:
    def __init__(self):
        self.dataframe = pd.read_csv("../data/weather.csv", encoding="utf-8", sep=";")
        # self.getdata(self.dataframe)
        self.cities = sorted(list(set(self.dataframe['statName'])))
        self.mindate = min(set(self.dataframe['date']))
        self.maxdate = max(set(self.dataframe['date']))
        print(self.mindate, self.maxdate)

    def open(self):
        route = fd.askopenfile(initialdir="../data/", title="Select file to open", defaultextension='.csv',
                               filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if route is not None:
            self.dataframe = pd.read_csv(route, encoding="utf-8", sep=";")

    def getdata(self, filters):
        if filters == 'all':
            return self.dataframe

    def getcities(self):
        return self.cities

    def getdate(self):
        return [self.mindate, self.maxdate]

    def getdateint(self):
        return [list(map(int, self.mindate.split('.'))), list(map(int, self.maxdate.split('.')))]

    @staticmethod
    def save(data):
        route = fd.asksaveasfile(initialdir="../data/", title="Select file to save", defaultextension='.csv',
                                 filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if route is not None:
            data.to_csv(route, encoding="utf-8", sep=";")


class Gui:
    def __init__(self, data):
        self.pointer = data
        self.df = self.askdata()
        root = tk.Tk()

        # root.resizable(False, False)

        def daysupdatecounter(days, month, year):
            nonlocal day
            print(month.get())
            if month.get() in [1, 3, 5, 7, 8, 10, 12]:
                dayscount = 31
            elif month.get() == 2:
                if year.get() % 4 == 0:
                    dayscount = 29
                else:
                    dayscount = 28
            else:
                dayscount = 20

            day.config(values=list(range(1, dayscount + 1)))
            if days.get() > dayscount:
                days.set(dayscount)

        top = ttk.Frame(root, relief='groove', borderwidth=5)
        top.pack(anchor='n')

        top_left = ttk.Frame(top, relief='groove', borderwidth=5)
        top_left.grid(column=0, row=0)

        # upper toolbar with filters
        toolbar = ttk.Frame(top_left, relief='groove', borderwidth=5)
        toolbar.grid(row=0, column=0, columnspan=3)

        self.cityfilter = tk.StringVar(value=self.pointer.getcities()[0])
        citychoice = ttk.Combobox(toolbar, textvariable=self.cityfilter, values=self.pointer.getcities(),
                                  state='readonly', width=30)
        citychoice.grid(row=0, column=0)

        fromlabel = ttk.Label(toolbar, text='start date:')
        fromlabel.grid(row=0, column=1)

        dayfilter = tk.IntVar(value=self.pointer.getdateint()[0][0])
        day = ttk.Combobox(toolbar, textvariable=dayfilter, state='readonly', width=3, values=list(range(1, 32)))
        day.grid(row=0, column=2)

        monthfilter = tk.IntVar(value=self.pointer.getdateint()[0][1])
        yearfilter = tk.IntVar(value=self.pointer.getdateint()[0][2])
        month = ttk.Combobox(toolbar, textvariable=monthfilter, values=list(range(1, 13)),
                             state='readonly', width=3)
        month.grid(row=0, column=3)
        month.bind('<<ComboboxSelected>>', lambda x: daysupdatecounter(dayfilter, monthfilter, yearfilter))

        year = ttk.Combobox(toolbar, textvariable=yearfilter, state='readonly', width=5,
                            values=list(range(self.pointer.getdateint()[0][2], self.pointer.getdateint()[1][2] + 1)))
        year.grid(row=0, column=4)

        def updatestartfilter():
            startdatefilter = str(dayfilter.get()) + '.' + str(monthfilter.get()) + '.' + str(yearfilter.get())
            print(startdatefilter)

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

        self.table = ttk.Treeview(tableframe, columns=list(range(7)))

        scroll = ttk.Scrollbar(tableframe, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)

        scroll.pack(side='right', fill='y')
        self.table.pack(side='left', fill='y')

        self.table.column(column="#0", width=50)
        self.table.heading(column="#0", text='ID')

        self.table.column(column=0, width=190)
        self.table.heading(column=0, text='city')

        self.table.column(column=1, width=80)
        self.table.heading(column=1, text='date')

        self.table.column(column=2, width=60)
        self.table.heading(column=2, text='tempMax')

        self.table.column(column=3, width=60)
        self.table.heading(column=3, text='tempMin')

        self.table.column(column=4, width=80)
        self.table.heading(column=4, text='pressure')

        self.table.column(column=5, width=50)
        self.table.heading(column=5, text='wind')

        self.table.column(column=6, width=50)
        self.table.heading(column=6, text='falls')
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
        self.view(self.df)

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

    def view(self, data):
        for row in data.iterrows():
            rowdata = row[1].tolist()
            self.table.insert("", "end", text=rowdata[0], values=rowdata[1:])
        # example of element:
        print(list(data.iterrows())[0])

    def askdata(self):
        filters = 'all'
        return self.pointer.getdata(filters)


if __name__ == "__main__":
    Gui(Data())
