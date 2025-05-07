
import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Настройка подключения к БД
def get_db_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="impala67",
        host="localhost",
        port="5432"
    )

# Добавление клиента
def submit_order():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT setval(pg_get_serial_sequence('client', 'client_id'), GREATEST((SELECT MAX(client_id) FROM client), 10000), true);")

        cur.execute("""
            INSERT INTO client (first_name, last_name, phone, address)
            VALUES (%s, %s, %s, %s)
        """, (entry_first.get(), entry_last.get(), entry_phone.get(), entry_address.get()))

        conn.commit()
        messagebox.showinfo("Успех", "Клиент успешно добавлен!")

        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Добавление отзыва
def submit_feedback():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT setval(pg_get_serial_sequence('feedback', 'feedback_id'), GREATEST((SELECT MAX(feedback_id) FROM feedback), 10000), true);")

        cur.execute(
            "INSERT INTO feedback (client_id, rating, comm) VALUES (%s, %s, %s)",
            (entry_client_id.get(), entry_rating.get(), entry_comment.get())
        )
        conn.commit()
        messagebox.showinfo("Успех", "Отзыв добавлен!")
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Обновление записи
def update_record(table, pk_column, pk_value, column, new_value):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"UPDATE {table} SET {column} = %s WHERE {pk_column} = %s", (new_value, pk_value))
        conn.commit()
        messagebox.showinfo("Успех", f"{table.capitalize()} обновлён!")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
    finally:
        cur.close()
        conn.close()

# Удаление записи
def delete_record(table, pk_column, pk_value):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM {table} WHERE {pk_column} = %s", (pk_value,))
        conn.commit()
        messagebox.showinfo("Удалено", f"Запись удалена из {table}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
    finally:
        cur.close()
        conn.close()

# Добавление запроса для поиска отзывов с оценкой выше заданной
def search_feedback_above_rating():
    try:
        rating_threshold = simpledialog.askfloat("Введите оценку", "Введите минимальную оценку:")
        if rating_threshold is None:
            return

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT c.first_name, c.last_name, f.rating, f.comm
            FROM client c
            JOIN feedback f ON c.client_id = f.client_id
            WHERE f.rating >= %s
            ORDER BY f.rating DESC;
        """, (rating_threshold,))

        results = cur.fetchall()

        # Создание нового окна для отображения результатов
        feedback_window = tk.Toplevel(root)
        feedback_window.title(f"Отзывы с оценкой выше {rating_threshold}")

        tree_feedback = ttk.Treeview(feedback_window, columns=("№", "Имя", "Фамилия", "Оценка", "Комментарий"),
                                     show="headings")
        tree_feedback.heading("#1", text="№")
        tree_feedback.heading("#2", text="Имя")
        tree_feedback.heading("#3", text="Фамилия")
        tree_feedback.heading("#4", text="Оценка")
        tree_feedback.heading("#5", text="Комментарий")
        tree_feedback.pack(fill="both", expand=True, side="left")

        # Вертикальный ползунок
        scrollbar_feedback = ttk.Scrollbar(feedback_window, orient="vertical", command=tree_feedback.yview)
        scrollbar_feedback.pack(side="right", fill="y")
        tree_feedback.config(yscrollcommand=scrollbar_feedback.set)

        # Заполнение таблицы результатами
        for index, row in enumerate(results, start=1):
            tree_feedback.insert("", "end", values=(index, *row))

        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


# Добавление запроса для подсчета количества отзывов у каждого клиента
def get_feedback_count_for_clients():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT c.first_name, c.last_name, COUNT(f.feedback_id) as feedback_count
            FROM client c
            LEFT JOIN feedback f ON c.client_id = f.client_id
            GROUP BY c.first_name, c.last_name
            ORDER BY feedback_count DESC;
        """)

        results = cur.fetchall()

        # Создание нового окна для отображения количества отзывов
        count_window = tk.Toplevel(root)
        count_window.title("Количество отзывов у каждого клиента")

        tree_count = ttk.Treeview(count_window, columns=("№", "Имя", "Фамилия", "Количество отзывов"), show="headings")
        tree_count.heading("#1", text="№")
        tree_count.heading("#2", text="Имя")
        tree_count.heading("#3", text="Фамилия")
        tree_count.heading("#4", text="Количество отзывов")
        tree_count.pack(fill="both", expand=True, side="left")

        # Вертикальный ползунок
        scrollbar_count = ttk.Scrollbar(count_window, orient="vertical", command=tree_count.yview)
        scrollbar_count.pack(side="right", fill="y")
        tree_count.config(yscrollcommand=scrollbar_count.set)

        # Заполнение таблицы результатами
        for index, row in enumerate(results, start=1):
            tree_count.insert("", "end", values=(index, *row))

        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


