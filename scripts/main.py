import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk
import pandas as pd


class Interface:
    def __init__(self):
        self.df = pd.read_csv("../data/weather.csv", encoding="utf-8", sep=";")
        root = tk.Tk()
        root.resizable(False, False)
        # upper toolbar with filters
        toolbar = ttk.Frame(root)
        toolbar.grid(column=0, row=0, columnspan=3)
        button1 = ttk.Button(toolbar, text="Insert row", command=lambda: self.insert(self.df))
        button1.grid(row=0, column=0, pady=8)
        # toolbar ends

        # table starts
        tableframe = ttk.Frame(root)
        tableframe.grid(column=0, row=1, columnspan=3)

        self.table = ttk.Treeview(tableframe, columns=list(range(7)))

        scroll = ttk.Scrollbar(tableframe, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)

        scroll.pack(side='right', fill='y')
        self.table.pack(side='left', fill='y')

        self.table.column(column="#0", width=50)
        self.table.heading(column="#0", text='index')

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
        editor = ttk.Frame(root)
        editor.grid(column=1, row=0, columnspan=3)
        button1 = ttk.Button(editor, text="Insert row", command=lambda: self.insert(self.df))
        button1.grid(row=0, column=0, pady=8)
        button2 = ttk.Button(editor, text="Delete row", command=lambda: self.delete(self.df))
        button2.grid(row=1, column=0, pady=8)

        button2 = ttk.Button(editor, text="Save to disk", command=lambda: self.save(self.df))
        button2.grid(row=2, column=0, pady=8)
        # editor panel ends
        self.view(self.df)

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


if __name__ == "__main__":
    interface = Interface()
