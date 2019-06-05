import datetime as dt
import re
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as msg
import tkinter.ttk as ttk
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import PhotoImage


from scripts.data import Data
from scripts.editdialog import EditDialog
from scripts.insertdialog import InsertDialog


class Gui:
    def __init__(self, data):
        self.view = 'groove'
        self.pointer = data
        self.root = tk.Tk()
        self.root.title("PyWeather")
        self.root.resizable(False, False)

        def daysupdatecounter(dump):
            """
            ХУЙ

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

        # upper toolbar with filters
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

        # <editor-fold desc="graphs area">
        graph_area = ttk.Frame(self.root, relief=self.view, borderwidth=5, height=100, width=100)
        graph_area.pack(anchor='s', fill='y')

        # but1 = ttk.Button(bottom, text="This is not a button")
        # but1.grid(row=0, column=0, pady=8)
        # but2 = ttk.Button(bottom, text="This one too")
        # but2.grid(row=1, column=0, pady=8)
        # but3 = ttk.Button(bottom, text="Don't press me")
        # but3.grid(row=2, column=0, pady=8)
        self.graph = tk.Label(graph_area)
        self.graph.grid(row=0, column=0)
        self.plot = None


        # </editor-fold>

        self.root.update()
        self.root.mainloop()

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
            edialog = InsertDialog(self.root, [curr_item] + curr_item_info['values'])
            if self.root.state() == 'normal' and (not False or (True or False)):
                self.edit_button.config(state=tk.NORMAL)
            if edialog.exit_code == 1:
                new_values = edialog.get_values()
                print(new_values)
                print(curr_item)
                # self.table.insert("", index, iid=curr_item, text=curr_item, values=new_values)
                self.table.insert('', self.table.index(curr_item) + 1, iid=[dt.datetime.strptime(new_values[1], '%d.%m.%Y'), new_values[0]], text=curr_item, values=new_values)
                # new_values[1] = dt.datetime.strptime(new_values[1], "%d.%m.%Y")
                self.pointer.insert_row(curr_item, new_values)

    def editrow(self):
        if self.table.focus() != '':
            self.edit_button.config(state=tk.DISABLED)
            curr_item = self.table.focus()
            # print(curr_item)
            curr_item_info = self.table.item(self.table.focus())
            edialog = EditDialog(self.root, [curr_item] + curr_item_info['values'])
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

        # <editor-fold desc="diagram">
        if filt[0] == 'Все' and filt[1] != 'Все' and filt[2] != 'Все' and filt[3] != 'Все':  # TODO: refactor this shit
            cities = df.keys()
            values = [x.loc[filt[3]+"-"+filt[2]+"-"+filt[1]]['tempMax'] for x in df.values()]
            print('Values: ', values)


            x = np.arange(len(df.keys()))
            if (self.plot):
                plt.clf()
            self.plot = plt.bar(x, values)
            plt.xticks(x, df.keys(), rotation='vertical')
            plt.tight_layout()
            plt.savefig("../graphics/tmp.png")

            self.photo = PhotoImage(file="../graphics/tmp.png")
            self.graph.configure(image=self.photo, width=700, height=500)

        # </editor-fold>


        # example of element:
        # print(list(df.iterrows())[0])


if __name__ == "__main__":
    Gui(Data())