# Админ-панель с вкладками
def open_admin():
    password = simpledialog.askstring("Пароль", "Введите пароль администратора:", show="*")
    if password != "impala67":
        messagebox.showerror("Доступ запрещён", "Неверный пароль")
        return

    admin = tk.Toplevel(root)
    admin.title("Админ-панель")

    notebook = ttk.Notebook(admin)
    notebook.pack(fill="both", expand=True)

    # --- Вкладка Клиенты ---
    frame_client = ttk.Frame(notebook)
    notebook.add(frame_client, text="Клиенты")

    # Поиск по ключевым словам
    search_entry_client = tk.Entry(frame_client)
    search_entry_client.pack()
    tk.Button(frame_client, text="Поиск", command=lambda: search_client(search_entry_client.get())).pack()

    tree_client = ttk.Treeview(frame_client, columns=("ID", "Имя", "Фамилия", "Телефон", "Адрес"), show="headings")
    for col in tree_client["columns"]:
        tree_client.heading(col, text=col)
    tree_client.pack(fill="both", expand=True, side="left")

    scrollbar_client = ttk.Scrollbar(frame_client, orient="vertical", command=tree_client.yview)
    scrollbar_client.pack(side="right", fill="y")
    tree_client.config(yscrollcommand=scrollbar_client.set)

    def refresh_client_data():
        for row in tree_client.get_children():
            tree_client.delete(row)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT client_id, first_name, last_name, phone, address FROM client ORDER BY client_id")
        for row in cur.fetchall():
            tree_client.insert("", "end", values=row)
        cur.close()
        conn.close()

    def search_client(keyword):
        keyword = keyword.lower()
        for row in tree_client.get_children():
            tree_client.delete(row)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT client_id, first_name, last_name, phone, address FROM client ORDER BY client_id")
        for row in cur.fetchall():
            if any(keyword in str(cell).lower() for cell in row):
                tree_client.insert("", "end", values=row)
        cur.close()
        conn.close()

    refresh_client_data()

    def edit_client():
        selected = tree_client.selection()
        if not selected:
            return
        values = tree_client.item(selected[0])['values']
        column = simpledialog.askstring("Столбец", "Что редактировать? (first_name, last_name, phone, address)")
        new_value = simpledialog.askstring("Новое значение", "Введите новое значение:")
        update_record("client", "client_id", values[0], column, new_value)
        refresh_client_data()

    def delete_client():
        selected = tree_client.selection()
        if not selected:
            return
        values = tree_client.item(selected[0])['values']
        delete_record("client", "client_id", values[0])
        tree_client.delete(selected[0])

    tk.Button(frame_client, text="Редактировать", command=edit_client).pack()
    tk.Button(frame_client, text="Удалить", command=delete_client).pack()

    # --- Вкладка Отзывы ---
    frame_feedback = ttk.Frame(notebook)
    notebook.add(frame_feedback, text="Отзывы")

    search_entry_feedback = tk.Entry(frame_feedback)
    search_entry_feedback.pack()
    tk.Button(frame_feedback, text="Поиск", command=lambda: search_feedback(search_entry_feedback.get())).pack()

    tree_feedback = ttk.Treeview(
        frame_feedback,
        columns=("ID", "client_id", "Имя", "Фамилия", "Оценка", "Комментарий"),
        show="headings"
    )
    for col in tree_feedback["columns"]:
        tree_feedback.heading(col, text=col)
    tree_feedback.pack(fill="both", expand=True, side="left")

    scrollbar_feedback = ttk.Scrollbar(frame_feedback, orient="vertical", command=tree_feedback.yview)
    scrollbar_feedback.pack(side="right", fill="y")
    tree_feedback.config(yscrollcommand=scrollbar_feedback.set)

    def refresh_feedback_data():
        for row in tree_feedback.get_children():
            tree_feedback.delete(row)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT f.feedback_id, f.client_id, c.first_name, c.last_name, f.rating, f.comm
            FROM feedback f
            JOIN client c ON f.client_id = c.client_id
            ORDER BY f.feedback_id
        """)
        for row in cur.fetchall():
            tree_feedback.insert("", "end", values=row)
        cur.close()
        conn.close()

    def search_feedback(keyword):
        keyword = keyword.lower()
        for row in tree_feedback.get_children():
            tree_feedback.delete(row)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT f.feedback_id, f.client_id, c.first_name, c.last_name, f.rating, f.comm
            FROM feedback f
            JOIN client c ON f.client_id = c.client_id
        """)
        for row in cur.fetchall():
            if any(keyword in str(cell).lower() for cell in row):
                tree_feedback.insert("", "end", values=row)
        cur.close()
        conn.close()

    refresh_feedback_data()

    def edit_feedback():
        selected = tree_feedback.selection()
        if not selected:
            return
        values = tree_feedback.item(selected[0])['values']
        column = simpledialog.askstring("Столбец", "Что редактировать? (rating, comm)")
        if column not in ("rating", "comm"):
            messagebox.showerror("Ошибка", "Можно редактировать только rating или comm")
            return
        new_value = simpledialog.askstring("Новое значение", "Введите новое значение:")
        update_record("feedback", "feedback_id", values[0], column, new_value)
        refresh_feedback_data()

    def delete_feedback():
        selected = tree_feedback.selection()
        if not selected:
            return
        values = tree_feedback.item(selected[0])['values']
        delete_record("feedback", "feedback_id", values[0])
        refresh_feedback_data()

    tk.Button(frame_feedback, text="Редактировать", command=edit_feedback).pack()
    tk.Button(frame_feedback, text="Удалить", command=delete_feedback).pack()

