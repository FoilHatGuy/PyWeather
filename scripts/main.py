import tkinter.filedialog as fd
import tkinter.ttk as ttk
import tkinter.messagebox as msg
import tkinter as tk
import pandas as pd

df = pd.read_csv("../data/weather.csv", encoding="utf-8", sep=";")


def save(data):
    route = fd.asksaveasfile(initialdir="../data/", title="Select file", defaultextension='.csv',
                             filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    if route is not None:
        data.to_csv(route, encoding="utf-8", sep=";")


def insert(data):
    pass


def delete(data):
    pass


root = tk.Tk()
root.resizable(False, False)

button1 = ttk.Button(root, text="Insert row", command=lambda: insert(df))
button1.grid(row=0, column=0, pady=8)
button2 = ttk.Button(root, text="Delete row", command=lambda: delete(df))
button2.grid(row=0, column=1, pady=8)

button2 = ttk.Button(root, text="Save to disk", command=lambda: save(df))
button2.grid(row=0, column=2, pady=8)

tableframe = ttk.Frame(root)
tableframe.grid(row=1, column=0, columnspan=3)

table = ttk.Treeview(tableframe, columns=list(range(7)))

scroll = ttk.Scrollbar(tableframe, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scroll.set)

scroll.pack(side='right', fill='y')
table.pack(side='left', fill='y')

table.column(column="#0", width=120)
table.heading(column="#0", text='ID')

table.column(column=0, width=80)
table.heading(column=0, text='statName')

table.column(column=1, width=80)
table.heading(column=1, text='date')

table.column(column=2, width=80)
table.heading(column=2, text='tempMax')

table.column(column=3, width=80)
table.heading(column=3, text='tempMin')

table.column(column=4, width=80)
table.heading(column=4, text='press')

table.column(column=5, width=80)
table.heading(column=5, text='wind')

table.column(column=6, width=80)
table.heading(column=6, text='falls')

for row in df.iterrows():
    rowdata = row[1].tolist()
    table.insert("", "end", text=rowdata[0], values=rowdata[1:])

print(list(df.iterrows())[0])

root.update()

root.mainloop()
