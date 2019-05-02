import tkinter.ttk as ttk
import tkinter
import pandas as pd

tk = tkinter.Tk()
tk.resizable(False, False)

button1 = ttk.Button(tk, text="Insert row")
button1.grid(row=0, column=0, pady=8)
button2 = ttk.Button(tk, text="Delete row")
button2.grid(row=0, column=1, pady=8)

button2 = ttk.Button(tk, text="Save to disk")
button2.grid(row=0, column=2, pady=8)

treeview =ttk.Treeview(tk, columns=list(range(7)))

treeview.grid(row=1, column=0, columnspan=3)

treeview.column(column="#0", width=120)
treeview.heading(column="#0", text='ID')

treeview.column(column=0, width=80)
treeview.heading(column=0, text='statName')

treeview.column(column=1, width=80)
treeview.heading(column=1, text='date')

treeview.column(column=2, width=80)
treeview.heading(column=2, text='tempMax')

treeview.column(column=3, width=80)
treeview.heading(column=3, text='tempMin')

treeview.column(column=4, width=80)
treeview.heading(column=4, text='press')

treeview.column(column=5, width=80)
treeview.heading(column=5, text='wind')

treeview.column(column=6, width=80)
treeview.heading(column=6, text='falls')

df = pd.read_csv("../data/weather.csv", encoding="utf-8", sep=";")
iter = df.iterrows()
for row in iter:
    rowdata = row[1].tolist()
    treeview.insert("", "end", text=rowdata[0], values=rowdata[1:])

tk.update()

tk.mainloop()
