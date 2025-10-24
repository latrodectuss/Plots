import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os


class DataPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Расширенный построитель графиков из CSV/Excel")
        self.root.geometry("1200x800")

        self.data_sets = {}
        self.current_data_key = None
        self.plot_settings = {}
        self.visible_plots = {}

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame, width=300, bg='#f0f0f0')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        load_frame = tk.LabelFrame(left_frame, text="Загрузка файлов", bg='#f0f0f0')
        load_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(load_frame, text="Разделитель CSV:", bg='#f0f0f0').pack(anchor=tk.W)
        self.separator_var = tk.StringVar(value=";")
        separator_entry = tk.Entry(load_frame, textvariable=self.separator_var, width=5)
        separator_entry.pack(anchor=tk.W, pady=2)

        tk.Label(load_frame, text="Кодировка:", bg='#f0f0f0').pack(anchor=tk.W)
        self.encoding_var = tk.StringVar(value="utf-8")
        encoding_combo = ttk.Combobox(load_frame, textvariable=self.encoding_var,
                                      values=["utf-8", "cp1251", "iso-8859-1", "windows-1251"], width=10)
        encoding_combo.pack(anchor=tk.W, pady=2)

        self.multi_file_var = tk.BooleanVar()
        multi_file_cb = tk.Checkbutton(load_frame, text="Загрузить несколько файлов",
                                       variable=self.multi_file_var, bg='#f0f0f0')
        multi_file_cb.pack(anchor=tk.W, pady=2)

        btn_frame = tk.Frame(load_frame, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X, pady=5)

        self.load_btn = tk.Button(btn_frame, text="Загрузить файл(ы)", command=self.load_files,
                                  bg='#a8d5ba', activebackground='#97c4a9', font=('Arial', 10))
        self.load_btn.pack(side=tk.LEFT, padx=2)

        self.clear_btn = tk.Button(btn_frame, text="Очистить все", command=self.clear_all,
                                   bg='#f4a4a4', activebackground='#e39393', font=('Arial', 10))
        self.clear_btn.pack(side=tk.LEFT, padx=2)

        self.data_frame = tk.LabelFrame(left_frame, text="Данные файлов", bg='#f0f0f0')
        self.data_frame.pack(fill=tk.X, padx=5, pady=5)

        self.file_listbox = tk.Listbox(self.data_frame, height=6)
        self.file_listbox.pack(fill=tk.X, pady=2)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        self.settings_frame = tk.LabelFrame(left_frame, text="Настройки графика", bg='#f0f0f0')
        self.settings_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(self.settings_frame, text="Тип графика:", bg='#f0f0f0').pack(anchor=tk.W)
        self.plot_type_var = tk.StringVar(value="auto")
        plot_types = [("Авто", "auto"), ("2D", "2d"), ("3D", "3d")]
        for text, value in plot_types:
            tk.Radiobutton(self.settings_frame, text=text, variable=self.plot_type_var,
                           value=value, bg='#f0f0f0').pack(anchor=tk.W)

        names_frame = tk.LabelFrame(self.settings_frame, text="Названия", bg='#f0f0f0')
        names_frame.pack(fill=tk.X, pady=5)

        tk.Label(names_frame, text="Заголовок:", bg='#f0f0f0').pack(anchor=tk.W)
        self.title_var = tk.StringVar(value="Графики данных")
        title_entry = tk.Entry(names_frame, textvariable=self.title_var)
        title_entry.pack(fill=tk.X, pady=2)

        tk.Label(names_frame, text="Ось X:", bg='#f0f0f0').pack(anchor=tk.W)
        self.xlabel_var = tk.StringVar()
        xlabel_entry = tk.Entry(names_frame, textvariable=self.xlabel_var)
        xlabel_entry.pack(fill=tk.X, pady=2)

        tk.Label(names_frame, text="Ось Y:", bg='#f0f0f0').pack(anchor=tk.W)
        self.ylabel_var = tk.StringVar()
        ylabel_entry = tk.Entry(names_frame, textvariable=self.ylabel_var)
        ylabel_entry.pack(fill=tk.X, pady=2)

        tk.Label(names_frame, text="Ось Z:", bg='#f0f0f0').pack(anchor=tk.W)
        self.zlabel_var = tk.StringVar()
        zlabel_entry = tk.Entry(names_frame, textvariable=self.zlabel_var)
        zlabel_entry.pack(fill=tk.X, pady=2)

        self.plots_frame = tk.LabelFrame(left_frame, text="Управление графиками", bg='#f0f0f0')
        self.plots_frame.pack(fill=tk.X, padx=5, pady=5)

        self.plots_list_frame = tk.Frame(self.plots_frame, bg='#f0f0f0')
        self.plots_list_frame.pack(fill=tk.X)

        action_frame = tk.Frame(left_frame, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        self.plot_btn = tk.Button(action_frame, text="Построить/Обновить", command=self.plot_data,
                                  state=tk.DISABLED, bg='#a8c6d5', activebackground='#97b5c4', font=('Arial', 10))
        self.plot_btn.pack(side=tk.LEFT, padx=2)

        self.save_btn = tk.Button(action_frame, text="Сохранить график", command=self.save_plot,
                                  state=tk.DISABLED, bg='#d5a8d1', activebackground='#c497c0', font=('Arial', 10))
        self.save_btn.pack(side=tk.LEFT, padx=2)

        plot_top_frame = tk.Frame(right_frame)
        plot_top_frame.pack(fill=tk.X)

        self.status_label = tk.Label(plot_top_frame, text="Загрузите файлы для построения графиков", fg="blue")
        self.status_label.pack(anchor=tk.W)

        self.plot_frame = tk.Frame(right_frame, bg='white')
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

        self.current_canvas = None

    def load_files(self):
        file_types = [
            ("Данные файлы", "*.csv *.xlsx *.xls"),
            ("CSV файлы", "*.csv"),
            ("Excel файлы", "*.xlsx *.xls"),
            ("Все файлы", "*.*")
        ]

        if self.multi_file_var.get():
            file_paths = filedialog.askopenfilenames(title="Выберите файлы с данными", filetypes=file_types)
        else:
            file_path = filedialog.askopenfilename(title="Выберите файл с данными", filetypes=file_types)
            file_paths = [file_path] if file_path else []

        for file_path in file_paths:
            if file_path and file_path not in self.data_sets:
                self.load_single_file(file_path)

        self.update_file_list()
        if self.data_sets:
            self.plot_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.NORMAL)

    def load_single_file(self, file_path):
        try:
            separator = self.separator_var.get()

            if file_path.endswith('.csv'):
                encodings_to_try = [self.encoding_var.get(), 'utf-8', 'cp1251', 'iso-8859-1', 'windows-1251']

                for encoding in encodings_to_try:
                    try:
                        data = pd.read_csv(file_path, delimiter=separator, encoding=encoding)
                        print(f"Файл успешно загружен с кодировкой: {encoding}")
                        break
                    except (UnicodeDecodeError, pd.errors.EmptyDataError) as e:
                        continue
                else:
                    try:
                        data = pd.read_csv(file_path, delimiter=separator)
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось загрузить CSV файл: {str(e)}")
                        return

            elif file_path.endswith(('.xlsx', '.xls')):
                data = pd.read_excel(file_path)
            else:
                return

            if data is not None and not data.empty:
                data = data.applymap(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)

                for col in data.columns:
                    try:
                        data[col] = pd.to_numeric(data[col], errors='ignore')
                    except:
                        pass

                key = os.path.basename(file_path)
                self.data_sets[key] = data
                self.visible_plots[key] = True

                self.plot_settings[key] = {
                    'color': f'C{len(self.data_sets) % 10}',
                    'marker': 'o',
                    'linewidth': 2,
                    'markersize': 6,
                    'show_line': True,
                    'show_points': True,
                    'label': key,
                    'x_col': data.columns[0] if len(data.columns) > 0 else '',
                    'y_col': data.columns[1] if len(data.columns) > 1 else '',
                    'z_col': data.columns[2] if len(data.columns) > 2 else ''
                }

                self.status_label.config(text=f"Загружено файлов: {len(self.data_sets)}", fg="green")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении файла {os.path.basename(file_path)}: {str(e)}")

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for key in self.data_sets.keys():
            self.file_listbox.insert(tk.END, key)

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            key = self.file_listbox.get(selection[0])
            self.current_data_key = key
            self.show_plot_settings(key)

    def show_plot_settings(self, key):
        for widget in self.plots_list_frame.winfo_children():
            widget.destroy()

        if key not in self.data_sets:
            return

        data = self.data_sets[key]
        settings = self.plot_settings[key]

        plot_frame = tk.LabelFrame(self.plots_list_frame, text=f"Настройки: {key}", bg='#f0f0f0')
        plot_frame.pack(fill=tk.X, pady=2)

        visible_var = tk.BooleanVar(value=self.visible_plots[key])
        visible_cb = tk.Checkbutton(plot_frame, text="Отображать", variable=visible_var,
                                    command=lambda: self.toggle_visibility(key, visible_var), bg='#f0f0f0')
        visible_cb.pack(anchor=tk.W)

        col_frame = tk.Frame(plot_frame, bg='#f0f0f0')
        col_frame.pack(fill=tk.X, pady=2)

        tk.Label(col_frame, text="X:", bg='#f0f0f0').pack(side=tk.LEFT)
        x_var = tk.StringVar(value=settings['x_col'])
        x_combo = ttk.Combobox(col_frame, textvariable=x_var, values=list(data.columns), width=10)
        x_combo.pack(side=tk.LEFT, padx=2)
        x_combo.bind('<<ComboboxSelected>>', lambda e: self.update_column_setting(key, 'x_col', x_var.get()))

        tk.Label(col_frame, text="Y:", bg='#f0f0f0').pack(side=tk.LEFT)
        y_var = tk.StringVar(value=settings['y_col'])
        y_combo = ttk.Combobox(col_frame, textvariable=y_var, values=list(data.columns), width=10)
        y_combo.pack(side=tk.LEFT, padx=2)
        y_combo.bind('<<ComboboxSelected>>', lambda e: self.update_column_setting(key, 'y_col', y_var.get()))

        if len(data.columns) >= 3:
            tk.Label(col_frame, text="Z:", bg='#f0f0f0').pack(side=tk.LEFT)
            z_var = tk.StringVar(value=settings['z_col'])
            z_combo = ttk.Combobox(col_frame, textvariable=z_var, values=list(data.columns), width=10)
            z_combo.pack(side=tk.LEFT, padx=2)
            z_combo.bind('<<ComboboxSelected>>', lambda e: self.update_column_setting(key, 'z_col', z_var.get()))

        display_frame = tk.Frame(plot_frame, bg='#f0f0f0')
        display_frame.pack(fill=tk.X, pady=2)

        line_var = tk.BooleanVar(value=settings['show_line'])
        line_cb = tk.Checkbutton(display_frame, text="Линия", variable=line_var,
                                 command=lambda: self.update_plot_setting(key, 'show_line', line_var.get()),
                                 bg='#f0f0f0')
        line_cb.pack(side=tk.LEFT)

        points_var = tk.BooleanVar(value=settings['show_points'])
        points_cb = tk.Checkbutton(display_frame, text="Точки", variable=points_var,
                                   command=lambda: self.update_plot_setting(key, 'show_points', points_var.get()),
                                   bg='#f0f0f0')
        points_cb.pack(side=tk.LEFT, padx=(10, 0))

        style_frame = tk.Frame(plot_frame, bg='#f0f0f0')
        style_frame.pack(fill=tk.X, pady=2)

        tk.Label(style_frame, text="Цвет:", bg='#f0f0f0').pack(side=tk.LEFT)
        color_var = tk.StringVar(value=settings['color'])
        color_combo = ttk.Combobox(style_frame, textvariable=color_var,
                                   values=['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive',
                                           'cyan', 'black'],
                                   width=8)
        color_combo.pack(side=tk.LEFT, padx=2)
        color_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot_setting(key, 'color', color_var.get()))

        tk.Label(style_frame, text="Толщ.линии:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(10, 0))
        linewidth_var = tk.StringVar(value=str(settings['linewidth']))
        linewidth_spin = tk.Spinbox(style_frame, from_=0.5, to=10, increment=0.5,
                                    textvariable=linewidth_var, width=5)
        linewidth_spin.pack(side=tk.LEFT, padx=2)
        linewidth_spin.bind('<FocusOut>',
                            lambda e: self.update_plot_setting(key, 'linewidth', float(linewidth_var.get())))

        tk.Label(style_frame, text="Разм.точек:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(10, 0))
        markersize_var = tk.StringVar(value=str(settings['markersize']))
        markersize_spin = tk.Spinbox(style_frame, from_=1, to=20, increment=1,
                                     textvariable=markersize_var, width=5)
        markersize_spin.pack(side=tk.LEFT, padx=2)
        markersize_spin.bind('<FocusOut>',
                             lambda e: self.update_plot_setting(key, 'markersize', float(markersize_var.get())))

        label_frame = tk.Frame(plot_frame, bg='#f0f0f0')
        label_frame.pack(fill=tk.X, pady=2)

        tk.Label(label_frame, text="Название:", bg='#f0f0f0').pack(side=tk.LEFT)
        label_var = tk.StringVar(value=settings['label'])
        label_entry = tk.Entry(label_frame, textvariable=label_var, width=20)
        label_entry.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        label_entry.bind('<FocusOut>', lambda e: self.update_plot_setting(key, 'label', label_var.get()))

    def toggle_visibility(self, key, var):
        self.visible_plots[key] = var.get()
        self.plot_data()

    def update_column_setting(self, key, col_type, value):
        self.plot_settings[key][col_type] = value
        self.plot_data()

    def update_plot_setting(self, key, setting, value):
        self.plot_settings[key][setting] = value
        self.plot_data()

    def plot_data(self):
        if not self.data_sets:
            return

        self.clear_plot()

        try:
            plot_type = self.plot_type_var.get()
            if plot_type == "auto":
                max_cols = max(len(self.data_sets[key].columns) for key in self.data_sets if self.visible_plots[key])
                plot_type = "3d" if max_cols >= 3 else "2d"

            if plot_type == "3d":
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111, projection='3d')
            else:
                fig, ax = plt.subplots(figsize=(10, 8))

            for key in self.data_sets:
                if not self.visible_plots[key]:
                    continue

                data = self.data_sets[key]
                settings = self.plot_settings[key]

                x_col = settings['x_col'] if settings['x_col'] in data.columns else data.columns[0]
                y_col = settings['y_col'] if settings['y_col'] in data.columns else data.columns[1] if len(
                    data.columns) > 1 else None
                z_col = settings['z_col'] if settings['z_col'] in data.columns else data.columns[2] if len(
                    data.columns) > 2 else None

                if y_col is None:
                    continue

                mask = ~data[x_col].isna() & ~data[y_col].isna()
                if z_col:
                    mask = mask & ~data[z_col].isna()

                x_data = data[x_col][mask]
                y_data = data[y_col][mask]
                z_data = data[z_col][mask] if z_col else None

                if len(x_data) == 0:
                    continue

                if plot_type == "3d" and z_col and len(z_data) > 0:
                    if settings['show_points']:
                        ax.scatter(x_data, y_data, z_data,
                                   c=settings['color'], marker=settings['marker'],
                                   s=settings['markersize'] * 20, label=settings['label'])
                else:
                    if settings['show_line'] and settings['show_points']:
                        ax.plot(x_data, y_data,
                                color=settings['color'], marker=settings['marker'],
                                linewidth=settings['linewidth'], markersize=settings['markersize'],
                                label=settings['label'])
                    elif settings['show_line']:
                        ax.plot(x_data, y_data,
                                color=settings['color'],
                                linewidth=settings['linewidth'],
                                label=settings['label'])
                    elif settings['show_points']:
                        ax.scatter(x_data, y_data,
                                   c=settings['color'], marker=settings['marker'],
                                   s=settings['markersize'] * 20, label=settings['label'])

            ax.set_xlabel(self.xlabel_var.get() or 'X')
            ax.set_ylabel(self.ylabel_var.get() or 'Y')
            if plot_type == "3d":
                ax.set_zlabel(self.zlabel_var.get() or 'Z')

            ax.set_title(self.title_var.get())
            ax.legend()
            ax.grid(True, alpha=0.3)

            canvas = FigureCanvasTkAgg(fig, self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.current_canvas = canvas
            self.status_label.config(text=f"Построено графиков: {sum(self.visible_plots.values())}", fg="darkgreen")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графиков: {str(e)}")

    def save_plot(self):
        if not self.current_canvas:
            return

        file_types = [
            ("PNG файлы", "*.png"),
            ("PDF файлы", "*.pdf"),
            ("SVG файлы", "*.svg"),
            ("Все файлы", "*.*")
        ]

        file_path = filedialog.asksaveasfilename(
            title="Сохранить график как...",
            filetypes=file_types,
            defaultextension=".png"
        )

        if file_path:
            try:
                self.current_canvas.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Успех", f"График сохранен как {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")

    def clear_plot(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        if self.current_canvas:
            self.current_canvas = None

        plt.close('all')

    def clear_all(self):
        self.data_sets.clear()
        self.plot_settings.clear()
        self.visible_plots.clear()
        self.current_data_key = None

        self.clear_plot()
        self.update_file_list()

        self.plot_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Загрузите файлы для построения графиков", fg="blue")

        for widget in self.plots_list_frame.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    app = DataPlotter(root)
    root.mainloop()


if __name__ == "__main__":
    main()