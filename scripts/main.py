import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk

import pandas as pd


class Data:
    def __init__(self):
        self.dataframe = pd.read_csv("../data/weather.csv", encoding="utf-8", sep=";")
        # self.getdata(self.dataframe)

    def getdata(self, filters):
        if filters == 'all':
            return self.dataframe


class Gui:
    def __init__(self, data):
        self.pointer = data
        self.df = self.askdata()
        root = tk.Tk()
        # root.resizable(False, False)

        top = ttk.Frame(root, relief='groove', borderwidth=5)
        top.pack(anchor='n')

        top_left = ttk.Frame(top, relief='groove', borderwidth=5)
        top_left.grid(column=0, row=0)
        # upper toolbar with filters
        toolbar = ttk.Frame(top_left, relief='groove', borderwidth=5)
        toolbar.grid(row=0, column=0, columnspan=3)
        button1 = ttk.Button(toolbar, text="Insert row", command=lambda: self.insert(self.df))
        button1.grid(row=0, column=0, pady=8)
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

        button2 = ttk.Button(bottom, text="Sa1ve to disk", command=lambda: self.save(self.df))
        button2.grid(row=2, column=0, pady=8)
        # /canvas

        root.update()
        root.mainloop()

    @staticmethod
    def save(data):
        route = fd.asksaveasfile(initialdir="../data/", title="Select file", defaultextension='.csv',
                                 filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if route is not None:
            data.to_csv(route, encoding="utf-8", sep=";")

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
