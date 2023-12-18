from tinydb import TinyDB, Query
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import re
from datetime import datetime
import shutil
import pandas as pd


class DatabaseManager:
    def __init__(self, file_path):
        self.file_path = file_path
        if os.path.exists(self.file_path):
            self.db = TinyDB(self.file_path)
        else:
            print("База данных по указанному пути не существует.")
            self.db = None

    def create_new_database(self):
        if not os.path.exists(self.file_path):
            self.db = TinyDB(self.file_path)
            # Создание пустой таблицы с указанием всех полей
            self.db.insert({
                'order_id': None,
                'customer_id': None,
                'amount': None,
                'date': None,
                'status': None,
                'delivery_address': None
            })
            print(f"Создана новая база данных по пути {self.file_path}.")
        else:
            print("База данных с таким именем уже существует в указанной директории.")

    def add_record(self, order_id, customer_id, amount, date, status, delivery_address):
        if self.db:
            Order = Query()
            if not self.db.contains(Order.order_id == order_id):
                self.db.insert({
                    'order_id': order_id,
                    'customer_id': customer_id,
                    'amount': amount,
                    'date': date,
                    'status': status,
                    'delivery_address': delivery_address
                })
                print("Запись успешно добавлена.")
            else:
                print("Запись с такими ключевыми полями уже существует.")
        else:
            print("База данных не открыта.")

    def delete_record_by_field(self, field_name, value):
        if self.db:
            Record = Query()
            if field_name in ['order_id', 'customer_id']:  
                self.db.remove(Record[field_name] == int(value))  
                print("Записи успешно удалены.")
            elif field_name in ['date', 'status', 'delivery_address']: 
                self.db.remove(Record[field_name] == str(value)) 
                print("Записи успешно удалены.")
            elif field_name in ['amount']:  
                self.db.remove(Record[field_name] == float(value)) 
                print("Записи успешно удалены.")
            else:
                print("Указано некорректное имя поля.")
        else:
            print("База данных не открыта.")
    
    def clear_all_records(self):
        if self.db:
            self.db.truncate()
            print("База данных очищена.")
        else:
            print("База данных не открыта.")

    def search_by_field(self, field_name, value):
        if self.db:
            Record = Query()
            if field_name in ['order_id', 'customer_id']:  
                results = self.db.search(Record[field_name] == int(value))  
            elif field_name in ['date', 'status', 'delivery_address']: 
                results = self.db.search(Record[field_name] == str(value))  
            elif field_name in ['amount']:  
                results = self.db.search(Record[field_name] == float(value))  
            else:
                print("Указано некорректное имя поля.")
                return None

            if results:
                print("Результаты поиска:")
                for result in results:
                    print(result)
                return results 
            else:
                print("Записей с указанным значением не найдено.")
                return []
        else:
            print("База данных не открыта.")
            return None


    
    def edit_record(self, field_name, old_value, new_values):
        if self.db:
            Record = Query()
            results = []
            if field_name in ['order_id', 'customer_id']:  
                results = self.db.search(Record[field_name] == int(old_value))  
            elif field_name in ['date', 'status', 'delivery_address']: 
                results = self.db.search(Record[field_name] == str(old_value))  
            elif field_name in ['amount']:  
                results = self.db.search(Record[field_name] == float(old_value))  
            else:
                print("Указано некорректное имя поля.")
                return False

            if results:
                for result in results:
                    update_values = {key: value for key, value in new_values.items() if value != ''}
                    self.db.update(update_values, Record[field_name] == result[field_name])
                return True
            else:
                print("Записей с указанным значением не найдено.")
                return False
        else:
            print("База данных не открыта.")
            return False
        
    def create_backup(self, backup_file):
        try:
            if os.path.exists(backup_file):
                os.remove(backup_file)
            shutil.copy2(self.file_path, backup_file)
            print(f"Создана резервная копия: {backup_file}")
            return True
        except Exception as e:
            print(f"Ошибка при создании резервной копии: {e}")
            return False
        
    def close_database(self):
        if self.db:
            self.db.close()
            print("База данных закрыта.")
            self.db = None

    def restore_from_backup(self, backup_file):
        try:
            self.close_database()  # Закрытие базы данных перед восстановлением из копии
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, self.file_path)
                print(f"База данных восстановлена из резервной копии: {backup_file}")
                self.db = TinyDB(self.file_path)  # После восстановления открываем базу данных снова
                return True
            else:
                print(f"Файл резервной копии не найден: {backup_file}")
                return False
        except Exception as e:
            print(f"Ошибка при восстановлении из резервной копии: {e}")
            return False
        
    def export_to_csv(self, csv_file):
        if self.db:
            try:
                data = self.db.all()
                df = pd.DataFrame(data)
                df.to_csv(csv_file, index=False)
                print(f"Данные экспортированы в CSV: {csv_file}")
                return True
            except Exception as e:
                print(f"Ошибка при экспорте данных в CSV: {e}")
                return False
        else:
            print("База данных не открыта.")
            return False

    def export_to_xlsx(self, xlsx_file):
        if self.db:
            try:
                data = self.db.all()
                df = pd.DataFrame(data)
                df.to_excel(xlsx_file, index=False)
                print(f"Данные экспортированы в XLSX: {xlsx_file}")
                return True
            except Exception as e:
                print(f"Ошибка при экспорте данных в XLSX: {e}")
                return False
        else:
            print("База данных не открыта.")
            return False
        
    def get_all_records(self):
        if self.db:
            return self.db.all()
        else:
            print("База данных не открыта.")
            return []

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Управление базой данных")

        self.db_manager = None
        self.create_select_window()


    def create_select_window(self):
        self.open_database_button = tk.Button(self.master, text="Открыть базу данных", command=self.open_database)
        self.open_database_button.pack()

        self.create_database_button = tk.Button(self.master, text="Создать новую базу данных", command=self.create_database)
        self.create_database_button.pack()

    def open_database(self):
        file_path = filedialog.askopenfilename(title="Выберите файл базы данных", filetypes=[("JSON files", "*.json")])
        if file_path:
            self.db_manager = DatabaseManager(file_path)
            self.destroy_select_window()
            self.create_interaction_window()
            all_records = self.db_manager.get_all_records()
            self.display_search_results(all_records)

    def create_database(self):
        directory_path = filedialog.askdirectory(title="Выберите директорию для новой базы данных")
        if directory_path:
            file_path = filedialog.asksaveasfilename(
                initialdir=directory_path, defaultextension=".json", filetypes=[("JSON files", "*.json")]
            )
            if file_path:
                self.db_manager = DatabaseManager(file_path)
                self.db_manager.create_new_database()
                self.destroy_select_window()
                self.create_interaction_window()

    def destroy_select_window(self):
        self.open_database_button.destroy()
        self.create_database_button.destroy()

    def create_interaction_window(self):
        fields = ['order_id', 'customer_id', 'amount', 'date', 'status', 'delivery_address']
        tk.Label(self.master, text="Order ID:").grid(row=1, column=1, sticky=tk.E)
        self.order_id_entry = tk.Entry(self.master)
        self.order_id_entry.grid(row=1, column=2, pady=5)

        tk.Label(self.master, text="Customer ID:").grid(row=2, column=1, sticky=tk.E)
        self.customer_id_entry = tk.Entry(self.master)
        self.customer_id_entry.grid(row=2, column=2, pady=5)

        tk.Label(self.master, text="Amount:").grid(row=3, column=1, sticky=tk.E)
        self.amount_entry = tk.Entry(self.master)
        self.amount_entry.grid(row=3, column=2, pady=5)

        tk.Label(self.master, text="Date:").grid(row=4, column=1, sticky=tk.E)
        self.date_entry = tk.Entry(self.master)
        self.date_entry.grid(row=4, column=2, pady=5)

        tk.Label(self.master, text="Status:").grid(row=5, column=1, sticky=tk.E)
        self.status_entry = tk.Entry(self.master)
        self.status_entry.grid(row=5, column=2, pady=5)

        tk.Label(self.master, text="Delivery Address:").grid(row=6, column=1, sticky=tk.E)
        self.delivery_address_entry = tk.Entry(self.master)
        self.delivery_address_entry.grid(row=6, column=2, pady=5)

        # Кнопка для добавления записи
        self.add_record_button = tk.Button(self.master, text="Добавить запись", command=self.add_record)
        self.add_record_button.grid(row=7, column=1, columnspan=2, pady=10)

        tk.Label(self.master, text="Поле:").grid(row=1, column=3, sticky=tk.E)
        self.delete_field_combo = ttk.Combobox(self.master, values=fields)
        self.delete_field_combo.grid(row=1, column=4, pady=5)

        tk.Label(self.master, text="Значение:").grid(row=2, column=3, sticky=tk.E)
        self.delete_value_entry = tk.Entry(self.master)
        self.delete_value_entry.grid(row=2, column=4, pady=5)

        # Кнопка для удаления записи
        self.delete_record_button = tk.Button(self.master, text="Удалить записи", command=self.delete_record)
        self.delete_record_button.grid(row=3, column=3, columnspan=2, pady=10)

        tk.Label(self.master, text="Поле:").grid(row=12, column=1, sticky=tk.E)
        self.search_field_combo = ttk.Combobox(self.master, values=fields)
        self.search_field_combo.grid(row=12, column=2, pady=5)

        tk.Label(self.master, text="Значение:").grid(row=13, column=1, sticky=tk.E)
        self.search_value_entry = ttk.Entry(self.master)
        self.search_value_entry.grid(row=13, column=2, pady=5)

        # Кнопка для поиска записи
        self.search_record_button = tk.Button(self.master, text="Поиск записей", command=self.search_record)
        self.search_record_button.grid(row=13, column=3, pady=0)

        tk.Label(self.master, text="Поле для поиска:").grid(row=1, column=5, sticky=tk.E)
        self.edit_field_combo = ttk.Combobox(self.master, values=fields)
        self.edit_field_combo.grid(row=1, column=6, pady=5)

        tk.Label(self.master, text="Значение для поиска:").grid(row=2, column=5, sticky=tk.E)
        self.old_value_entry = ttk.Entry(self.master)
        self.old_value_entry.grid(row=2, column=6, pady=5)

        # Поля для ввода новых значений
        tk.Label(self.master, text="Новые значения:").grid(row=3, column=5, columnspan=2, pady=5)

        tk.Label(self.master, text="Order ID:").grid(row=4, column=5, sticky=tk.E)
        self.new_order_id_entry = ttk.Entry(self.master)
        self.new_order_id_entry.grid(row=4, column=6, pady=5)

        tk.Label(self.master, text="Customer ID:").grid(row=5, column=5, sticky=tk.E)
        self.new_customer_id_entry = ttk.Entry(self.master)
        self.new_customer_id_entry.grid(row=5, column=6, pady=5)

        tk.Label(self.master, text="Amount:").grid(row=6, column=5, sticky=tk.E)
        self.new_amount_entry = ttk.Entry(self.master)
        self.new_amount_entry.grid(row=6, column=6, pady=5)

        tk.Label(self.master, text="Date:").grid(row=7, column=5, sticky=tk.E)
        self.new_date_entry = ttk.Entry(self.master)
        self.new_date_entry.grid(row=7, column=6, pady=5)

        tk.Label(self.master, text="Status:").grid(row=8, column=5, sticky=tk.E)
        self.new_status_entry = ttk.Entry(self.master)
        self.new_status_entry.grid(row=8, column=6, pady=5)

        tk.Label(self.master, text="Delivery Address:").grid(row=9, column=5, sticky=tk.E)
        self.new_delivery_address_entry = ttk.Entry(self.master)
        self.new_delivery_address_entry.grid(row=9, column=6, pady=5)

        # Кнопка для редактирования записи
        self.edit_record_button = tk.Button(self.master, text="Редактировать записи", command=self.edit_record)
        self.edit_record_button.grid(row=10, column=5, columnspan=2, pady=10)

        self.create_backup_button = tk.Button(self.master, text="Создать резервную копию", command=self.create_backup)
        self.create_backup_button.grid(row=15, column=1, columnspan=2, pady=10)

        # Кнопка для восстановления из резервной копии
        self.restore_backup_button = tk.Button(self.master, text="Восстановить из копии", command=self.restore_backup)
        self.restore_backup_button.grid(row=16, column=1, columnspan=2, pady=10)

        self.export_csv_button = tk.Button(self.master, text="Экспорт в CSV", command=self.export_to_csv)
        self.export_csv_button.grid(row=15, column=3, columnspan=2, pady=10)\
        
        self.tree_frame = tk.Frame(self.master)
        self.tree_frame.grid(row=14, column=1, columnspan=8)

        self.show_all_records_button = tk.Button(self.master, text="Показать все записи", command=self.show_all_records)
        self.show_all_records_button.grid(row=13, column=5, columnspan=2, pady=10)

        self.clear_database_button = tk.Button(self.master, text="Очистить базу данных", command=self.clear_database)
        self.clear_database_button.grid(row=15, column=5, columnspan=2, pady=10)


        self.tree_scroll_y = tk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = tk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)

        self.tree = None
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        

    def add_record(self):
        try:
            order_id = self.order_id_entry.get().strip()
            customer_id = self.customer_id_entry.get().strip()
            amount = self.amount_entry.get().strip()
            date = self.date_entry.get().strip()
            status = self.status_entry.get().strip()
            delivery_address = self.delivery_address_entry.get().strip()

            # Проверка и преобразование типов
            if order_id.isdigit():
                order_id = int(order_id)
            else:
                raise ValueError("Некорректный формат Order ID.")

            if customer_id.isdigit():
                customer_id = int(customer_id)
            else:
                raise ValueError("Некорректный формат Customer ID.")

            if amount.replace('.', '', 1).isdigit():  # Проверка на float
                amount = float(amount)
            else:
                raise ValueError("Некорректный формат Amount.")

            # Проверка формата даты
            if date:
                if re.match(r'\d{4}-\d{2}-\d{2}', date):
                    try:
                        date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
                    except ValueError:
                        raise ValueError("Некорректный формат даты. Используйте YYYY-MM-DD.")
                else:
                    raise ValueError("Некорректный формат даты. Используйте YYYY-MM-DD.")

            # Добавьте здесь другие проверки для остальных полей при необходимости

            if self.db_manager:
                self.db_manager.add_record(order_id, customer_id, amount, date, status, delivery_address)
                messagebox.showinfo("Добавление записи", "Запись успешно добавлена.")
            else:
                messagebox.showwarning("Добавление записи", "База данных не открыта.")

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))


    def delete_record(self):
        field = self.delete_field_combo.get()
        value = self.delete_value_entry.get()

        if self.db_manager:
            self.db_manager.delete_record_by_field(field, value)
            messagebox.showinfo("Удаление записей", "Записи успешно удалены.")
        else:
            messagebox.showwarning("Удаление записей", "Записи не найдены.")
        pass

    def search_record(self):
        field = self.search_field_combo.get()
        value = self.search_value_entry.get()

        if self.db_manager:
            results = self.db_manager.search_by_field(field, value)
            if results:
                self.display_search_results(results)
            else:
                messagebox.showinfo("Результаты поиска", "Записей с указанным значением не найдено.")
        else:
            messagebox.showwarning("Поиск записей", "База данных не открыта.")

    def display_search_results(self, results):
        if self.tree:
            self.tree.delete(*self.tree.get_children()) 
        if self.tree:
            self.tree.destroy() 

        columns = list(results[0].keys())

        self.tree = ttk.Treeview(
            self.tree_frame, columns=columns, show='headings',
            yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set
        )

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        for row in results:
            self.tree.insert("", "end", values=list(row.values()))

        self.tree.pack(fill='both', expand=True)
    
    def show_all_records(self):
        if self.db_manager:
            all_records = self.db_manager.get_all_records()
            self.display_search_results(all_records)
        else:
            messagebox.showwarning("Показать все записи", "База данных не открыта.")

        
    def edit_record(self):
        field_name = self.edit_field_combo.get()
        old_value = self.old_value_entry.get()

        new_order_id = self.new_order_id_entry.get().strip()
        new_customer_id = self.new_customer_id_entry.get().strip()
        new_amount = self.new_amount_entry.get().strip()
        new_date = self.new_date_entry.get().strip()
        new_status = self.new_status_entry.get().strip()
        new_delivery_address = self.new_delivery_address_entry.get().strip()

        # Проверка и преобразование типов
        try:
            new_order_id = int(new_order_id) if new_order_id else ''
            new_customer_id = int(new_customer_id) if new_customer_id else ''
            new_amount = float(new_amount) if new_amount else ''
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат ввода.")
            return False

        # Обработка формата даты
        if new_date:
            if re.match(r'\d{4}-\d{2}-\d{2}', new_date):
                try:
                    new_date = datetime.strptime(new_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте YYYY-MM-DD.")
                    return False
            else:
                messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте YYYY-MM-DD.")
                return False

        new_values = {
            'order_id': new_order_id,
            'customer_id': new_customer_id,
            'amount': new_amount,
            'date': new_date,
            'status': new_status,
            'delivery_address': new_delivery_address
        }

        if self.db_manager:
            success = self.db_manager.edit_record(field_name, old_value, new_values)
            if success:
                messagebox.showinfo("Редактирование записей", "Записи успешно отредактированы.")
            else:
                messagebox.showerror("Редактирование записей", "Ошибка при редактировании записей.")
        else:
            messagebox.showwarning("Редактирование записей", "База данных не открыта.")

    def create_backup(self):
        if self.db_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json", filetypes=[("JSON files", "*.json")], initialdir=os.getcwd()
            )
            if file_path:
                success = self.db_manager.create_backup(file_path)
                if success:
                    messagebox.showinfo("Резервная копия", "Резервная копия успешно создана.")
                else:
                    messagebox.showerror("Резервная копия", "Ошибка при создании резервной копии.")
        else:
            messagebox.showwarning("Резервная копия", "База данных не открыта.")

    def restore_backup(self):
        if self.db_manager:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")], initialdir=os.getcwd()
            )
            if file_path:
                success = self.db_manager.restore_from_backup(file_path)
                if success:
                    messagebox.showinfo("Восстановление из копии", "База данных успешно восстановлена из копии.")
                else:
                    messagebox.showerror("Восстановление из копии", "Ошибка при восстановлении из копии.")
        else:
            messagebox.showwarning("Восстановление из копии", "База данных не открыта.")
    
    def export_to_csv(self):
        if self.db_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialdir=os.getcwd()
            )
            if file_path:
                success = self.db_manager.export_to_csv(file_path)
                if success:
                    messagebox.showinfo("Экспорт в CSV", "Данные успешно экспортированы в CSV.")
                else:
                    messagebox.showerror("Экспорт в CSV", "Ошибка при экспорте данных в CSV.")
        else:
            messagebox.showwarning("Экспорт в CSV", "База данных не открыта.")

    def clear_database(self):
        if self.db_manager:
            self.db_manager.clear_all_records()
        else:
            messagebox.showwarning("Очистить базу данных", "База данных не открыта.")


def run_app():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()
