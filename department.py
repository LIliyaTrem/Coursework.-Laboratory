import streamlit as st
from datetime import datetime
import database as db
import pandas as pd

# функция для проверки id отделения
def verify_department_id(department_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM department_record;
            """
        )
    for id in c.fetchall():
        if id[0] == department_id:
            verify = True
            break
    conn.close()
    return verify

# функция для отображения сведений об отделения, указанных в списке
def show_department_details(list_of_departments):
    department_titles = ['ID отделения', 'Название отделения', 'Описание', 'Контактный номер',
                      'Дополнительный номер', 'Адрес', 'электронная почта']
    if len(list_of_departments) == 0:
        st.warning('Нет данных')
    elif len(list_of_departments) == 1:
        department_details = [x for x in list_of_departments[0]]
        series = pd.Series(data = department_details, index = department_titles)
        st.write(series)
    else:
        department_details = []
        for department in list_of_departments:
            department_details.append([x for x in department])
        df = pd.DataFrame(data = department_details, columns = department_titles)
        st.write(df)

# функция для создания уникального id отделения с использованием текущей даты и времени
def generate_department_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'D-{id_1}-{id_2}'
    return id

# функция для отображения id и имени врача, указанных в списке
def show_list_of_doctors(list_of_doctors):
    doctor_titles = ['ID врача', 'Имя']
    if len(list_of_doctors) == 0:
        st.warning('Нет данных')
    else:
        doctor_details = []
        for doctor in list_of_doctors:
            doctor_details.append([x for x in doctor])
        df = pd.DataFrame(data = doctor_details, columns = doctor_titles)
        st.write(df)

# функция для получения названия отделения из базы данных для заданного id отдела
def get_department_name(dept_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM department_record
            WHERE id = :id;
            """,
            { 'id': dept_id }
        )
    return c.fetchone()[0]

# класс, содержащий все поля и методы, необходимые для работы с таблицей отделения в базе данных
class Department:

    def __init__(self):
        self.name = str()
        self.id = str()
        self.description = str()
        self.contact_number_1 = str()
        self.contact_number_2 = str()
        self.address = str()
        self.email_id = str()

   # метод для добавления новой записи отделения в базу данных
    def add_department(self):
        st.write('Введите:')
        self.name = st.text_input('Задавние отделения')
        self.description = st.text_area('Отделение')
        self.contact_number_1 = st.text_input('Номер')
        contact_number_2 = st.text_input('Дополнительный номер')
        self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
        self.address = st.text_area('Адресс')
        self.email_id = st.text_input('Email')
        self.id = generate_department_id()
        save = st.button('Сохранить')

        #SQLite для сохранения новой записи отделения в базе данных
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO department_record
                    (
                        id, name, description, contact_number_1, contact_number_2,
                        address, email_id
                    )
                    VALUES (
                        :id, :name, :desc, :phone_1, :phone_2, :address, :email_id
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'desc': self.description,
                        'phone_1': self.contact_number_1,
                        'phone_2': self.contact_number_2, 'address': self.address,
                        'email_id': self.email_id
                    }
                )
            st.success('Отделение добавлено')
            st.write('ID отделения: ', self.id)
            conn.close()

    # метод для обновления существующей записи отделения в базе данных
    def update_department(self):
        id = st.text_input('Ведите ID отделения')
        if id == '':
            st.empty()
        elif not verify_department_id(id):
            st.error('ID не найден')
        else:
            st.success('Верно')
            conn, c = db.connection()

            # показывает текущую информацию об отделе перед обновлением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM department_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Данные отделения:')
                show_department_details(c.fetchall())

            st.write('Введите:')
            self.description = st.text_area('Отделения')
            self.contact_number_1 = st.text_input('Номер')
            contact_number_2 = st.text_input('Дополнительный номер')
            self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
            self.address = st.text_area('Адрес')
            self.email_id = st.text_input('EmailD')
            update = st.button('Обнавить')

            #SQLite для обнавления новой записи отделения в базе данных
            if update:
                with conn:
                    c.execute(
                        """
                        UPDATE department_record
                        SET description = :desc,
                        contact_number_1 = :phone_1, contact_number_2 = :phone_2,
                        address = :address, email_id = :email_id
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'desc': self.description,
                            'phone_1': self.contact_number_1,
                            'phone_2': self.contact_number_2,
                            'address': self.address, 'email_id': self.email_id
                        }
                    )
                st.success('Информация обнавлена')
                conn.close()

    # метод для удаления существующей записи отделения из базы данных
    def delete_department(self):
        id = st.text_input('Введите ID для удаления')
        if id == '':
            st.empty()
        elif not verify_department_id(id):
            st.error('Invalid Department ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # показывает текущую информацию об отделе перед удалением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM department_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Информация об отделении')
                show_department_details(c.fetchall())

                confirm = st.checkbox('Установите флажок, чтобы подтвердить удаление')
                if confirm:
                    delete = st.button('Delete')

                    #SQLite для уделения новой записи отделения в базе данных
                    if delete:
                        c.execute(
                            """
                            DELETE FROM department_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Отделение удалено')
            conn.close()

    # способ показать полную запись отделения
    def show_all_departments(self):
        conn, c = db.connection()
        with conn:
            c.execute(
                """
                SELECT *
                FROM department_record;
                """
            )
            show_department_details(c.fetchall())
        conn.close()

    # метод для поиска и отображения сведений об определенном отделении в базе данных с использованием ID отделения
    def search_department(self):
        id = st.text_input('Введите ID отдела для поиска')
        if id == '':
            st.empty()
        elif not verify_department_id(id):
            st.error('ID неверны')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM department_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Ифнормация об отделении:')
                show_department_details(c.fetchall())
            conn.close()

    # медод чтобы показать список врачей, работающих в определенном отделении
    def list_dept_doctors(self):
        dept_id = st.text_input('Введите ID')
        if dept_id == '':
            st.empty()
        elif not verify_department_id(dept_id):
            st.error('ID неверный')
        else:
            st.success('Верно')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT id, name
                    FROM doctor_record
                    WHERE department_id = :dept_id;
                    """,
                    { 'dept_id': dept_id }
                )
                st.write('Список врачей', get_department_name(dept_id), 'в отделении:')
                show_list_of_doctors(c.fetchall())
            conn.close()
