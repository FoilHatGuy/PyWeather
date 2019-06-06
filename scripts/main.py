import datetime as dt
import re
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as msg
import tkinter.ttk as ttk
from tkinter import PhotoImage
import os
import pandas as pd
from dateutil.relativedelta import relativedelta

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from scripts.data import Data
from scripts.editdialog import EditDialog


# from scripts.insertdialog import InsertDialog


class Gui:
    def __init__(self, data):
        self.imageId = None
        self.view = 'groove'
        self.pointer = data
        self.root = tk.Tk()
        self.root.title("PyWeather")
        self.root.resizable(False, False)

        def daysupdatecounter(dump):
            """

            :return:
            """
            # print(days.get(), month.get(), year.get())
            if self.monthfilter.get() == 'Все':
                dayscount = 31
            elif self.yearfilter.get() == 'Все':
                if self.monthfilter.get() != 12:
                    dayscount = (dt.date(4, int(self.monthfilter.get()) + 1, 1) - dt.timedelta(days=1)).day
                else:
                    dayscount = (dt.date(4 + 1, 1, 1) - dt.timedelta(days=1)).day
            else:
                if self.monthfilter.get() != 12:
                    dayscount = (dt.date(int(self.yearfilter.get()), int(self.monthfilter.get()) + 1, 1) - dt.timedelta(
                        days=1)).day
                else:
                    dayscount = (dt.date(int(self.yearfilter.get()) + 1, 1, 1) - dt.timedelta(days=1)).day

            self.day.config(values=['Все'] + list(r'{0:02}'.format(x) for x in range(1, dayscount + 1)))
            if self.dayfilter.get() != 'Все' and int(self.dayfilter.get()) > dayscount:
                self.dayfilter.set(dayscount)

        top = ttk.Frame(self.root, relief=self.view, borderwidth=5)
        top.pack(anchor='n')

        top_left = ttk.Frame(top, relief=self.view, borderwidth=5)
        top_left.grid(column=0, row=0)

        # <editor-fold desc="Filters toolbar">
        toolbar = ttk.Frame(top_left, relief=self.view, borderwidth=5)
        toolbar.grid(row=0, column=0, columnspan=3)

        citylabel = ttk.Label(toolbar, text='Город:', width=10, anchor="e")
        citylabel.grid(row=0, column=0)

        self.cityfilter = tk.StringVar(value='Все')
        citychoice = ttk.Combobox(toolbar, textvariable=self.cityfilter, values=['Все'] + self.pointer.getcities(),
                                  state='readonly', width=30)
        citychoice.grid(row=0, column=1)

        datelabel = ttk.Label(toolbar, text='Дата:', width=10, anchor="e")
        datelabel.grid(row=0, column=2, padx=5)

        self.dayfilter = tk.StringVar(value='Все')
        self.day = ttk.Combobox(toolbar, textvariable=self.dayfilter, state='readonly', width=3,
                                values=['Все'] + list(["%.2d" % i for i in range(1, 32)]))
        self.day.grid(row=0, column=3)

        self.monthfilter = tk.StringVar(value='Все')
        self.yearfilter = tk.StringVar(value='Все')
        month = ttk.Combobox(toolbar, textvariable=self.monthfilter,
                             values=['Все'] + list(["%.2d" % i for i in range(1, 13)]),
                             state='readonly', width=3)
        month.grid(row=0, column=4)

        year = ttk.Combobox(toolbar, textvariable=self.yearfilter, state='readonly', width=5, values=['Все'] + list(
            range(self.pointer.getdate()[0].year, self.pointer.getdate()[1].year + 1)))
        year.grid(row=0, column=5)

        refresh = ttk.Button(toolbar, text='Обновить', command=lambda: self.askdata(list(
            map(lambda x: x.get(), [self.cityfilter, self.dayfilter, self.monthfilter, self.yearfilter]))))
        refresh.grid(row=0, column=6, padx=30)

        month.bind('<<ComboboxSelected>>', daysupdatecounter)
        year.bind('<<ComboboxSelected>>', daysupdatecounter)
        # </editor-fold>

        # <editor-fold desc="Table">
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
        # </editor-fold>

        # <editor-fold desc="Right editor panel">
        editor = ttk.Frame(top, relief=self.view, borderwidth=5)
        editor.grid(column=1, row=0, columnspan=3)

        self.insert_but = ttk.Button(editor, text="Insert row", command=self.insert)
        self.insert_but.grid(row=0, column=0, pady=8)

        self.edit_button = ttk.Button(editor, text="Edit row", command=self.editrow)
        self.edit_button.grid(row=1, column=0, pady=8)

        self.delete_but = ttk.Button(editor, text="Delete row", command=self.delete)
        self.delete_but.grid(row=2, column=0, pady=8)

        save_butt = ttk.Button(editor, text="Save to disk", command=self.save)
        save_butt.grid(row=3, column=0, pady=8)

        delete_but = ttk.Button(editor, text="Load database", command=self.load)
        delete_but.grid(row=4, column=0, pady=8)

        save_butt = ttk.Button(editor, text="Save figure", command=self.savefigure)
        save_butt.grid(row=5, column=0, pady=8)
        # </editor-fold>

        # <editor-fold desc="Graphs area">
        self.graph_area = ttk.Frame(self.root, relief=self.view, borderwidth=5, height=100, width=100)
        self.graph_area.pack(anchor='s', fill='y')

        # but1 = ttk.Button(bottom, text="This is not a button")
        # but1.grid(row=0, column=0, pady=8)
        # but2 = ttk.Button(bottom, text="This one too")
        # but2.grid(row=1, column=0, pady=8)
        # but3 = ttk.Button(bottom, text="Don't press me")
        # but3.grid(row=2, column=0, pady=8)
        # self.graph = tk.Label(graph_area)
        # self.graph.grid(row=0, column=0)

        # </editor-fold>
        self.fig = plt.Figure()
        self.msge = tk.Label(self.graph_area, text='Невозможно построить график')
        self.msge.grid(row=0, column=0)
        self.plot = self.fig.add_subplot(111)
        self.graph = FigureCanvasTkAgg(self.fig, master=self.graph_area)
        self.graph.get_tk_widget().grid(row=0, column=0)
        self.graph.get_tk_widget().grid_forget()

        self.askdata(['Все', 'Все', 'Все', 'Все'])

        self.root.update()
        self.root.mainloop()

    def savefigure(self):
        if not self.imageId:
            files = [f for f in os.listdir('../graphics') if
                     os.path.isfile('../graphics' + f) and not re.match(r'\d\d\d\.png', f)]
            indx = pd.DataFrame(columns=['ID', 'city', 'minDate', 'maxDate'])

            if files:
                for file in files:
                    indx = indx.append(pd.read_csv('../graphics' + file, encoding="utf-8", sep=";"), sort=False)
                # print(indx)
                self.imageId = max(indx['ID'].to_list())
            else:
                self.imageId = 0
        self.fig.savefig('../graphics/{0:03}.png'.format(self.imageId))

    def load(self):
        route = fd.askopenfilename()
        print(route)
        if not re.match(r'.*\d{3}\.csv', route):
            if route:
                self.pointer.load_data(route)
        else:
            msg.showerror('Недопустимое имя', "Имя файла имеет недопустимы формат. Пожалуйста, введите другое имя.")
        self.askdata(list(
            map(lambda x: x.get(), [self.cityfilter, self.dayfilter, self.monthfilter, self.yearfilter])))

    def insert(self):
        if self.table.focus() != '':
            self.edit_button.config(state=tk.DISABLED)
            curr_item = self.table.focus()
            # print(curr_item)
            curr_item_info = self.table.item(self.table.focus())
            edialog = EditDialog(self.root, [curr_item] + curr_item_info['values'], False)
            if self.root.state() == 'normal' and (not False or (True or False)):
                self.edit_button.config(state=tk.NORMAL)
            if edialog.exit_code == 1:
                new_values = edialog.get_values()
                print(new_values)
                print(curr_item)
                # self.table.insert("", index, iid=curr_item, text=curr_item, values=new_values)
                self.table.insert('', self.table.index(curr_item) + 1,
                                  iid=[dt.datetime.strptime(new_values[1], '%d.%m.%Y'), new_values[0]], text=curr_item,
                                  values=new_values)
                # new_values[1] = dt.datetime.strptime(new_values[1], "%d.%m.%Y")
                self.pointer.insert_row(curr_item, new_values)

    def editrow(self):
        if self.table.focus() != '':
            self.edit_button.config(state=tk.DISABLED)
            curr_item = self.table.focus()
            # print(curr_item)
            curr_item_info = self.table.item(self.table.focus())
            edialog = EditDialog(self.root, [curr_item] + curr_item_info['values'], True)
            if self.root.state() == 'normal' and (not False or (True or False)):
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
        self.msge.grid_forget()
        self.graph.get_tk_widget().grid(row=0, column=0)
        df = self.pointer.my_get_data(filt)
        # print(df)
        data = 'tempMax'
        self.table.delete(*self.table.get_children())
        for city in df.keys():
            for row in df[city].to_dict('index').items():
                row = list(row)
                row[0] = dt.date(row[0].year, row[0].month, row[0].day)
                # print(row)
                self.table.insert("", "end", iid=str(row[0]) + ' ' + city, text=row[0].strftime("%d.%m.%Y"),
                                  values=[city, row[0].strftime("%d.%m.%Y")] + list(row[1].values()))
        print(filt)

        # <editor-fold desc="diagram">
        graph_drawed = False
        # <editor-fold desc="BAR: All cities in one day">
        if filt[0] == 'Все' and filt[1] != 'Все' and filt[2] != 'Все' and filt[3] != 'Все':
            # cities = df.keys()
            values = [x.loc[filt[3] + "-" + filt[2] + "-" + filt[1]][data] for x in df.values()]

            x = np.arange(len(df.keys()))
            if self.plot:
                self.fig.clf()
            bb = self.fig.add_subplot(111)
            # print(bb)
            self.plot = bb.bar(x, values)
            bb.set_xticklabels(df.keys(), rotation='vertical')
            bb.set_title(r'Погода в городах России на {0:02}.{1:02}.{2:04}'.format(int(filt[1]), int(filt[2]), int(filt[3])))
            self.fig.tight_layout()
            graph_drawed = True
            self.graph.draw()
        # </editor-fold>

        # <editor-fold desc="PLOT: One month of year in one city">
        elif filt[0] != 'Все' and filt[1] == 'Все' and filt[2] != 'Все' and filt[3] != 'Все':
            dates = []
            values = []

            for row in df[filt[0]].iterrows():
                dates.append(row[0].strftime("%d.%m.%Y"))
                values.append(row[1][data])

            # print(dates)
            # print(values)

            x = np.arange(len(dates))
            # print(x)

            if self.plot:
                self.fig.clf()
            bb = self.fig.add_subplot(111)
            self.plot = bb.plot(x, values, 'o-')
            bb.set_title('Данные по одному месяцу в г.', filt[0])
            bb.set_xticks(x, False)
            bb.set_xticklabels(dates, rotation='vertical')
            self.fig.tight_layout()
            self.graph.draw()
            graph_drawed = True

            # One month of year in one city
        # </editor-fold>

        # <editor-fold desc="PLOT: annual in one city">
        elif filt[0] != 'Все' and filt[1] == 'Все' and filt[2] == 'Все' and filt[3] != 'Все':
            dates = []
            values = []
            for month in range(1, 13):
                # print(df[filt[0]][df[filt[0]].index.month == month][data].median())
                # print(df[filt[0]].index.strftime("%m.%Y"))
                dates.append(df[filt[0]][df[filt[0]].index.month == month].index[0].strftime("%m.%Y"))
                values.append(df[filt[0]][df[filt[0]].index.month == month][data].median())

            # print(dates)
            # print(values)

            x = np.arange(len(dates))
            # print(x)

            if self.plot:
                self.fig.clf()
            bb = self.fig.add_subplot(111)
            self.plot = bb.plot(x, values, 'o-')
            print(filt[0])
            bb.set_title('Годовое изменение погоды в г. '+filt[0])
            bb.set_xticks(x, False)
            bb.set_xticklabels(dates, rotation='vertical')
            self.fig.tight_layout()
            self.graph.draw()
            graph_drawed = True

            pass
        # </editor-fold>

        # <editor-fold desc="PLOT: temp during several years in one city">
        elif filt[0] != 'Все' and filt[1] == 'Все' and filt[2] == 'Все' and filt[3] == 'Все':
            city = list(df.keys())[0]
            # print(city)

            dates = []
            values = []
            date = self.pointer.getdate()[0]
            while self.pointer.getdate()[0] <= date <= self.pointer.getdate()[1]:
                # print(df[city][df[city].index.month == month][data].median())
                # print(df[city].index.strftime("%m.%Y"))
                dates.append(df[city][df[city].index.month == date.month].index[0].strftime("%m.%Y"))
                values.append(df[city][(df[city].index.month == date.month) &
                                       (df[city].index.year == date.year)][data].median())
                date += relativedelta(months=1)

            # print(dates)
            # print(values)

            x = np.arange(len(dates))
            # print(x)

            if self.plot:
                self.fig.clf()
            bb = self.fig.add_subplot(111)
            self.plot = bb.plot(x, values, 'o-')
            bb.set_title(city)
            bb.set_xticks(x, False)
            bb.set_xticklabels(dates, rotation='vertical')
            self.fig.tight_layout()
            self.graph.draw()
            graph_drawed = True

        # <editor-fold desc="BAR: Average monthly temp among cities">
        elif filt[0] == 'Все' and filt[1] == 'Все' and filt[2] != 'Все' and filt[3] != 'Все':
            dates = []
            values = []
            for city in list(df.keys()):
                # print(df[city][df[city].index.month == month][data].median())
                # print(df[city].index.strftime("%m.%Y"))
                dates.append(city)
                values.append(df[city][data].mean())

            x = np.arange(len(df.keys()))
            if self.plot:
                self.fig.clf()
            bb = self.fig.add_subplot(111)
            # print(bb)
            self.plot = bb.bar(x, values)
            bb.set_xticklabels(df.keys(), rotation='vertical')
            self.fig.tight_layout()
            graph_drawed = True
            self.graph.draw()
        # </editor-fold>

        else:
            if self.plot:
                self.fig.clf()
            self.graph.get_tk_widget().grid_forget()
            self.msge.grid(row=0, column=0)
            pass
        # </editor-fold>


        if graph_drawed:
            # plt.savefig("../graphics/tmp.png")
            #
            # self.photo = PhotoImage(file="../graphics/tmp.png")
            # self.graph.configure(image=self.photo, width=700, height=500)
            pass

        # </editor-fold>

        # example of element:
        # print(list(df.iterrows())[0])


if __name__ == "__main__":
    Gui(Data())