# Основной интерфейс
root = tk.Tk()
root.title("Курьерская доставка")

tk.Label(root, text="Имя").grid(row=0, column=0)
entry_first = tk.Entry(root)
entry_first.grid(row=0, column=1)

tk.Label(root, text="Фамилия").grid(row=1, column=0)
entry_last = tk.Entry(root)
entry_last.grid(row=1, column=1)

tk.Label(root, text="Телефон").grid(row=2, column=0)
entry_phone = tk.Entry(root)
entry_phone.grid(row=2, column=1)

tk.Label(root, text="Адрес").grid(row=3, column=0)
entry_address = tk.Entry(root)
entry_address.grid(row=3, column=1)

tk.Button(root, text="Сделать заказ", command=submit_order).grid(row=4, column=0, columnspan=2, pady=10)

tk.Label(root, text="ID клиента (для отзыва)").grid(row=5, column=0)
entry_client_id = tk.Entry(root)
entry_client_id.grid(row=5, column=1)

tk.Label(root, text="Оценка (1-5)").grid(row=6, column=0)
entry_rating = tk.Entry(root)
entry_rating.grid(row=6, column=1)

tk.Label(root, text="Комментарий").grid(row=7, column=0)
entry_comment = tk.Entry(root)
entry_comment.grid(row=7, column=1)

tk.Button(root, text="Оставить отзыв", command=submit_feedback).grid(row=8, column=0, columnspan=2, pady=10)

tk.Button(root, text="Админ-панель", command=open_admin).grid(row=9, column=0, columnspan=2, pady=10)

root.mainloop()
