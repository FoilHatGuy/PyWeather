import datetime as dt
import re
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk

import pandas as pd

from scripts.editdialog import EditDialog


class Data:
    def __init__(self):
        self.cityindex = pd.read_csv("../data/index.csv", encoding="utf-8", sep=";", index_col=u'city')
        self.mindate = dt.date(3000, 1, 1)
        self.maxdate = dt.date(1000, 1, 1)
        self.cityindex['minDate'] = pd.to_datetime(self.cityindex['minDate'], format='%Y-%m-%d')
        self.cityindex['maxDate'] = pd.to_datetime(self.cityindex['maxDate'], format='%Y-%m-%d')
        self.mindate = min(set(self.cityindex['minDate']))
        self.maxdate = max(set(self.cityindex['maxDate']))

    def getdata(self, filters):
        # print(filters)
        dictdf = {filters[0]: {'city': self.cityindex.loc[filters[0]]}} if filters[0] != 'Все' else self.cityindex.to_dict('index')
        # df = pd.DataFrame(columns=['tempMax', 'tempMin', 'press', 'wind', 'falls'])
        # print('dictdf: ', dictdf)
        df = {}
        for x in dictdf.keys():
            # print(df)
            buf = pd.read_csv('../data/{0:03d}.csv'.format(self.cityindex.loc[x]['ID']), encoding="utf-8", sep=";", index_col='date')
            # print(buf)
            buf.index = pd.to_datetime(buf.index)
            ioi = buf[(buf.index.day == int(filters[1]) if filters[1] != 'Все' else True) &
                      (buf.index.month == int(filters[2]) if filters[2] != 'Все' else True) &
                      (buf.index.year == int(filters[3]) if filters[3] != 'Все' else buf.index.year > 0)]
            # print(ioi)
            df.update({x: ioi})
        return df

    def getcities(self):
        return self.cityindex.index.to_list()

    def getdate(self):
        return [self.mindate, self.maxdate]

    def save(self):
        route = fd.askdirectory(initialdir="../data/", title="Select file to save", defaultextension='.csv',
                                filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        # print(self.dataframe)
        if route is not None:
            self.dataframe.to_csv(route, encoding="utf-8", sep=";", index=False)

    def open(self):
        route = fd.askopenfilename(initialdir="../data/", title="Select file to open", defaultextension='.csv',
                                   filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if route is not None and not re.match(r'\d\d\d\.csv', route):
            self.cityindex = pd.read_csv(route, encoding="utf-8", sep=";")

    def update_row(self, iid, values):

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
        #         button1 = ttk.Button(editor, text="Insert row", command=lambda: self.insert(self.df))
        #         button1.grid(row=0, column=0, pady=8)
        #         button2 = ttk.Button(editor, text="open file", command=lambda: self.pointer.open())
        #         button2.grid(row=1, column=0, pady=8)
        #
        #         button2 = ttk.Button(editor, text="Save to disk", command=lambda: self.pointer.save())
        #         button2.grid(row=2, column=0, pady=8)
        # =======

        self.insert_but = ttk.Button(editor, text="Insert row", command=self.insert)
        self.insert_but.grid(row=0, column=0, pady=8)

        self.edit_button = ttk.Button(editor, text="Edit row", command=self.editrow)
        self.edit_button.grid(row=1, column=0, pady=8)

        self.delete_but = ttk.Button(editor, text="Delete row", command=self.delete)
        self.delete_but.grid(row=2, column=0, pady=8)

        save_butt = ttk.Button(editor, text="Save to disk", command=lambda: self.pointer.save())
        save_butt.grid(row=3, column=0, pady=8)
        # >>>>>>> a945df43bd1acf5d7e229d8915c95378b3e0bcf2
        # editor panel ends
        self.askdata(['Все', 'Все', 'Все', 'Все'])

        # canvas with graphs
        bottom = ttk.Frame(self.root, relief=self.view, borderwidth=5, height=100, width=100)
        bottom.pack(anchor='s', fill='y')

        but1 = tk.Button(bottom, text="This is not a button")
        but1.grid(row=0, column=0, pady=8)
        but2 = tk.Button(bottom, text="This one too")
        but2.grid(row=1, column=0, pady=8)
        but3 = tk.Button(bottom, text="Don't press me")
        but3.grid(row=2, column=0, pady=8)
        # /canvas

        self.root.update()
        self.root.mainloop()

    def insert(self, data):
        pass

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

                # <editor-fold desc="Table">
                self.table.item(curr_item, text=curr_item, values=new_values)
                # self.table.delete(curr_item)
                # self.table.insert("", index, iid=curr_item, text=curr_item, values=new_values)
                # </editor-fold>

                # <editor-fold desc="DataFrame">
                new_values[1] = dt.datetime.strptime(new_values[1], "%d.%m.%Y")
                self.pointer.update_row(int(curr_item), new_values)
                # </editor-fold>

    def delete(self, data):
        pass

    def askdata(self, filt):
        df = self.pointer.getdata(filt)
        # print(df)
        self.table.delete(*self.table.get_children())
        for city in df.keys():
            for row in df[city].to_dict('index').items():
                row = list(row)
                row[0] = dt.date(row[0].year, row[0].month, row[0].day)
                # print(row)
                self.table.insert("", "end", iid=(row[0], city), text=row[0].strftime("%d.%m.%Y"),
                                  values=[city, row[0].strftime("%d.%m.%Y")] + list(row[1].values()))
        # example of element:
        # print(list(df.iterrows())[0])


if __name__ == "__main__":
    Gui(Data())
