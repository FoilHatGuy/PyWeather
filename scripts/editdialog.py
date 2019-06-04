import tkinter as tk
import tkinter.ttk as ttk

g_padx = 8
g_pady = 8

class EditDialog(tk.Toplevel):
    def __init__(self, root, values):
        tk.Toplevel.__init__(self, root)

        self.geometry("+"+str(root.winfo_x()-25)+"+"+str(root.winfo_y()+150))
        self.resizable(False, False)

        # label_id = tk.Label(self, text="ID")
        # label_id.grid(column=0, row=0, padx=g_padx, pady=g_pady, sticky='w')

        label_city = tk.Label(self, text="City")
        label_city.grid(column=0, row=0, padx=g_padx, pady=g_pady, sticky='w')

        label_date = tk.Label(self, text="Date")
        label_date.grid(column=0, row=1, padx=g_padx, pady=g_pady, sticky='w')

        label_max_temp = tk.Label(self, text="Max temperature")
        label_max_temp.grid(column=0, row=2, padx=g_padx, pady=g_pady, sticky='w')

        label_min_temp = tk.Label(self, text="Min temperature")
        label_min_temp.grid(column=0, row=3, padx=g_padx, pady=g_pady, sticky='w')

        label_press = tk.Label(self, text="Pressure")
        label_press.grid(column=0, row=4, padx=g_padx, pady=g_pady, sticky='w')

        label_wind = tk.Label(self, text="Wind")
        label_wind.grid(column=0, row=5, padx=g_padx, pady=g_pady, sticky='w')

        label_falls = tk.Label(self, text="Falls")
        label_falls.grid(column=0, row=6, padx=g_padx, pady=g_pady, sticky='w')

        # self.text_id = tk.StringVar()
        # self.text_id.set(values[0])
        # self.entry_id = ttk.Entry(self, state='readonly', textvariable=self.text_id)
        # self.entry_id.grid(column=1, row=0, padx=g_padx)

        self.text_city = tk.StringVar()
        self.text_city.set(values[1])
        self.entry_city = ttk.Entry(self, state="readonly", textvariable=self.text_city, width=30)
        self.entry_city.grid(column=1, row=0, padx=g_padx, columnspan=2)

        self.text_date = tk.StringVar()
        self.text_date.set(values[2])
        self.entry_date = ttk.Entry(self, state="readonly", textvariable=self.text_date, width=30)
        self.entry_date.grid(column=1, row=1, padx=g_padx, columnspan=2)

        self.text_max_temp = tk.StringVar()
        self.text_max_temp.set(values[3])
        self.entry_max_temp = ttk.Entry(self, textvariable=self.text_max_temp, width=30)
        self.entry_max_temp.grid(column=1, row=2, padx=g_padx, columnspan=2)

        self.text_min_temp = tk.StringVar()
        self.text_min_temp.set(values[4])
        self.entry_min_temp = ttk.Entry(self, textvariable=self.text_min_temp, width=30)
        self.entry_min_temp.grid(column=1, row=3, padx=g_padx, columnspan=2)

        self.text_press = tk.StringVar()
        self.text_press.set(values[5])
        self.entry_press = ttk.Entry(self, textvariable=self.text_press, width=30)
        self.entry_press.grid(column=1, row=4, padx=g_padx, columnspan=2)

        self.text_wind = tk.StringVar()
        self.text_wind.set(str(values[6]))
        self.entry_wind = ttk.Entry(self, textvariable=self.text_wind, width=30)
        self.entry_wind.grid(column=1, row=5, padx=g_padx, columnspan=2)

        self.text_falls = tk.StringVar()
        self.text_falls.set(str(values[7]))
        self.entry_falls = ttk.Entry(self, textvariable=self.text_falls, width=30)
        self.entry_falls.grid(column=1, row=6, padx=g_padx, columnspan=2)

        self.ok_button = ttk.Button(self, text="OK", width=10, command=self.on_ok_button)
        self.ok_button.grid(column=1, row=7, padx=g_padx, pady=g_pady)

        self.cancel_button = ttk.Button(self, text="Cancel", width=10, command=self.on_cancel_button)
        self.cancel_button.grid(column=2, row=7, padx=g_padx, pady=g_pady)

        self.exit_code = 0

        self.transient(root)
        self.wait_window(self)

    def on_ok_button(self):
        self.exit_code = 1
        self.destroy()

    def on_cancel_button(self):
        self.destroy()

    def get_values(self):
        return [self.text_city.get(), self.text_date.get(), self.text_max_temp.get(), self.text_min_temp.get(),
                self.text_press.get(), int(self.text_wind.get()), int(self.text_falls.get())]
